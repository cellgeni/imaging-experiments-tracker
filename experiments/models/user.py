from typing import List
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User

from experiments.models import CasbinRule
from experiments.authorization import Authorization


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_external = models.BooleanField('External group member', default=False)


@receiver(models.signals.post_save, sender=User)
def create_user_profile_signal(sender, instance, created, **kwargs):
    """Create Profile for every new User."""
    if created:
        Profile.objects.create(user=instance)


# @receiver(models.signals.post_delete, sender=User)
# def cleanup_casbin_rules_after_user_deletion(sender, instance, *args, **kwargs):
#     """ Deletes casbin_rules after deleting a User."""
#     Authorization.delete_roles_for_user(instance.username)
