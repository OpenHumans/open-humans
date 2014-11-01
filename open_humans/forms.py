from account.forms import SignupForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Submit

from django.forms import BooleanField, ModelForm

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

        # I later realize this is a hack on the intended usage of 'initial'.
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
            HTML("""
                <h4>Receive news and updates</h4>
                <p>Don't want to miss out on new features and opportunities?
                Make sure you're subscribed to receive news and updates.</p>
                """),
            'newsletter',
            HTML("""
                <h4>Allow other Open Humans members to contact you</h4>
                <p>You'll receive their message and email address, but your
                email address won't be revealed unless you choose to reply.</p>
                """),
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
