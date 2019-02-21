from django.conf import settings
from django.contrib import messages as django_messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import SafeString
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin

from common.mixins import LargePanelMixin, PrivateMixin
from common.views import BaseOAuth2AuthorizationView
from data_import.models import DataTypes

# TODO: move this to common
from open_humans.mixins import SourcesContextMixin

from .forms import (
    AddDataTypeForm,
    MessageProjectMembersForm,
    OAuth2DataRequestProjectForm,
    OnSiteDataRequestProjectForm,
    RemoveProjectMembersForm,
    SelectDatatypesForm,
)
from .models import (
    ActivityFeed,
    DataRequestProject,
    DataRequestProjectMember,
    OAuth2DataRequestProject,
    OnSiteDataRequestProject,
    id_label_to_project,
)


MAX_UNAPPROVED_MEMBERS = settings.MAX_UNAPPROVED_MEMBERS


class CoordinatorOrActiveMixin(object):
    """
    - Always let the coordinator view this page
    - Only let members view it if the project is active
    - Only let members view it if the project is not approved and less than
      MAX_UNAPPROVED_MEMBERS have joined.
    """

    def dispatch(self, *args, **kwargs):
        project = self.get_object()

        if project.coordinator == self.request.user:
            return super(CoordinatorOrActiveMixin, self).dispatch(*args, **kwargs)

        if not project.active:
            raise Http404

        if not project.approved and project.authorized_members > MAX_UNAPPROVED_MEMBERS:
            django_messages.error(
                self.request,
                (
                    """Sorry, "{}" has not been approved and has exceeded the {}
                member limit for unapproved projects.""".format(
                        project.name, MAX_UNAPPROVED_MEMBERS
                    )
                ),
            )

            return HttpResponseRedirect(reverse("my-member-data"))

        return super(CoordinatorOrActiveMixin, self).dispatch(*args, **kwargs)


class ProjectMemberMixin(object):
    """
    Add project_member and related helper methods.
    """

    @property
    def project_member(self):
        project = self.get_object()

        project_member, _ = DataRequestProjectMember.objects.get_or_create(
            member=self.request.user.member, project=project
        )

        return project_member

    @property
    def project_joined_by_member(self):
        return self.project_member and self.project_member.joined

    @property
    def project_authorized_by_member(self):
        return self.project_member and self.project_member.authorized

    def authorize_member(self, hidden):
        project = self.get_object()

        self.request.user.log(
            "direct-sharing:{0}:authorize".format(project.type),
            {"project-id": project.id},
        )

        django_messages.success(
            self.request,
            ('You have successfully joined the project "{}".'.format(project.name)),
        )
        if (
            project.approved
            and not ActivityFeed.objects.filter(
                member=self.project_member.member,
                project=project,
                action="joined-project",
            ).exists()
        ):
            event = ActivityFeed(
                member=self.project_member.member,
                project=project,
                action="joined-project",
            )
            event.save()

        project_member = self.project_member

        # The OAuth2 projects have join and authorize in the same step
        if project.type == "oauth2":
            project_member.joined = True

        project_member.authorized = True
        project_member.revoked = False
        project_member.username_shared = project.request_username_access
        project_member.all_sources_shared = project.all_sources_access
        project_member.visible = not hidden  # visible is the opposite of hidden
        project_member.erasure_requested = None
        project_member.save()
        # if this is a new DataRequestProjectMember object, the docs state that
        # manytomany fields should be saved separately from initial creation
        project_member.granted_sources.set(project.requested_sources.all())
        project_member.save()


class OnSiteDetailView(ProjectMemberMixin, CoordinatorOrActiveMixin, DetailView):
    """
    A base DetailView for on-site projects.
    """

    model = OnSiteDataRequestProject


class JoinOnSiteDataRequestProjectView(PrivateMixin, LargePanelMixin, OnSiteDetailView):
    """
    Display the consent form for a project.
    """

    template_name = "private_sharing/join-on-site.html"

    def get_login_message(self):
        project = self.get_object()
        return 'Please log in to join "{0}"'.format(project.name)

    def get(self, request, *args, **kwargs):
        """
        If the member has already accepted the consent form redirect them to
        the authorize page.
        """
        if self.project_joined_by_member:
            return HttpResponseRedirect(
                reverse_lazy(
                    "direct-sharing:authorize-on-site",
                    kwargs={"slug": self.get_object().slug},
                )
            )

        return super().get(request, *args, **kwargs)

    # pylint: disable=unused-argument
    def post(self, request, *args, **kwargs):
        project = self.get_object()
        project_member = self.project_member

        project_member.joined = True

        # store the consent text that the user has consented to
        project_member.consent_text = project.consent_text

        # if the user joins again after revoking the study then reset their
        # revoked and authorized status
        project_member.revoked = False
        project_member.authorized = False

        project_member.save()

        request.user.log("direct-sharing:on-site:consent", {"project-id": project.id})

        return HttpResponseRedirect(
            reverse_lazy(
                "direct-sharing:authorize-on-site", kwargs={"slug": project.slug}
            )
        )


class ConnectedSourcesMixin(object):
    """
    Add context for connected/unconnected sources.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_object()
        requested_sources = project.requested_sources.all()
        context.update(
            {
                "project_authorized_by_member": self.project_authorized_by_member,
                "sources": requested_sources,
            }
        )

        return context


class AuthorizeOnSiteDataRequestProjectView(
    PrivateMixin, LargePanelMixin, ConnectedSourcesMixin, OnSiteDetailView
):
    """
    Display the requested permissions for a project.
    """

    template_name = "private_sharing/authorize-on-site.html"

    def get_login_message(self):
        project = self.get_object()
        return 'Please log in to authorize "{0}"'.format(project.name)

    def get(self, request, *args, **kwargs):
        """
        If the member hasn't already accepted the consent form redirect them to
        the consent form page.
        """
        # the opposite of the test in the join page
        if not self.project_joined_by_member:
            return HttpResponseRedirect(
                reverse_lazy(
                    "direct-sharing:join-on-site",
                    kwargs={"slug": self.get_object().slug},
                )
            )

        return super().get(request, *args, **kwargs)

    # pylint: disable=unused-argument
    def post(self, request, *args, **kwargs):
        # repeating this because making a function for these two lines
        # would add more complexity than it would save.
        if not self.project_joined_by_member:
            return HttpResponseRedirect(
                reverse_lazy(
                    "direct-sharing:join-on-site",
                    kwargs={"slug": self.get_object().slug},
                )
            )

        if self.request.POST.get("cancel") == "cancel":
            self.project_member.delete()

            return HttpResponseRedirect(reverse("home"))

        if self.request.POST.get("hide-membership") == "hidden_membership":
            hidden = True
        else:
            hidden = False
        self.authorize_member(hidden)

        project = self.get_object()

        if project.post_sharing_url:
            redirect_url = project.post_sharing_url.replace(
                "PROJECT_MEMBER_ID", self.project_member.project_member_id
            )
        else:
            redirect_url = reverse(
                "activity-management", kwargs={"source": project.slug}
            )

        return HttpResponseRedirect(redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {"project": self.get_object(), "username": self.request.user.username}
        )

        return context


class AuthorizeOAuth2ProjectView(
    ConnectedSourcesMixin, ProjectMemberMixin, BaseOAuth2AuthorizationView
):
    """
    Override oauth2_provider view to add origin, context, and customize login
    prompt.
    """

    template_name = "private_sharing/authorize-oauth2.html"

    def dispatch(self, *args, **kwargs):
        try:
            if not self.application.oauth2datarequestproject:
                raise Http404
        except ObjectDoesNotExist:
            raise Http404
        if not self.application.oauth2datarequestproject.active:
            return HttpResponseRedirect(reverse("direct-sharing:authorize-inactive"))
        return super().dispatch(*args, **kwargs)

    def get_object(self):
        return self.application.oauth2datarequestproject

    def post(self, request, *args, **kwargs):
        """
        Get whether or not the member has requested hidden membership.
        """
        self.hidden = request.POST.get("hide-membership", None)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Override the OAuth2 AuthorizationView's form_valid to authorize a
        project member if the user authorizes the OAuth2 request.
        """
        allow = form.cleaned_data.get("allow")

        if allow:
            if self.hidden == "hidden_membership":
                hidden = True
            else:
                hidden = False
            self.authorize_member(hidden)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "object": self.get_object(),
                "project": self.get_object(),
                # XXX: BaseOAuth2AuthorizationView doesn't provide the request
                # context for some reason
                "request": self.request,
                "username": self.request.user.username,
            }
        )

        return context


class CoordinatorOnlyView(View):
    """
    Only let coordinators and superusers view these pages.
    """

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()

        if self.object.coordinator.user != self.request.user:
            if not self.request.user.is_superuser:
                raise Http404

        return super().dispatch(*args, **kwargs)


class SaveDataRequestProjectView(FormView):
    """
    Base View for saving DataRequestProjects
    """

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        if form.is_valid():
            if hasattr(self, "object"):
                # This is an update
                project = self.object
                project.requested_sources.clear()
            else:
                project = OnSiteDataRequestProject()
            for key, value in form.cleaned_data.items():
                if key != "request_sources_access":
                    setattr(project, key, value)
            project.coordinator = self.request.user.member
            project.save()
            requested_sources = form.cleaned_data.get("request_sources_access", [])
            for source in requested_sources:
                project.requested_sources.add(id_label_to_project(source))
            project.save()
            self.object = project

        return super().form_valid(form)


class UpdateDataRequestProjectView(
    PrivateMixin,
    LargePanelMixin,
    CoordinatorOnlyView,
    SingleObjectMixin,
    SaveDataRequestProjectView,
):
    """
    Base view for creating an data request activities.
    """

    success_url = reverse_lazy("direct-sharing:manage-projects")

    def get_login_message(self):
        project = self.get_object()
        return 'Please log in to authorize "{0}"'.format(project.name)

    def get_initial(self):
        """
        Populate the form with common DataRequestProject bits
        """
        initial = super().get_initial()
        initial["name"] = self.object.name
        initial["is_study"] = self.object.is_study
        initial["leader"] = self.object.leader
        initial["organization"] = self.object.organization
        initial["is_academic_or_nonprofit"] = self.object.is_academic_or_nonprofit
        initial["add_data"] = self.object.add_data
        initial["explore_share"] = self.object.explore_share
        initial["contact_email"] = self.object.contact_email
        initial["info_url"] = self.object.info_url
        initial["short_description"] = self.object.short_description
        initial["long_description"] = self.object.long_description
        initial["returned_data_description"] = self.object.returned_data_description
        initial["active"] = self.object.active
        initial["badge_image"] = self.object.badge_image
        initial["request_username_access"] = self.object.request_username_access
        initial["erasure_supported"] = self.object.erasure_supported
        initial["deauth_email_notification"] = self.object.deauth_email_notification
        requested_sources = self.object.requested_sources.all()
        initial["request_sources_access"] = [rs.id_label for rs in requested_sources]

        return initial


class CreateDataRequestProjectView(
    PrivateMixin, LargePanelMixin, SaveDataRequestProjectView
):
    """
    Base view for creating an data request activities.
    """

    login_message = "Please log in to create a project."

    def get_success_url(self):
        project_slug = self.object.slug
        if project_slug:
            return reverse_lazy("direct-sharing:select-datatypes", args=[project_slug])
        reverse_lazy("direct-sharing:manage-projects")


class CreateOAuth2DataRequestProjectView(CreateDataRequestProjectView):
    """
    Create an OAuth2DataRequestProject.
    """

    template_name = "private_sharing/create-project.html"
    model = OAuth2DataRequestProject
    form_class = OAuth2DataRequestProjectForm


class CreateOnSiteDataRequestProjectView(CreateDataRequestProjectView):
    """
    Create an OnSiteDataRequestProject.
    """

    template_name = "private_sharing/create-project.html"
    model = OnSiteDataRequestProject
    form_class = OnSiteDataRequestProjectForm


class UpdateOAuth2DataRequestProjectView(UpdateDataRequestProjectView):
    """
    Update an OAuth2DataRequestProject.
    """

    template_name = "private_sharing/update-project.html"
    model = OAuth2DataRequestProject
    form_class = OAuth2DataRequestProjectForm

    def get_initial(self):
        """
        Populate the form with common DataRequestProject bits
        """
        initial = super().get_initial()
        initial["enrollment_url"] = self.object.enrollment_url
        initial["redirect_url"] = self.object.redirect_url
        initial["deauth_webhook"] = self.object.deauth_webhook
        return initial


class UpdateOnSiteDataRequestProjectView(UpdateDataRequestProjectView):
    """
    Update an OnSiteDataRequestProject.
    """

    template_name = "private_sharing/update-project.html"
    model = OnSiteDataRequestProject
    form_class = OnSiteDataRequestProjectForm

    def get_initial(self):
        """
        Populate the form with common DataRequestProject bits
        """
        initial = super().get_initial()
        initial["consent_text"] = self.object.consent_text
        initial["post_sharing_url"] = self.object.post_sharing_url
        return initial


class RefreshTokenMixin(object):
    """
    A mixin that adds a POST handler for refreshing a project's token.
    """

    # pylint: disable=unused-argument
    def post(self, request, *args, **kwargs):
        if self.request.POST.get("refresh_token") == "refresh_token":
            self.object.refresh_token()

        return self.get(request, *args, **kwargs)


class OAuth2DataRequestProjectDetailView(
    PrivateMixin, CoordinatorOnlyView, RefreshTokenMixin, DetailView
):
    """
    Display an OAuth2DataRequestProject.
    """

    template_name = "private_sharing/project-detail.html"
    model = OAuth2DataRequestProject

    def get_login_message(self):
        project = self.get_object()
        msg = 'Please log in to view project information for "{0}".'.format(
            project.name
        )
        return msg


class OnSiteDataRequestProjectDetailView(
    PrivateMixin, CoordinatorOnlyView, RefreshTokenMixin, DetailView
):
    """
    Display an OnSiteDataRequestProject.
    """

    template_name = "private_sharing/project-detail.html"
    model = OnSiteDataRequestProject

    def get_login_message(self):
        project = self.get_object()
        msg = 'Please log in to view project information for "{0}".'.format(
            project.name
        )
        return msg


class ManageDataRequestActivitiesView(PrivateMixin, TemplateView):
    """
    A view for listing all data request activities for the current user.
    """

    login_message = "Please log in to manage your projects."
    template_name = "private_sharing/manage.html"

    def get_context_data(self, **kwargs):
        context = super(ManageDataRequestActivitiesView, self).get_context_data(
            **kwargs
        )

        query = {"coordinator__user": self.request.user}

        oauth2 = OAuth2DataRequestProject.objects.filter(**query)
        onsite = OnSiteDataRequestProject.objects.filter(**query)

        context.update({"onsite": onsite, "oauth2": oauth2})

        return context


class InDevelopmentView(TemplateView):
    """
    Add in-development projects to template context.
    """

    template_name = "private_sharing/in-development.html"

    def get_context_data(self, **kwargs):
        context = super(InDevelopmentView, self).get_context_data(**kwargs)

        context.update(
            {"projects": DataRequestProject.objects.filter(approved=False, active=True)}
        )

        return context


class OverviewView(SourcesContextMixin, TemplateView):
    """
    Add current sources to template context.
    """

    template_name = "direct-sharing/overview.html"


class ProjectLeaveView(PrivateMixin, DetailView):
    """
    Let a member remove themselves from a project.
    """

    template_name = "private_sharing/leave-project.html"
    model = DataRequestProjectMember

    # pylint: disable=unused-argument
    def post(self, *args, **kwargs):
        project_member = self.get_object()
        remove_datafiles = self.request.POST.get("remove_datafiles", "off") == "on"
        erasure_requested = self.request.POST.get("erasure_requested", "off") == "on"
        done_by = "self"

        project_member.leave_project(
            remove_datafiles=remove_datafiles,
            done_by=done_by,
            erasure_requested=erasure_requested,
        )

        if "next" in self.request.GET:
            return HttpResponseRedirect(self.request.GET["next"])
        else:
            return HttpResponseRedirect(reverse("my-member-connections"))


class BaseProjectMembersView(PrivateMixin, CoordinatorOnlyView, DetailView, FormView):
    """
    Base class for views for coordinators to take bulk action on proj members.
    """

    model = DataRequestProject

    def get_login_message(self):
        project = self.get_object()
        return 'Please log in to work on "{0}".'.format(project.name)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(BaseProjectMembersView, self).get_form_kwargs(*args, **kwargs)
        kwargs["project"] = self.get_object()
        return kwargs

    def get_success_url(self):
        project = self.get_object()

        return reverse_lazy(
            "direct-sharing:detail-{}".format(project.type),
            kwargs={"slug": project.slug},
        )


class MessageProjectMembersView(BaseProjectMembersView):
    """
    A view for coordinators to message their project members.
    """

    form_class = MessageProjectMembersForm
    template_name = "private_sharing/message-project-members.html"

    def form_valid(self, form):
        form.send_messages(self.get_object())

        django_messages.success(self.request, "Your message was sent successfully.")

        return super(MessageProjectMembersView, self).form_valid(form)


class RemoveProjectMembersView(BaseProjectMembersView):
    """
    A view for coordinators to remove project members.
    """

    form_class = RemoveProjectMembersForm
    template_name = "private_sharing/remove-project-members.html"

    def form_valid(self, form):
        form.remove_members(self.get_object())

        django_messages.success(self.request, "Project member(s) removed.")

        return super(RemoveProjectMembersView, self).form_valid(form)


class DataRequestProjectWithdrawnView(PrivateMixin, CoordinatorOnlyView, ListView):
    """
    A view for coordinators to list members that have requested data removal.
    """

    model = DataRequestProject
    paginate_by = 100
    template_name = "private_sharing/project-withdrawn-members-view.html"

    def get_login_message(self):
        project = self.get_object()
        return 'Please log in to work on "{0}".'.format(project.name)

    def withdrawn_members(self):
        """
        Returns a queryset with the members that have requested data erasure.
        """
        return self.object.project_members.get_queryset().filter(revoked=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.object
        context["object_list"] = self.withdrawn_members()
        return context

    def get_object(self, queryset=None):
        """
        Impliment get_object as a convenience funtion.
        """
        slug = self.request.path.split("/")[4]
        if queryset is None:
            queryset = self.get_queryset()

        self.object = queryset.get(slug=slug)
        return self.object


class SelectDatatypesView(
    PrivateMixin, CoordinatorOrActiveMixin, LargePanelMixin, FormView
):
    """
    Select the datatypes for a project.
    """

    form_class = SelectDatatypesForm
    model = DataRequestProject
    success_url = reverse_lazy("direct-sharing:manage-projects")
    template_name = "private_sharing/select-datatypes.html"

    def get_object(self):
        """
        Impliment get_object as a convenience funtion.
        """
        slug = self.request.path.split("/")[4]
        queryset = self.model.objects.all()

        self.object = queryset.get(slug=slug)
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = []
        html_tab = SafeString("&emsp;&emsp;")

        # Pre-populate form based on whether we saved the form in the session to add
        # datatypes or, failing that, if there are datatypes already associated with
        # the project
        populate = self.request.session.pop("select_category_form", None)
        if not populate:
            populate = {}
            populate_names = self.object.datatypes.all().values_list('name', flat=True)
            for name in populate_names:
                populate[name.replace(" ", "_")] = ["on"]

        for entry in DataTypes.objects.all().order_by('name'):
            parents = entry.get_all_parents
            if not entry.parent:
                tab = ""  # We are not going to tab over the first level of the ontology
            else:
                tab = html_tab * len(parents)
            html_name = entry.name.replace(" ", "_")
            if populate:
                initial = populate.pop(html_name, False)
            else:
                initial = False
            if initial == ["on"]:
                initial = True
            new_field = {
                "label": entry.name,
                "id": "id_{0}".format(html_name),
                "initial": initial,
                "name": html_name,
                "tab": tab,
            }
            if entry.parent:
                for field in fields:
                    if entry.parent.name == field["label"]:
                        loc = fields.index(field)
                        fields.insert(loc + 1, new_field)
                        break
            if new_field not in fields:
                fields.append(new_field)

        context.update({"fields_tree": fields, "project": self.object})
        return context

    def form_valid(self, form):
        """
        Form is good, let's save this thing.
        """
        ret = super().form_valid(form)
        if "add-datatype" in form.cleaned_data:
            # User wants to add a new datatype.  Save the current state of the
            # selection form.
            form.cleaned_data.pop("add-datatype")
            self.request.session["select_category_form"] = form.cleaned_data
            self.request.session["project"] = self.object.slug
            return HttpResponseRedirect(reverse("direct-sharing:add-datatype"))

        # Remove existing datatypes and save new
        self.object.datatypes.clear()
        for field, value in form.cleaned_data.items():
            # values are encapsulated as a list of len 1, 'on' is true
            if value[0] == "on":
                # The datatype is contained in the name of the field
                name = field.replace("_", " ")
                datatype = DataTypes.objects.get(name=name)

                self.object.datatypes.add(datatype)
                self.object.save()

        return ret


class AddDataTypeView(PrivateMixin, CreateView):
    """
    Select the datatypes for a project.
    """

    form_class = AddDataTypeForm
    template_name = "private_sharing/add-datatype.html"

    def get_success_url(self):
        project_slug = self.request.session.pop("project", None)
        if project_slug:
            return reverse_lazy("direct-sharing:select-datatypes", args=[project_slug])
        return reverse_lazy("direct-sharing:manage-projects")
