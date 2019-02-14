#!/usr/bin/env python3

import os
import sys

# apply the .env environment here because it might contain environment
# variables that change how Python outputs deprecration warnings, for example
from env_tools import apply_env

apply_env()


if "test" in sys.argv:
    import django.template.base as template_base

    from open_humans.testing import allowed_undefined_variables

    old_resolve = template_base.Variable.resolve

    def new_resolve(self, context):
        """
        Replace the `resolve` method of Django's `Variable` so that it can
        throw an `Exception` for undefined variables.
        """
        try:
            value = old_resolve(self, context)
        except template_base.VariableDoesNotExist as e:
            # if it's not a variable that's allowed to not exist then raise a
            # base Exception so Nodes can't catch it (which will make the test
            # fail)
            if self.var not in allowed_undefined_variables:
                raise Exception(e)

            # re-raise the original and let the individual Nodes deal with it
            # however they'd like
            raise e

        return value

    template_base.Variable.resolve = new_resolve


if "IGNORE_SPURIOUS_WARNINGS" in os.environ:
    import warnings

    warnings.filterwarnings("ignore", "", DeprecationWarning)
    warnings.filterwarnings("ignore", "", RuntimeWarning, "django.db.models.fields")


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "open_humans.settings")

    # pylint: disable=ungrouped-imports
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
