#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "achiever.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Check if 'runserver' is in the arguments and no port is specified
    if 'runserver' in sys.argv and len(sys.argv) == 2:
        sys.argv.append('8001')
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
