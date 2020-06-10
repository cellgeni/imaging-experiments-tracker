from typing import List

from django.contrib.auth.models import User

from experiments import auth
from experiments.constants import VIEW_PERMISSION
from experiments.models.measurement import Project


class UserPermissions:

    def __init__(self, user: User):
        self.user = user

    def get_projects_with_viewing_permissions(self) -> List[Project]:
        """Return a list of projects for which a user has viewing permissions."""
        res = []
        for project in Project.objects.all():
            if auth.check_permission(self.user.id, project.id, VIEW_PERMISSION):
                res.append(project)
        return res
