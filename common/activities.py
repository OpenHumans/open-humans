import re

from django.urls import reverse

LABELS = {
    "share-data": {"name": "Share data", "class": "label-success"},
    "academic-non-profit": {"name": "Academic/<br>Non-profit", "class": "label-info"},
    "study": {"name": "Study", "class": "label-primary"},
    "data-source": {"name": "Data source", "class": "label-warning"},
    "inactive": {"name": "Inactive", "class": "label-default"},
    "in-development": {"name": "In development", "class": "label-default"},
}

TWO_HOURS = 2 * 60 * 60
ONE_MINUTE = 60


def fix_linebreaks(string):
    string = re.sub(r"[\r\n]", " ", string)
    string = re.sub(r" +", " ", string)

    return string


def get_labels(*args):
    """
    Convenience method to filter labels.
    """
    return {name: value for name, value in LABELS.items() if name in args}


def activity_from_data_request_project(project, user=None):
    """
    Create an activity definition from the given DataRequestProject.
    """
    labels = []

    data_source = bool(project.returned_data_description)

    # a member can share with a project by sharing their username or their data
    share_data = (
        project.request_username_access
        or project.requested_sources.exists()
        or project.all_sources_access
    )

    if data_source:
        labels.append("data-source")

    if share_data:
        labels.append("share-data")

    activity = {
        "verbose_name": project.name,
        "data_source": data_source,
        "share_data": share_data,
        "labels": get_labels(*labels),
        "leader": project.leader,
        "organization": project.organization,
        "contact_email": project.contact_email,
        "description": fix_linebreaks(project.short_description),
        "long_description": fix_linebreaks(project.long_description),
        "data_description": project.returned_data_description,
        "in_development": False,
        "is_connected": False,
        "active": project.active,
        "approved": project.approved,
        "info_url": project.info_url,
        "connect_verb": "join" if project.type == "on-site" else "connect",
        "add_data_text": (
            "Join {}".format(project.name)
            if project.type == "on-site"
            else "Connect {}".format(project.name)
        ),
        "members": project.authorized_members,
        "project_id": project.id,
        "url_slug": project.slug,
        "has_files": (
            user and project.projectdatafile_set.filter(user__pk=user.pk).count() > 0
        ),
        "type": "project",
        "on_site": project.type == "on-site",
        "badge": {
            "label": project.id_label,
            "name": project.name,
            "url": "direct-sharing/images/badge.png",
            "href": reverse("activity", kwargs={"slug": project.slug}),
        },
        "source_name": project.id_label,
        "project": project,
    }

    if project.type == "on-site":
        activity["join_url"] = reverse(
            "direct-sharing:join-on-site", kwargs={"slug": project.slug}
        )
    else:
        activity["join_url"] = project.oauth2datarequestproject.enrollment_url

    if project.is_academic_or_nonprofit:
        activity["labels"].update(get_labels("academic-non-profit"))

    if project.is_study:
        activity["labels"].update(get_labels("study"))

    if user and not user.is_anonymous:
        activity["is_connected"] = project.is_joined(user)

    try:
        activity["badge"].update({"url": project.badge_image.url})
    except ValueError:
        pass

    classes = list(activity["labels"].keys())
    if activity["is_connected"]:
        classes.append("connected")
    activity["classes"] = " ".join(classes)

    return activity
