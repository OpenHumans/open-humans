import csv
from io import StringIO
import os
import tempfile
import unittest
from unittest.mock import patch

from allauth.account.models import EmailAddress, EmailConfirmation
from altcha import Payload, solve_challenge

from django import forms
from django.conf import settings
from django.contrib import auth
from django.core import mail, management
from django.core.cache import cache
from django.core.files.storage import InMemoryStorage
from django.db import IntegrityError
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from common.altcha import AltchaField, new_challenge
from common.testing import BrowserTestCase, get_or_create_user, SmokeTestCase
from private_sharing.models import (
    ActivityFeed,
    DataRequestProject,
    DataRequestProjectMember,
    OnSiteDataRequestProject,
)

from .models import Member

UserModel = auth.get_user_model()


class SmokeTests(SmokeTestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    def setUp(self):
        super().setUp()
        # The public projects API serializes badge URLs. Smoke tests should
        # exercise that endpoint without requiring an S3 bucket or credentials.
        badge_storage = patch.object(
            DataRequestProject._meta.get_field("badge_image"),
            "storage",
            InMemoryStorage(),
        )
        badge_storage.start()
        self.addCleanup(badge_storage.stop)

    anonymous_urls = ["/account/login/", "/account/password/reset/", "/account/signup/"]

    authenticated_or_anonymous_urls = [
        "/",
        "/about/",
        "/activity/favorite-trance-tracks/",
        "/activity/groovy-music/",
        "/api/public/datafiles/",
        "/api/public/datatypes/",
        "/api/public/members/",
        "/api/public/projects/",
        "/api/public-data/?username=beau",
        "/api/public-data/?created_start=2/14/2016&created_end=2/14/2016",
        "/api/public-data/sources-by-member/",
        "/api/public-data/members-by-source/",
        "/beau/",
        "/community-guidelines/",
        "/contact-us/",
        "/copyright/",
        "/data-use/",
        "/member/beau/",
        "/members/",
        "/members/page/1/",
        "/members/?sort=username",
        "/members/page/1/?sort=username",
        "/public-data/",
        "/public-data-api/",
        "/news/",
        "/create/",
        "/terms/",
        "/gdpr/",
    ]

    redirect_urls = [
        "/account/delete/",
        "/member/beau/email/",
        "/member/me/",
        "/member/me/account-settings/",
        "/member/me/change-email/",
        "/member/me/change-name/",
        "/member/me/connections/",
        # '/member/me/connections/delete/1/',
        "/member/me/edit/",
        "/member/me/joined/",
        "/member/me/data/",
        "/activity/groovy-music/delete-files/",
        "/member/me/send-confirmation-email/",
        "/public-data/activate-1-overview/",
        "/public-data/activate-2-information/",
        # require a POST
        # '/public-data/activate-3-quiz/',
        # '/public-data/activate-4-signature/',
        # 301 redirect
        # '/public-data/toggle-sharing/',
        "/public-data/deactivate/",
    ]

    authenticated_urls = redirect_urls + [
        "/account/password/change/",
        "/account/password/set/",
        (
            "/oauth2/authorize/?origin=external&response_type=code"
            "&scope=go-viral%20read%20write&client_id=example-id-15"
        ),
    ]

    @override_settings(
        AWS_STORAGE_BUCKET_NAME=None,
        AWS_ACCESS_KEY_ID=None,
        AWS_SECRET_ACCESS_KEY=None,
    )
    def test_public_data_without_aws_credentials(self):
        for url in [
            "/api/public/datafiles/",
            "/api/public/members/",
            "/api/public/projects/",
        ]:
            with self.subTest(url=url):
                self.assert_status_code(url, status_code=200)

    def test_custom_404(self):
        self.assert_status_code("/does-not-exist/", status_code=404)

    def test_custom_500(self):
        with self.assertRaises(Exception):
            self.assert_status_code("/raise-exception/", status_code=500)


@override_settings(SSLIFY_DISABLE=True)
class OpenHumansUserTests(TestCase):
    """
    Tests for our custom User class.
    """

    fixtures = ["open_humans/fixtures/test-data.json"]

    def setUp(self):  # noqa
        get_or_create_user("user1")

    def test_lookup_by_username(self):
        user1 = auth.authenticate(username="user1", password="user1")

        self.assertEqual(user1.username, "user1")

    def test_lookup_by_email(self):
        user1 = auth.authenticate(username="user1@test.com", password="user1")

        self.assertEqual(user1.username, "user1")

    def test_redirect_on_login(self):
        """
        Redirect to previous page on login.
        """
        first_redirect = "/"
        first_response = self.client.post(
            reverse("account_login"),
            {"next": first_redirect, "login": "chickens", "password": "asdfqwerty"},
        )
        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(first_response.url, first_redirect)

        second_redirect = "/api/public-data/?source=direct-sharing-1"
        second_response = self.client.post(
            reverse("account_login"),
            {"next": second_redirect, "login": "chickens", "password": "asdfqwerty"},
        )
        self.assertEqual(second_response.status_code, 302)
        self.assertEqual(second_response.url, second_redirect)

    def test_password_reset(self):
        """
        Test that password reset works and that we we redirect to the proper
        place when a password reset is made.
        """

        redirect = "/"
        response_request_reset = self.client.post(
            reverse("account_reset_password"),
            {"next_t": redirect, "email": "froopla@borknorp.com"},
        )
        self.assertEqual(response_request_reset.status_code, 302)
        # We should now have mail in the outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[Open Humans] Password Reset Email")
        reset_url = [
            item
            for item in mail.outbox[0].body.split("\n")
            if "account/password/reset/key" in item
        ][0]
        key = reset_url.split("/")[7]
        # Go ahead and reset the mailbox
        mail.outbox = []
        do_reset_response = self.client.get(reset_url, follow=True)
        self.assertEqual(do_reset_response.status_code, 200)
        self.assertContains(do_reset_response, "Set your new password")

        do_reset_post_response = self.client.post(
            do_reset_response.redirect_chain[-1][0],
            {"password1": "asdfqwerty", "password2": "asdfqwerty"},
        )
        self.assertEqual(do_reset_post_response.status_code, 302)
        self.assertEqual(do_reset_post_response.url, redirect)

    def test_lowercase_unique(self):
        # Create a lowercase user2
        UserModel.objects.create_user("user2", "user2@test.com", "user2")

        # Creating an uppercase USER2 should fail
        self.assertRaises(
            IntegrityError,
            UserModel.objects.create_user,
            "USER2",
            "other+user2@test.com",
            "user2",
        )


@unittest.skip("The way the django-oauth model handles the primary key has changed")
class CommandTests(TestCase):
    """
    Tests for our management commands.
    """

    fixtures = ["open_humans/fixtures/test-data.json"]

    def setUp(self):
        self.output = StringIO()

    def test_bulk_email(self):
        try:
            import sys

            out, sys.stdout = sys.stdout, StringIO()
            management.call_command("bulk_email", "-h", stdout=self.output)
            sys.stdout = out
        except SystemExit as e:
            if e.code != 0:
                raise e

    def test_setup_api(self):
        management.call_command("setup_api", stdout=self.output)

    def test_update_badges(self):
        management.call_command("update_badges", stdout=self.output)

    def test_user_connections_json(self):
        management.call_command(
            "user_connections_json", "/dev/null", stdout=self.output
        )

    def test_stats(self):
        management.call_command("stats", "--days=365", stdout=self.output)


class WsgiTests(TestCase):
    """
    Tests for our WSGI application.
    """

    @staticmethod
    def test_import():
        from .wsgi import application  # noqa, pylint: disable=unused-variable


class WelcomeEmailTests(TestCase):
    """
    Tests for our welcome email.
    """

    @patch("open_humans.signals.send_mail")
    def test_send_welcome_email(self, mock):
        user = get_or_create_user("email_test_user")

        member = Member(user=user)
        member.save()

        email = user.emailaddress_set.all()[0]
        email.verified = False
        email.save()

        confirmation = EmailConfirmation.create(email)
        confirmation.sent = timezone.now()
        confirmation.save()

        # confirm the email; this sends the email_confirmed signals
        confirmed_email = confirmation.confirm(request=mock)

        self.assertTrue(confirmed_email is not None)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(mock.call_args[0][-1][0], "email_test_user@test.com")


class OpenHumansBrowserTests(BrowserTestCase):
    """
    Browser tests of general Open Humans functionality.
    """

    @unittest.skipIf(settings.NOBROWSER, "skipping browser tests")
    def test_create_user(self):
        driver = self.driver

        driver.get(self.live_server_url)

        driver.find_element_by_class_name("signup-link").click()

        username = self.wait_for_element_id("signup-username")

        username.clear()
        username.send_keys("test_123")

        name = driver.find_element_by_id("signup-name")

        name.clear()
        name.send_keys("Test Testerson")

        email = driver.find_element_by_id("email-address")

        email.clear()
        email.send_keys("test@example.com")

        password = driver.find_element_by_id("signup-password")

        password.clear()
        password.send_keys("testing123")

        password_confirm = driver.find_element_by_id("signup-password-confirm")

        password_confirm.clear()
        password_confirm.send_keys("testing123")

        driver.find_element_by_name("terms").click()

        driver.find_element_by_id("create-account").click()

        self.assertEqual(
            "Please verify your email address.",
            driver.find_element_by_css_selector(
                ".call-to-action-3 > .container > h3"
            ).text,
        )

    @unittest.skipIf(settings.NOBROWSER, "skipping browser tests")
    def test_remove_connection(self):
        driver = self.driver

        self.login()

        driver.get(self.live_server_url + "/member/me/connections/")

        driver.find_element_by_xpath(
            "(//a[contains(text(),'Remove connection')])[1]"
        ).click()
        driver.find_element_by_name("remove_datafiles").click()
        driver.find_element_by_css_selector("label").click()
        driver.find_element_by_css_selector("input.btn.btn-danger").click()


@override_settings(SSLIFY_DISABLE=True)
class HidePublicMembershipTestCase(APITestCase):
    """
    Tests whether or not membership in public data activities is properly
    hidden when requested.
    """

    fixtures = ["open_humans/fixtures/test-data.json"]

    def test_public_api(self):
        """
        Tests the public API endpoints.
        """
        user = UserModel.objects.get(username="bacon")
        project = DataRequestProject.objects.get(id=1)
        project_member = project.active_user(user)

        project_member.set_visibility(visible_status=False)
        results = self.client.get("/api/public-data/members-by-source/").data["results"]
        result = {}
        for item in results:
            if item["source"] == "direct-sharing-1":
                result = item
        assert result["usernames"] == []

        project_member.set_visibility(visible_status=True)
        results = self.client.get("/api/public-data/members-by-source/").data["results"]
        result = {}
        for item in results:
            if item["source"] == "direct-sharing-1":
                result = item
        assert result["usernames"] == ["bacon"]


def solved_altcha_payload():
    """
    Do the proof of work for a fresh challenge, as the browser widget would.
    """
    challenge = new_challenge()

    return Payload(challenge, solve_challenge(challenge)).to_base64()


class CaptchaForm(forms.Form):
    captcha = AltchaField()


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class AltchaTests(TestCase):
    """
    Tests for the proof-of-work CAPTCHA field and its challenge endpoint.
    """

    def setUp(self):
        cache.clear()

    def test_challenge_endpoint(self):
        response = self.client.get(reverse("altcha-challenge"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("signature", response.json())
        self.assertEqual(response.json()["parameters"]["algorithm"], "PBKDF2/SHA-256")

    def test_solved_challenge_is_accepted(self):
        form = CaptchaForm({"captcha": solved_altcha_payload()})

        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_solution_is_rejected(self):
        self.assertFalse(CaptchaForm({}).is_valid())

    def test_garbage_solution_is_rejected(self):
        self.assertFalse(CaptchaForm({"captcha": "not-a-solution"}).is_valid())

    def test_solution_signed_with_another_key_is_rejected(self):
        payload = solved_altcha_payload()

        with override_settings(SECRET_KEY="a-different-key"):
            self.assertFalse(CaptchaForm({"captcha": payload}).is_valid())

    def test_solution_cannot_be_reused(self):
        payload = solved_altcha_payload()

        self.assertTrue(CaptchaForm({"captcha": payload}).is_valid())
        self.assertFalse(CaptchaForm({"captcha": payload}).is_valid())

    def test_signup_requires_captcha(self):
        data = {
            "username": "new_member",
            "name": "New Member",
            "email": "new_member@test.com",
            "password1": "asdfqwerty",
            "terms": "on",
        }

        response = self.client.post(reverse("email_signup"), data)

        self.assertFalse(UserModel.objects.filter(username="new_member").exists())
        self.assertContains(response, "<altcha-widget")

        data["captcha"] = solved_altcha_payload()
        response = self.client.post(reverse("email_signup"), data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Member.objects.filter(user__username="new_member").exists())


class HomePageTests(TestCase):
    """
    Tests for what the homepage shows.
    """

    fixtures = ["open_humans/fixtures/test-data.json"]

    def test_no_activity_feed(self):
        response = self.client.get("/")

        self.assertNotContains(response, "Recent activity")
        self.assertNotContains(response, "New member!")

    def test_signup_records_no_activity_event(self):
        user = get_or_create_user("quiet_user")
        Member.objects.create(user=user, name="Quiet User")

        self.assertFalse(ActivityFeed.objects.filter(member__user=user).exists())


class MemberDirectoryTests(TestCase):
    """
    Tests for which members the public directory lists and what a profile
    shows.
    """

    fixtures = ["open_humans/fixtures/test-data.json"]

    def test_lists_only_members_of_approved_projects(self):
        user = get_or_create_user("no_projects")
        Member.objects.create(user=user, name="No Projects Yet")

        response = self.client.get("/members/")

        # "bacon" has a visible membership in an approved project
        self.assertContains(response, 'href="/member/bacon"')
        self.assertNotContains(response, 'href="/member/no_projects"')
        self.assertNotContains(response, 'href="/member/chickens"')

    def test_membership_in_unapproved_project_is_not_enough(self):
        DataRequestProject.objects.filter(pk=2).update(approved=False)

        response = self.client.get("/members/")

        self.assertNotContains(response, 'href="/member/bacon"')

    def test_unlisted_profile_loads_by_direct_link(self):
        self.assertEqual(self.client.get("/member/chickens/").status_code, 200)

    def test_profile_has_no_bio(self):
        response = self.client.get("/member/beau/")

        self.assertNotContains(response, "About me")
        self.assertNotContains(response, "Testing!")

    def test_profile_edit_form_has_no_bio_field(self):
        self.assertTrue(self.client.login(username="beau", password="asdfqwerty"))

        response = self.client.get(reverse("my-member-profile-edit"))

        self.assertNotContains(response, 'name="about_me"')


class SpamReportTests(TestCase):
    """
    Tests for the spam_report management command.
    """

    fixtures = ["open_humans/fixtures/test-data.json"]

    @staticmethod
    def member(username, name="Sam Rivera"):
        user = get_or_create_user(username)

        return Member.objects.create(user=user, name=name)

    def report(self):
        with tempfile.TemporaryDirectory() as output_dir:
            management.call_command(
                "spam_report", output_dir=output_dir, stdout=StringIO()
            )

            with open(os.path.join(output_dir, "accounts.csv")) as f:
                accounts = {row["username"]: row for row in csv.DictReader(f)}

            with open(os.path.join(output_dir, "projects.csv")) as f:
                projects = {row["name"]: row for row in csv.DictReader(f)}

        return accounts, projects

    def test_flags_idle_account_with_link_in_name(self):
        self.member("linker", name="https://deals.example")

        accounts, _ = self.report()

        self.assertEqual(accounts["linker"]["name_has_link"], "True")

    def test_flags_idle_account_with_banned_word_in_name(self):
        self.member("wordy", name="Dental Marketing Experts")

        accounts, _ = self.report()

        self.assertIn("dental", accounts["wordy"]["name_banned_words"].split())

    def test_skips_account_with_an_approved_project_membership(self):
        member = self.member("joined", name="Dental Marketing Experts")
        DataRequestProjectMember.objects.create(
            member=member,
            project=DataRequestProject.objects.get(pk=1),
            joined=True,
            authorized=True,
        )

        accounts, _ = self.report()

        self.assertNotIn("joined", accounts)

    def test_skips_idle_account_with_clean_name(self):
        self.member("quiet")

        accounts, _ = self.report()

        self.assertNotIn("quiet", accounts)

    def test_skips_deactivated_account(self):
        member = self.member("gone", name="https://deals.example")
        member.user.is_active = False
        member.user.save()

        accounts, _ = self.report()

        self.assertNotIn("gone", accounts)

    def test_lists_unapproved_projects_and_flags_their_coordinators(self):
        coordinator = self.member("promoter")
        OnSiteDataRequestProject.objects.create(
            name="Best Deals",
            coordinator=coordinator,
            is_study=False,
            is_academic_or_nonprofit=False,
            leader="Promoter",
            organization="Deals Inc",
            contact_email="promoter@test.com",
            short_description="Buy now at https://deals.example",
            long_description="Deals",
            request_username_access=False,
            approved=False,
        )

        accounts, projects = self.report()

        self.assertEqual(projects["Best Deals"]["looks_like_spam"], "True")
        self.assertEqual(projects["Best Deals"]["has_link"], "True")
        self.assertEqual(accounts["promoter"]["coordinates_spam_project"], "True")

    def test_approved_projects_are_not_listed(self):
        _, projects = self.report()

        self.assertEqual(projects, {})


class CsrfErrorTests(TestCase):
    """
    A signed-in member who resubmits a login form whose CSRF token the login
    already rotated is sent on rather than shown the CSRF error.
    """

    fixtures = ["open_humans/fixtures/test-data.json"]

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def post_stale_login(self, data=None):
        return self.client.post(
            "/account/login/",
            {"csrfmiddlewaretoken": "stale", "login": "beau", **(data or {})},
        )

    def test_signed_in_member_goes_home(self):
        self.client.login(username="beau", password="asdfqwerty")

        response = self.post_stale_login()

        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_signed_in_member_goes_to_next(self):
        self.client.login(username="beau", password="asdfqwerty")

        response = self.post_stale_login({"next": "/members/"})

        self.assertRedirects(response, "/members/", fetch_redirect_response=False)

    def test_offsite_next_goes_home(self):
        self.client.login(username="beau", password="asdfqwerty")

        response = self.post_stale_login({"next": "https://example.com/"})

        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_signed_out_visitor_sees_error(self):
        response = self.post_stale_login()

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "CSRF error", status_code=403)

    def test_signed_in_member_sees_error_on_other_forms(self):
        self.client.login(username="beau", password="asdfqwerty")

        response = self.client.post("/account/logout/", {})

        self.assertEqual(response.status_code, 403)
