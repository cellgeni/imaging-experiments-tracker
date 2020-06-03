from typing import Union
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User

from experiments.constants import Role


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_external = models.BooleanField('External group member', default=False)

    def get_default_role(self) -> Union[Role, None]:
        if not self.is_external:
            if self.user.is_superuser:
                return Role.OWNER
            else:
                return Role.VIEWER
        return None

@receiver(models.signals.post_save, sender=User)
def create_user_profile_signal(sender, instance, created, **kwargs):
    """Create Profile for every new User."""
    if created:
        Profile.objects.create(user=instance)