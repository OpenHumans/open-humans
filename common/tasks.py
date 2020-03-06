from django.core.mail.message import EmailMultiAlternatives
from django.template import engines
from django.template.loader import render_to_string
from django.urls import reverse

from celery import shared_task
from celery.utils.log import get_task_logger

from common.utils import full_url
from private_sharing.models import DataRequestProject, DataRequestProjectMember

logger = get_task_logger(__name__)


@shared_task
def send_emails(project_id, project_members, subject, message, all_members=False):
    """
    Sends emails from project coordinator to project members.
    """
    project = DataRequestProject.objects.get(id=project_id)

    template = engines["django"].from_string(message)
    logger.info("Sending {0} emails".format(len(project_members)))
    if all_members:
        project_members = project.project_members.filter_active().all()
    for project_member in project_members:
        if isinstance(project_member, str):
            # As the instance was passed as json, we need to lookup the db
            # object
            project_member = DataRequestProjectMember.objects.get(
                project_member_id=project_member
            )
        context = {
            "message": template.render(
                {"PROJECT_MEMBER_ID": project_member.project_member_id}
            ),
            "project": project.name,
            "username": project_member.member.user.username,
            "activity_management_url": full_url(
                reverse("activity", kwargs={"slug": project.slug})
            ),
            "project_message_form": full_url(
                reverse("activity-messaging", kwargs={"slug": project.slug})
            ),
        }

        plain = render_to_string("email/project-message.txt", context)
        headers = {"Reply-To": project.contact_email}
        email_from = "{} <{}>".format(project.name, "support@openhumans.org")

        mail = EmailMultiAlternatives(
            subject,
            plain,
            email_from,
            [project_member.member.primary_email.email],
            headers=headers,
        )
        mail.send()
