from registration.signals import user_activated
from django.dispatch import receiver
from django.contrib.auth.models import Group


@receiver(user_activated)
def add_default_user_group(sender, **kwargs):
    user = kwargs['user']
    user.groups.add(Group.objects.get(name='contributor'))
    user.save()

