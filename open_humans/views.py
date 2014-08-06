from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy
from django.forms import BooleanField, ModelForm
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from .models import Profile


class UserProfileDetailView(DetailView):
    """
    A view of the current user's profile.
    """
    context_object_name = 'profile'
    model = Profile
    template_name = 'profile/detail.html'

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileEditForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.form_id = 'edit-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'

        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            'about_me',
        )

        self.helper.add_input(Submit('save', 'Save'))

    class Meta:
        model = Profile
        # XXX: When the next version of crispy-forms comes out this duplication
        # should no longer be necessary.
        fields = ('about_me',)


class UserProfileEditView(UpdateView):
    """
    An edit view of the current user's profile.
    """
    form_class = ProfileEditForm
    model = Profile
    template_name = 'profile/edit.html'
    success_url = reverse_lazy('profile-detail')

    def get_object(self, queryset=None):
        return self.request.user.profile


class UserWithTermsForm(UserCreationForm):
    """
    Subclass Django's UserCreationForm and add a `terms` field to it to add
    validation for the Terms of Use checkbox.
    """
    terms = BooleanField()

    class Meta(UserCreationForm.Meta):
        # The default form doesn't include the email address so add it here too
        fields = UserCreationForm.Meta.fields + ('email', 'terms',)


class UserCreateView(CreateView):
    """
    A view that creates a new user, logs them in, and redirects them to the
    root URL.
    """
    form_class = UserWithTermsForm
    template_name = 'signup.html'

    def form_valid(self, form):
        form.save()

        user = authenticate(username=form.cleaned_data.get('username'),
                            password=form.cleaned_data.get('password1'))

        if user is not None:
            login(self.request, user)

        return HttpResponseRedirect('/')
