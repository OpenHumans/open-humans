from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def participant_required(function=None,
                         redirect_field_name=REDIRECT_FIELD_NAME,
                         login_url=None):
    """
    Decorator for views that checks that the user is a participant, redirecting
    to the signup page if necessary.
    """
    def logged_in_and_is_participant(user):
        return user.is_authenticated() and user.member is not None

    actual_decorator = user_passes_test(
        logged_in_and_is_participant,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)

    return actual_decorator
