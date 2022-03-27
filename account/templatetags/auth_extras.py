from django import template
from django.contrib.auth.models import Group
from account.models import *

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


def allow_register(id=1):
    try:
        config = Config.objects.get(id=1)
    except:
        config = Config.objects.create(register=False)
        config.save()
    allow_register = config.register
    return allow_register


register.filter('allow_register', allow_register)