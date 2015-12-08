from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.detail import SingleObjectMixin

from ipware.ip import get_ip

from common.mixins import PrivateMixin
from data_import.models import DataFileAccessLog
from data_import.utils import app_name_to_content_type

from .forms import ConsentForm
from .models import PublicDataAccess, WithdrawalFeedback


class QuizView(PrivateMixin, TemplateView):
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


class ConsentView(PrivateMixin, FormView):
    """
    Modification of FormView that walks through the informed consent content.

    Stepping through the form is triggered by POST requests containing new
    values in the 'section' field. If this field is present, the view overrides
    form data processing.
    """
    template_name = 'public_data/consent.html'
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
            kwargs['section'] = int(request.POST['section'])

            self.request.method = 'GET'

            return self.get(request, *args, **kwargs)
        else:
            form_class = self.get_form_class()
            form = self.get_form(form_class)

            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        participant = self.request.user.member.public_data_participant

        participant.enrolled = True
        participant.signature = form.cleaned_data['signature']

        participant.save()

        django_messages.success(self.request,
                                ('Thank you! You are now enrolled as a '
                                 'participant in the public data sharing '
                                 'study.'))

        return super(ConsentView, self).form_valid(form)


class ToggleSharingView(PrivateMixin, RedirectView):
    """
    Toggle the specified data_file to the specified value of public.
    """
    permanent = False
    url = reverse_lazy('my-member-research-data')

    @staticmethod
    def toggle_data(user, source, public):
        model, model_type = app_name_to_content_type(source)

        data_files = (model.objects
                      .filter(user_data__user=user)
                      .order_by('-task__start_time'))

        # first set all access to False
        for data_file in data_files:
            access, _ = PublicDataAccess.objects.get_or_create(
                data_file_model=model_type,
                data_file_id=data_file.pk)

            access.is_public = False
            access.save()

        # then, if public, set the data access to True for only the latest file
        if public == 'True':
            access, _ = PublicDataAccess.objects.get_or_create(
                data_file_model=model_type,
                data_file_id=data_files[0].pk)

            access.is_public = True
            access.save()

    def post(self, request, *args, **kwargs):
        """
        Toggle public sharing status of a dataset.
        """
        if 'source' in request.POST and 'public' in request.POST:
            public = request.POST['public']

            if public not in ['True', 'False']:
                raise ValueError("'public' must be 'True' or 'False'")

            self.toggle_data(request.user,
                             request.POST['source'],
                             request.POST['public'])
        else:
            raise ValueError("'public' and 'source' must be specified")

        return super(ToggleSharingView, self).post(request, *args, **kwargs)


class WithdrawView(PrivateMixin, CreateView):
    """
    A very simple form that withdraws the user from the study on POST.
    """
    template_name = 'public_data/withdraw.html'
    model = WithdrawalFeedback
    fields = ['feedback']
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

        form.instance.member = self.request.user.member

        return super(WithdrawView, self).form_valid(form)


class HomeView(TemplateView):
    """
    Provide this page's URL as the next URL for login or signup.
    """
    template_name = 'public_data/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context.update({'next': reverse_lazy('public-data:home')})

        return context
