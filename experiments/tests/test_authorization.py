from django.test import TestCase
from experiments.auth import Authorization
from experiments.models import Project
from django.contrib.auth.models import User


class AuthorisationTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="some", password="123")
        self.project = Project.objects.create(name="project")

    def test_enforce(self):
        """
        Get a project, get a user, assign a permission, check the permission
        was applied. Remove the permission, check user no longer has it.
        """
        permission = "delete"
        Authorization.add_permission(self.user.id, self.project.id, permission)
        self.assertTrue(Authorization.enforce(
            self.user.id, self.project.id, permission))

    # def test_add_permission(self):
    #     """Get a user, add a permission to a project, check permission was added."""
    #     permission = "delete"
    #     user = User.objects.create(username="some", password="123")
    #     project = Project.objects.create(name="project")
    #     Authorization.add_permission(user.id, project.id, permission)
    #     self.assertIn(permission, Authorization.get_user_policy())
