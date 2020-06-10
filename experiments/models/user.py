from typing import Union

from django.contrib.auth.models import User
from django.db import models

from experiments.constants import Role


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_external = models.BooleanField('External group member', default=False)

    def get_default_role(self) -> Union[Role, None]:
        """Get a default role depending on the kind of this user."""
        if not self.is_external:
            if self.user.is_superuser:
                return Role.OWNER
            else:
                return Role.VIEWER
        return None

    def __str__(self) -> str:
        if self.is_external:
            return f"External group member"
        return f"Group member"
