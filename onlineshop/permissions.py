from django.conf import settings


def check_permission(user):
    if user.is_admin:
        return True
    else:
        return False