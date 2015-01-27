from django.forms import BooleanField, CharField, Form


class ConsentForm(Form):
    """
    A subclass of django-user-account's SignupForm with a `terms` field to add
    validation for the Terms of Use checkbox.
    """
    check_uncertainty = BooleanField(
        label=("I understand the uncertainty and risk of research as stated " +
               "in this consent form."))
    check_any_purpose = BooleanField(
        label=("I understand that data I choose to publicly share may be " +
               "for any purpose, including research purposes."))
    check_privacy = BooleanField(
        label=("I understand that once I authorize public data sharing, " +
               "data privacy laws might not apply or no longer protect my " +
               "information."))
    check_withdraw = BooleanField(
        label=("I understand that I can withdraw data from Open Humans at " +
               "any time, but copies of that data that have already been " +
               "made by other people may remain."))
    check_rights = BooleanField(
        label=("By signing this consent form, I have not given up any of my " +
               "legal rights."))
    check_eligible = BooleanField(
        label=("I am a United States citizen or permanent resident and I am " +
               "at least 18 years of age."))
    check_name = BooleanField(
        label="I am signing this form with my full legal name.")

    signature = CharField(label="Electronic Signature of Participant",
                          max_length=100)

    class Meta:
        fields = '__all__'
