import os

from django.test import TestCase
from django.conf import settings
from experiments.auth import Authorization
from experiments.models import Project
from django.contrib.auth.models import User

DELETE_PERMISSION = "delete"
VIEW_PERMISSION = "view"
OWNER_ROLE = "owner"
VIEWER_ROLE = "viewer"

class AuthorisationTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="some", password="123")
        self.project = Project.objects.create(name="project")
        self.auth = Authorization(os.path.join(settings.CASBIN_ROOT, "roles.yaml"))

    def test_enforce(self):
        """
        Check a user has a permission manually added to them.
        Check a user no longer has a permission removed from them.
        """
        permission = "delete"
        self.auth.add_permission(self.user.id, self.project.id, permission)
        self.assertTrue(self.auth.check_permission(
            self.user.id, self.project.id, permission))
        self.auth.remove_permission(
            self.user.id, self.project.id, permission)
        self.assertFalse(self.auth.check_permission(
            self.user.id, self.project.id, permission))

    def test_add_role(self):
        """Check if a user has a role added to them."""
        role = OWNER_ROLE
        self.auth.add_role(self.user.id, self.project.id, role)
        self.assertEqual(role, self.auth.get_role(
            self.user.id, self.project.id))
        self.auth.remove_role(self.user.id, self.project.id, role)
        self.assertEqual(None, self.auth.get_role(
            self.user.id, self.project.id))
    
    def test_permission_removed_with_roled_removed(self):
        """
        Check if permission is assigned if a role is assigned. 
        Check if permission is removed if the role is removed.
        """
        role = OWNER_ROLE
        self.auth.add_role(self.user.id, self.project.id, role)
        self.assertTrue(self.auth.check_permission(
            self.user.id, self.project.id, DELETE_PERMISSION))
        self.auth.remove_role(self.user.id, self.project.id, role)
        self.assertFalse(self.auth.check_permission(
            self.user.id, self.project.id, DELETE_PERMISSION))
    
    def test_permission_removed_with_roled_reassigned(self):
        """
        Check if permission is assigned if a role is assigned. 
        Check if permission is removed if the other role is assigned. 
        """
        role = OWNER_ROLE
        self.auth.add_role(self.user.id, self.project.id, role)
        self.assertTrue(self.auth.check_permission(
            self.user.id, self.project.id, DELETE_PERMISSION))
        self.assertTrue(self.auth.check_permission(
            self.user.id, self.project.id, VIEW_PERMISSION))
        new_role = VIEWER_ROLE
        self.auth.add_role(self.user.id, self.project.id, new_role)
        self.assertFalse(self.auth.check_permission(
            self.user.id, self.project.id, DELETE_PERMISSION))
        self.assertTrue(self.auth.check_permission(
            self.user.id, self.project.id, VIEW_PERMISSION))
