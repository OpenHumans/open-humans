from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.forms import BooleanField
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView


class UserWithTermsForm(UserCreationForm):
    """
    Subclass Django's UserCreationForm and add a `terms` field to it to add
    validation for the Terms of Use checkbox.
    """
    terms = BooleanField()

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'terms',)


class UserCreateView(CreateView):
    """
    A view that creates a new user, logs them in, and redirects them to the
    root URL.
    """
    form_class = UserWithTermsForm
    template_name = 'home.html'

    def form_valid(self, form):
        form.save()

        user = authenticate(username=form.cleaned_data.get('username'),
                            password=form.cleaned_data.get('password1'))

        if user is not None:
            login(self.request, user)

        return HttpResponseRedirect('/')
