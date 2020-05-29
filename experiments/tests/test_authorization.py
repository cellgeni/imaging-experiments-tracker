import os

from django.test import TestCase
from django.conf import settings
from experiments.auth import Authorization
from experiments.models import Project
from django.contrib.auth.models import User


class AuthorisationTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="some", password="123")
        self.project = Project.objects.create(name="project")
        #self.auth = Authorization(os.path.join(settings.CASBIN_ROOT, "roles.yaml"))

    def test_enforce(self):
        """
        Get a project, get a user, assign a permission, check the permission
        was applied. Remove the permission, check user no longer has it.
        """
        permission = "delete"
        Authorization.add_permission(self.user.id, self.project.id, permission)
        self.assertTrue(Authorization.enforce(
            self.user.id, self.project.id, permission))
        Authorization.remove_permission(
            self.user.id, self.project.id, permission)
        self.assertFalse(Authorization.enforce(
            self.user.id, self.project.id, permission))

    def test_add_role(self):
        """Add role to a user"""
        auth = Authorization(os.path.join(settings.CASBIN_ROOT, "roles.yaml"))
        role = "owner"
        auth.add_role(self.user.id, self.project.id, role)
        self.assertEqual(role, auth.get_role(
            self.user.id, self.project.id))
        auth.remove_role(self.user.id, self.project.id, role)
        self.assertEqual(None, auth.get_role(
            self.user.id, self.project.id))
