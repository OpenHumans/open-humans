from django.forms import BooleanField, CharField, Form


class ConsentForm(Form):
    """
    A subclass of django-user-account's SignupForm with a `terms` field to add
    validation for the Terms of Use checkbox.
    """

    check_uncertainty = BooleanField(
        label=('I understand the uncertainty and risk as stated '
               'in this feature activation process.'))
    check_any_purpose = BooleanField(
        label=('I understand that data I choose to publicly share may be '
               'for any purpose, including research purposes.'))
    check_privacy = BooleanField(
        label=('I understand that once I authorize public data sharing, '
               'data privacy laws might not apply or no longer protect my '
               'information.'))
    check_withdraw = BooleanField(
        label=('I understand that I can turn off public data sharing at '
               'any time, but copies of that data that have already been '
               'made by other people may remain.'))
    check_rights = BooleanField(
        label=('By signing this form, I have not given up any of my '
               'legal rights.'))
    check_eligible = BooleanField(
        label=('I am at least 18 years of age.'))
    check_name = BooleanField(
        label='I am signing this form with my full legal name.')

    signature = CharField(label='Electronic Signature',
                          max_length=100)

    class Meta:  # noqa: D101
        fields = '__all__'
