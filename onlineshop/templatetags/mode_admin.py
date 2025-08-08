from django import template
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


@register.filter(name='is_staff')
def is_staff(user):
    if user.is_staff is True:
        return True
    return False
