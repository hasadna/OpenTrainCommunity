#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    env_or_default_settings = os.getenv('DJANGO_SETTINGS_MODULE', 'train2.settings.dev_settings')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', env_or_default_settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
