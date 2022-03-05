from django import template
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, permission_required
from order.models import AccessMode
register = template.Library()


@register.filter(name='mode_admin')
def mode_admin(user):
    try:
        mode = AccessMode.objects.get(user=user)
        if mode.admin is True:
            return True
    except:
        return False
    return False
