from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView

from data_import.utils import file_path_to_type_and_id

from .forms import ConsentForm, WithdrawForm
from .models import Participant, PublicDataStatus


class QuizView(TemplateView):
    """
    Modification of TemplateView that accepts and requires POST.

    This prevents users from jumping to the quiz link without going through
    the informed consent pages.
    """
    template_name = 'public_data/quiz.html'

    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super(QuizView, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class ConsentView(FormView):
    """
    Modification of FormView that walks through the informed consent content.

    Stepping through the form is triggered by POST requests containing new
    values in the 'section' field. If this field is present, the view overrides
    form data processing.
    """
    template_name = "public_data/consent.html"
    form_class = ConsentForm
    success_url = reverse_lazy('my-member-research-data')

    def get(self, request, *args, **kwargs):
        """Customized to allow additional context."""
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(
            self.get_context_data(form=form, **kwargs))

    def form_invalid(self, form):
        """
        Customized to add final section marker when reloading.
        """
        return self.render_to_response(self.get_context_data(form=form,
                                                             section=6))

    def post(self, request, *args, **kwargs):
        """
        Customized to convert a POST with 'section' into GET request.
        """
        if 'section' in request.POST:
            print "Section in POST is " + str(request.POST['section'])
            kwargs['section'] = int(request.POST['section'])
            self.request.method = 'GET'
            return self.get(request, *args, **kwargs)
        else:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            if form.is_valid():
                return self.form_valid(form, request)
            else:
                return self.form_invalid(form)

    # TODO: No need to add `request` here, it's available via `self.request`
    def form_valid(self, form, request):
        """
        If the form is valid, redirect to the supplied URL.
        """
        participant = Participant(member=request.user.member,
                                  enrolled=True,
                                  signature=form.cleaned_data['signature'])
        participant.save()
        django_messages.success(request,
                                ("Thank you! You are now enrolled as a " +
                                 "participant in public data sharing study."))
        return super(ConsentView, self).form_valid(form)


class ToggleSharingView(RedirectView):
    """
    Toggle the specified data_file to the specified value of public.
    """
    url = reverse_lazy('my-member-research-data')

    @staticmethod
    def toggle_data(data_file_path, public):
        model_type, object_id = file_path_to_type_and_id(data_file_path)

        sharing, _ = PublicDataStatus.objects.get_or_create(
            data_file_model=model_type,
            data_file_id=object_id)

        if public == "True":
            sharing.is_public = True
        elif public == "False":
            sharing.is_public = False
        else:
            raise ValueError("'public' parameter must be 'True' or 'False'")

        sharing.save()

    def post(self, request, *args, **kwargs):
        """
        Toggle public sharing status of a dataset.
        """
        if 'data_file' in request.POST and 'public' in request.POST:
            self.toggle_data(request.POST['data_file'],
                             request.POST['public'])

        return super(ToggleSharingView, self).post(request, *args, **kwargs)


class WithdrawView(FormView):
    """
    A very simple form that withdraws the user from the study on POST.
    """
    template_name = 'public_data/withdraw.html'
    form_class = WithdrawForm
    success_url = reverse_lazy('my-member-settings')

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        participant = self.request.user.member.public_data_participant

        participant.enrolled = False
        participant.save()

        django_messages.success(self.request, (
            'You have successfully withdrawn from the study and marked your '
            'files as private.'))

        return super(WithdrawView, self).form_valid(form)
