import sys

allowed_undefined_variables = [
    'activity.data_source',
    'activity.share_data',
    'css_classes.label',
    'css_classes.wrap',
    'error',
    'form.code.value',
    'form.email.errors',
    'form.email.value',
    'form.name.errors',
    'form.name.value',
    'form.non_field_errors',
    'form.password.errors',
    'form.password.value',
    'form.password_confirm.errors',
    'form.password_confirm.value',
    'form.terms.errors',
    'form.username.errors',
    'form.username.value',
    'form_submit_value',
    'panel_offset',
    'panel_width',
    'public_button_next',
    'quiz_complete',
    'section',
    'source',
    'source.href_next',
    'user_data.href_next',
]


class InvalidString(str):
    """
    Raise an exception if an invalid template string is encountered.
    """

    def __mod__(self, other):
        if getattr(other, 'var') in allowed_undefined_variables:
            return super(InvalidString, self).__mod__(other)

        from django.template.base import TemplateSyntaxError

        raise TemplateSyntaxError(
            'Undefined variable or unknown value for "{}" ({})'.format(
                other, other.var))


def has_migration(app, migration):
    if 'migrate' in sys.argv:
        return False

    if 'test' not in sys.argv:
        return True

    from django.db.migrations.recorder import MigrationRecorder

    try:
        MigrationRecorder.Migration.objects.get(app=app, name=migration)
    except MigrationRecorder.Migration.DoesNotExist:
        return False

    return True
