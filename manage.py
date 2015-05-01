#!/usr/bin/env python

# apply the .env environment here because it might contain environment
# variables that change how Python outputs deprecration warnings, for example
from env_tools import apply_env

apply_env()

import os
import sys

if 'IGNORE_SPURIOUS_WARNINGS' in os.environ:
    import warnings

    warnings.filterwarnings('ignore', '', DeprecationWarning)
    warnings.filterwarnings('ignore', '', RuntimeWarning,
                            'django.db.models.fields')

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'open_humans.settings')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
