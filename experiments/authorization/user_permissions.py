from typing import List

from django.contrib.auth.models import User

from experiments import auth
from experiments.constants import VIEW_PERMISSION, Role
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

    def assign_a_role_in_all_projects(self, role: Role):
        """Assign a user a role in all projects."""
        for project in Project.objects.all():
            auth.add_role(self.user.id, project.id, role)

    def delete_all_roles(self):
        """Remove roles for a user in all projects."""
        for project in Project.objects.all():
            auth.remove_existing_role(self.user.id, project.id)

