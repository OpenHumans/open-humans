from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from .forms import ConsentForm
from .models import Participant


class QuizView(TemplateView):
    """
    Modification of TemplateView that accepts and requires POST.

    This prevents users from jumping to the quiz link without going through
    the informed consent pages.
    """
    template_name='public_data/quiz.html'

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
        """Customized to convert a POST with 'section' into GET request"""
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
