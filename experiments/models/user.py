from typing import List
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User

from experiments.models import CasbinRule
from experiments.auth import Authz


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_external = models.BooleanField('External group member', default=False)

    def get_policy(self) -> List[str]:
        return Authz.get_user_policy(self.user.username)

    def has_policy(self, obj_type: str = None, obj_name: str = None, action: str = None, obj_id: int = None) -> bool:
        return Authz.enforce(
            username=self.user.username,
            obj_type=obj_type,
            obj_name=obj_name,
            aciton=action,
            obj_id=obj_id)

    def get_roles(self) -> List[str]:
        Authz.get_roles_for_user(self.user.username)


@receiver(models.signals.post_save, sender=User)
def create_user_profile_signal(sender, instance, created, **kwargs):
    """Create Profile for every new User."""
    if created:
        Profile.objects.create(user=instance)


@receiver(models.signals.post_delete, sender=User)
def cleanup_casbin_rules_after_user_deletion(sender, instance, *args, **kwargs):
    """ Deletes casbin_rules after deleting a User."""
    Authz.delete_roles_for_user(instance.username)
