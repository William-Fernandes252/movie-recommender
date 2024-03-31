import os
import sys

DJANGO_SETTINGS_MODULE = "config.settings"

PWD = os.getenv("PWD")


def main():
    os.chdir(PWD)
    sys.path.append(PWD)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
    import django

    django.setup()


if __name__ == "__main__":
    main()
