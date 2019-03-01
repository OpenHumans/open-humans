from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count, F, Q
from django.db.models.expressions import RawSQL
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import DeleteView, FormView

import feedparser

from common.activities import activity_from_data_request_project
from common.mixins import LargePanelMixin, NeverCacheMixin, PrivateMixin
from data_import.models import DataFile, is_public
from public_data.models import PublicDataAccess
from private_sharing.models import (
    ActivityFeed,
    DataRequestProject,
    DataRequestProjectMember,
    FeaturedProject,
    toggle_membership_visibility,
)
from private_sharing.utilities import source_to_url_slug

from .forms import ActivityMessageForm
from .mixins import SourcesContextMixin
from .models import BlogPost, Member, GrantProject

User = get_user_model()
TEN_MINUTES = 60 * 10


def sort_projects_by_membership(projects):
    """
    Takes a queryset of projects and returns a queryset sorted by the number of
    members in a project.
    """
    projects = projects.annotate(
        num_members=Count(
            "project_members",
            filter=(
                Q(project_members__joined=True)
                & Q(project_members__member__user__is_active=True)
            ),
        )
    )
    projects = projects.order_by("-num_members")
    return projects


class SourceDataFilesDeleteView(PrivateMixin, DeleteView):
    """
    Let the user delete all datafiles for a source. Note that DeleteView was
    written with a single object in mind but will happily delete a QuerySet due
    to duck-typing.
    """

    template_name = "member/my-member-source-data-files-delete.html"
    success_url = reverse_lazy("my-member-data")

    def get_object(self, queryset=None):
        source = self.kwargs["source"]
        self.source = source

        return DataFile.objects.filter(user=self.request.user, source=source)

    def get_context_data(self, **kwargs):
        """
        Add the source to the request context.
        """
        context = super(SourceDataFilesDeleteView, self).get_context_data(**kwargs)

        context.update({"source": self.kwargs["source"]})

        return context

    def get_success_url(self):
        """
        Direct to relevant activity page.
        """
        url_slug = source_to_url_slug(self.source)
        return reverse("activity-management", kwargs={"source": url_slug})


class ExceptionView(View):
    """
    Raises an exception for testing purposes.
    """

    @staticmethod
    def get(request):  # pylint: disable=unused-argument
        raise Exception("A test exception.")


class PublicDataDocumentationView(TemplateView):
    """
    Add activities to the context.
    """

    template_name = "pages/public-data-api.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = (
            DataRequestProject.objects.filter(approved=True, no_public_data=False)
            .exclude(returned_data_description="")
            .order_by("name")
        )

        context.update({"projects": projects})

        return context


class HomeView(NeverCacheMixin, SourcesContextMixin, TemplateView):
    """
    View with recent activity feed, blog posts, and highlighted projects.
    """

    template_name = "pages/home.html"

    @staticmethod
    def get_recent_blogposts():
        blogposts_cachetag = "recent-blogposts"
        blogposts = cache.get(blogposts_cachetag)
        if blogposts:
            return blogposts

        blogfeed = feedparser.parse("https://blog.openhumans.org/feed/")
        posts = []
        for item in blogfeed["entries"][0:3]:
            try:
                post = BlogPost.objects.get(rss_id=item["id"])
            except BlogPost.DoesNotExist:
                post = BlogPost.create(rss_feed_entry=item)
            posts.append(post)
        cache.set(blogposts_cachetag, posts, timeout=TEN_MINUTES)
        return posts

    @staticmethod
    def get_recent_activity():
        """
        Lists the 12 most recent actions by users.
        """
        # Here we must use raw sql because the ORM is not quite able to take
        # a queryset, look up two separate foreign keys in two separate models
        # to get an object from a fourth model and return that to filter the
        # first queryset.
        sql = (
            "select id from private_sharing_activityfeed where "
            + "(member_id, project_id) IN (select member_id, project_id "
            + "from private_sharing_datarequestprojectmember "
            + "where visible='true')"
        )
        project_qs = ActivityFeed.objects.filter(id__in=RawSQL(sql, ""))
        non_project_qs = ActivityFeed.objects.filter(project__isnull=True)
        recent_qs = non_project_qs | project_qs
        recent = recent_qs.order_by("-timestamp")[0:12]
        recent_1 = recent[:6]
        recent_2 = recent[6:]
        return (recent_1, recent_2)

    def get_featured_projects(self):
        """
        Get FeaturedProjects in 'activity' data format

        Override description if one is provided.
        """
        featured_qs = FeaturedProject.objects.order_by("id")[0:3]
        featured_projs = featured_qs.prefetch_related("project")
        highlighted = []
        try:
            for featured in featured_projs:
                activity = featured.project
                if featured.description:
                    activity.commentary = featured.description
                else:
                    activity.commentary = featured.project.description
                if not self.request.user.is_anonymous:
                    activity.has_files = (
                        activity.projectdatafile_set.filter(
                            user__pk=self.request.user.pk
                        ).count()
                        > 0
                    )
                highlighted.append(activity)
            return highlighted
        except (ValueError, TypeError):
            return []

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        recent_activity_1, recent_activity_2 = self.get_recent_activity()

        context.update(
            {
                "recent_activityfeed_1": recent_activity_1,
                "recent_activityfeed_2": recent_activity_2,
                "recent_blogposts": self.get_recent_blogposts(),
                "featured_projects": self.get_featured_projects(),
                "no_description": True,
            }
        )

        return context


class AddDataPageView(NeverCacheMixin, SourcesContextMixin, TemplateView):
    """
    View with data source activities. Never cached.
    """

    template_name = "pages/add-data.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # This returns all approved & active projects in the context that have
        # 'add_data' selected
        projects = (
            DataRequestProject.objects.filter(approved=True)
            .filter(active=True)
            .filter(add_data=True)
            .exclude(returned_data_description__isnull=True)
            .exclude(returned_data_description__exact="")
        )
        if not self.request.user.is_anonymous:
            project_memberships = DataRequestProjectMember.objects.filter(
                member=self.request.user.member,
                joined=True,
                authorized=True,
                revoked=False,
            ).select_related("project")
            projects = projects.exclude(project_members__in=project_memberships)
        sorted_projects = sort_projects_by_membership(projects)
        context.update({"projects": sorted_projects})
        return context


class ExploreSharePageView(AddDataPageView):
    """
    View with data sharing activities. Never cached.
    """

    template_name = "pages/explore-share.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # This returns all approved & active projects in the context that have
        # 'explore_share' selected

        projects = (
            DataRequestProject.objects.filter(approved=True)
            .filter(active=True)
            .filter(explore_share=True)
        )
        if not self.request.user.is_anonymous:
            project_memberships = DataRequestProjectMember.objects.filter(
                member=self.request.user.member,
                joined=True,
                authorized=True,
                revoked=False,
            )
            projects = projects.exclude(project_members__in=project_memberships)
        sorted_projects = sort_projects_by_membership(projects)
        context.update({"projects": sorted_projects})
        return context


class CreatePageView(TemplateView):
    """
    View about creating projects. Has current data sources in context.
    """

    template_name = "pages/create.html"

    def get_context_data(self, **kwargs):
        """
        Update context with same source data used by the activities grid.
        """
        context = super().get_context_data(**kwargs)
        projects = DataRequestProject.objects.filter(
            approved=True, active=True
        ).order_by("id")
        context.update({"projects": projects})
        return context


class ActivityManagementView(NeverCacheMixin, LargePanelMixin, TemplateView):
    """
    A 'home' view for each activity, with sections for describing the activity,
    the user's status for that activity, displaying the user's files for
    management, and providing methods to connect or disconnect the activity.
    """

    source = None
    template_name = "member/activity-management.html"

    def post(self, request, **kwargs):
        """
        Toggle membership visibility back and forth.
        """
        visible = self.request.POST.get("visible", "")
        source = self.request.POST.get("source", "")
        if visible != "":
            toggle_membership_visibility(self.request.user, source, visible)

        return redirect(request.path)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            self.project = DataRequestProject.objects.get(slug=self.kwargs["source"])
        except (KeyError, DataRequestProject.DoesNotExist):
            raise Http404
        self.activity = activity_from_data_request_project(
            self.project, user=self.request.user
        )

        public_users = [
            pda.user
            for pda in PublicDataAccess.objects.filter(
                data_source=self.activity["source_name"]
            )
            .filter(is_public=True)
            .annotate(user=F("participant__member__user"))
        ]
        public_files = (
            DataFile.objects.filter(source=self.activity["source_name"])
            .exclude(parent_project_data_file__completed=False)
            .distinct("user")
            .filter(user__in=public_users)
            .count()
        )

        requesting_activities = self.project.requesting_projects.filter(
            approved=True
        ).filter(active=True)
        requested_activities = self.project.requested_sources.all()
        data_is_public = False

        data_files = []
        if self.request.user.is_authenticated:
            data_files = DataFile.objects.for_user(self.request.user).filter(
                source=self.activity["source_name"]
            )
            data_is_public = is_public(
                self.request.user.member, self.activity["source_name"]
            )

        project = None
        project_member = None
        project_permissions = None
        granted_permissions = None
        permissions_changed = False

        if "project_id" in self.activity:
            project = DataRequestProject.objects.get(pk=self.activity["project_id"])

            project_permissions = {
                "share_username": project.request_username_access,
                "share_sources": requested_activities,
                "all_sources": project.all_sources_access,
                "returned_data_description": project.returned_data_description,
            }
            if self.activity["is_connected"]:
                project_member = project.active_user(self.request.user)
                granted_sources = project_member.granted_sources.all()
                granted_permissions = {
                    "share_username": project_member.username_shared,
                    "share_sources": project_member.granted_sources.all(),
                    "all_sources": project_member.all_sources_shared,
                    "returned_data_description": project.returned_data_description,
                }
                permissions_changed = not all(
                    [
                        granted_permissions[x] == project_permissions[x]
                        for x in ["share_username", "all_sources"]
                    ]
                )
                gs = set(granted_sources.values_list("id", flat=True))
                ra = set(requested_activities.values_list("id", flat=True))
                permissions_changed = permissions_changed or gs.symmetric_difference(ra)
            if project.no_public_data:
                public_files = []

        try:
            show_toggle_visible_button = (
                not project_member.revoked
            ) and project_member.authorized
        except AttributeError:
            show_toggle_visible_button = False

        context.update(
            {
                "activity": self.activity,
                "data_files": data_files,
                "is_public": data_is_public,
                "source": self.activity["source_name"],
                "project": project,
                "project_member": project_member,
                "project_permissions": project_permissions,
                "granted_permissions": granted_permissions,
                "permissions_changed": permissions_changed,
                "public_files": public_files,
                "requesting_activities": requesting_activities,
                "requested_activities": requested_activities,
                "show_toggle_visible_button": show_toggle_visible_button,
            }
        )

        return context


class ActivityMessageFormView(PrivateMixin, LargePanelMixin, FormView):
    """
    A view that lets a member send a message (via email) to a project they
    have joined, via project member ID.
    """

    login_message = "Please log in to message to a project you've joined."
    template_name = "member/activity-message.html"
    form_class = ActivityMessageForm

    def get_activity(self):
        project = DataRequestProject.objects.filter(slug=self.kwargs["source"])
        if project.exists():
            return project.get()
        return None

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect if user is not a project member that can accept messages.
        """
        # Note:  I considered moving this to get instead of dispatch, but
        # I get this feeling that we may want to check on post, as well,
        # so I added the quick check to see if we're logged in. --mdulaney
        if not request.user.is_authenticated:
            request.session["next_url"] = self.request.get_full_path()
            return HttpResponseRedirect(reverse(settings.LOGIN_URL))
        self.project = self.get_activity()
        self.project_member = self.project.active_user(request.user)
        if not self.project_member:
            django_messages.error(
                self.request,
                'Project messaging unavailable for "{}": you must be an '
                "active member of the project.".format(self.project.name),
            )
            return HttpResponseRedirect(self.get_redirect_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.get_redirect_url()

    def get_redirect_url(self):
        return reverse("activity-management", kwargs={"source": self.project.slug})

    def get_context_data(self, **kwargs):
        """
        Add the project and project_member to the request context.
        """
        context = super(ActivityMessageFormView, self).get_context_data(**kwargs)
        context.update({"project": self.project, "project_member": self.project_member})
        return context

    def form_valid(self, form):
        form.send_mail(self.project_member.project_member_id, self.project)

        django_messages.success(
            self.request, ('Your message was sent to "{}".'.format(self.project.name))
        )

        return super().form_valid(form)


class StatisticView(NeverCacheMixin, SourcesContextMixin, TemplateView):
    """
    Show latest statistics on signed up users/projects etc.
    """

    template_name = "pages/statistics.html"

    @staticmethod
    def get_number_member():
        members = Member.objects.filter(user__is_active=True)
        members_with_data = members.annotate(
            datafiles_count=Count("user__datafiles")
        ).filter(datafiles_count__gte=1)
        return (members.count(), members_with_data.count())

    @staticmethod
    def get_number_files():
        files = DataFile.objects.count()
        return files

    @staticmethod
    def get_number_active_approved():
        active_projects = DataRequestProject.objects.filter(approved=True, active=True)
        return active_projects.count()

    @staticmethod
    def get_number_finished_approved():
        finished_projects = DataRequestProject.objects.filter(
            approved=True, active=False
        )
        return finished_projects.count()

    @staticmethod
    def get_number_planned():
        planned_projects = DataRequestProject.objects.filter(
            approved=False, active=True
        )
        return planned_projects.count()

    def get_context_data(self, *args, **kwargs):
        context = super(StatisticView, self).get_context_data(*args, **kwargs)

        (members, members_with_data) = self.get_number_member()

        context.update(
            {
                "number_members": members,
                "number_members_with_data": members_with_data,
                "number_files": self.get_number_files(),
                "active_projects": self.get_number_active_approved(),
                "finished_projects": self.get_number_finished_approved(),
                "planned_projects": self.get_number_planned(),
                "no_description": True,
            }
        )

        return context


class GrantProjectView(NeverCacheMixin, TemplateView):
    """
    Show page of project grants.
    """

    template_name = "pages/grant_projects.html"

    def get_context_data(self, **kwargs):
        context = super(GrantProjectView, self).get_context_data(**kwargs)
        context["grant_projects"] = GrantProject.objects.all().order_by("-grant_date")
        return context


def csrf_error(request, reason):
    """
    A custom view displayed during a CSRF error.
    """
    response = render(request, "CSRF-error.html", context={"reason": reason})
    response.status_code = 403

    return response


def server_error(request):
    """
    A view displayed during a 500 error. Needed because we want to render our
    own 500 page.
    """
    response = render(request, "500.html")
    response.status_code = 500

    return response


class DataProcessingActivities(TemplateView):
    template_name = "pages/data-processing-activities.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["member_count"] = Member.objects.filter(user__is_active=True).count()
        context["project_data_sources"] = DataRequestProject.objects.filter(
            approved=True
        ).exclude(returned_data_description="")
        context["project_data_recipients"] = (
            DataRequestProject.objects.filter(approved=True)
            .annotate(source_count=Count("requested_sources"))
            .filter(source_count__gt=0)
        )
        return context
