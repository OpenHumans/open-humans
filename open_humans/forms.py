from account.forms import SignupForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Submit

from django.forms import BooleanField, ModelForm
from django.template.loader import render_to_string

from .models import Profile


class CustomSignupForm(SignupForm):
    """
    A subclass of django-user-account's SignupForm with a `terms` field to add
    validation for the Terms of Use checkbox.
    """
    terms = BooleanField()

    class Meta:
        fields = '__all__'


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
            'profile_image',
            'about_me',
        )

        # May be a hack. Intended 'initial' usage is "to declare the initial
        # value of form fields at runtime", not as general form customization.
        submit_value = 'Save'
        if 'submit_value' in kwargs['initial']:
            submit_value = kwargs['initial']['submit_value']
        self.helper.add_input(Submit('save', submit_value))

    class Meta:
        model = Profile
        # XXX: When the next version of crispy-forms comes out this duplication
        # should no longer be necessary.
        fields = ('profile_image', 'about_me',)


class SettingsEditForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SettingsEditForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.form_id = 'edit-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'

        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            HTML(render_to_string('profile/form-info-newsletter.html')),
            'newsletter',
            HTML(render_to_string(
                'profile/form-info-allow-user-messages.html')),
            'allow_user_messages',
        )

        # I later realize this is a hack on the intended usage of 'initial'.
        submit_value = 'Save'
        if 'submit_value' in kwargs['initial']:
            submit_value = kwargs['initial']['submit_value']
        self.helper.add_input(Submit('save', submit_value))

    class Meta:
        model = Profile
        # XXX: When the next version of crispy-forms comes out this duplication
        # should no longer be necessary.
        fields = ('newsletter', 'allow_user_messages',)
