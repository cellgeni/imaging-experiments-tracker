from django.contrib.auth.models import User
from django.test import TestCase

from experiments import auth
from experiments.authorization.user_permissions import UserPermissions
from experiments.constants import VIEW_PERMISSION
from experiments.models import Project


class UserPermissionTestCase(TestCase):

    def create_project_without_permission(self, user: User, permission: str) -> Project:
        """Create a project for which there will be no 'permission' for a user."""
        project = Project.objects.create(name="unauthorized")
        if auth.check_permission(user.id, project.id, permission):
            auth.remove_permission(user.id, project.id, permission)
        return project

    def create_project_with_permission(self, user: User, permission: str) -> Project:
        """Create a project with a permission for a user."""
        project = Project.objects.create(name="authorized")
        auth.add_permission(user.id, project.id, permission)
        return project

    def test_get_projects_with_viewing_permissions(self):
        user = User.objects.create_user(username="some")
        authorized_project = self.create_project_with_permission(user, VIEW_PERMISSION)
        _ = self.create_project_without_permission(user, VIEW_PERMISSION)
        self.assertEqual([authorized_project], UserPermissions(user).get_projects_with_viewing_permissions())
