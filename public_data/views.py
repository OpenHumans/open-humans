from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from .forms import ConsentForm


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
    success_url = "/"

    def get(self, request, *args, **kwargs):
        """Customized to allow additional context."""
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(
            self.get_context_data(form=form, **kwargs))

    def post(self, request, *args, **kwargs):
        """Customized to convert a POST with 'section' into GET request"""
        if 'section' in request.POST:
            print "Section in POST is " + str(request.POST['section'])
            kwargs['section'] = int(request.POST['section'])
            self.request.method = 'GET'
            return self.get(request, *args, **kwargs)
        else:
            return super(ConsentView, self).post(request, *args, **kwargs)
