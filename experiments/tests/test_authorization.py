from django.contrib.auth.models import User
from django.test import TestCase

from experiments import auth
from experiments.constants import (DELETE_PERMISSION, OWNER_ROLE,
                                   VIEW_PERMISSION, VIEWER_ROLE)
from experiments.models import Project


class AuthorisationTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="some", password="123")
        self.project = Project.objects.create(name="project")

    def test_enforce(self):
        """
        Check a user has a permission manually added to them.
        Check a user no longer has a permission removed from them.
        """
        permission = "delete"
        auth.add_permission(self.user.id, self.project.id, permission)
        self.assertTrue(auth.check_permission(
            self.user.id, self.project.id, permission))
        auth.remove_permission(
            self.user.id, self.project.id, permission)
        self.assertFalse(auth.check_permission(
            self.user.id, self.project.id, permission))

    def test_add_role(self):
        """Check if a user has a role added to them."""
        role = OWNER_ROLE
        auth.add_role(self.user.id, self.project.id, role)
        self.assertEqual(role, auth.get_role(
            self.user.id, self.project.id))
        auth.remove_role(self.user.id, self.project.id, role)
        self.assertEqual(None, auth.get_role(
            self.user.id, self.project.id))
    
    def test_permission_removed_with_roled_removed(self):
        """
        Check if permission is assigned if a role is assigned. 
        Check if permission is removed if the role is removed.
        """
        role = OWNER_ROLE
        auth.add_role(self.user.id, self.project.id, role)
        self.assertTrue(auth.check_permission(
            self.user.id, self.project.id, DELETE_PERMISSION))
        auth.remove_role(self.user.id, self.project.id, role)
        self.assertFalse(auth.check_permission(
            self.user.id, self.project.id, DELETE_PERMISSION))
    
    def test_permission_removed_with_roled_reassigned(self):
        """
        Check if permission is assigned if a role is assigned. 
        Check if permission is removed if the other role is assigned. 
        """
        role = OWNER_ROLE
        auth.add_role(self.user.id, self.project.id, role)
        self.assertTrue(auth.check_permission(
            self.user.id, self.project.id, DELETE_PERMISSION))
        self.assertTrue(auth.check_permission(
            self.user.id, self.project.id, VIEW_PERMISSION))
        new_role = VIEWER_ROLE
        auth.add_role(self.user.id, self.project.id, new_role)
        self.assertFalse(auth.check_permission(
            self.user.id, self.project.id, DELETE_PERMISSION))
        self.assertTrue(auth.check_permission(
            self.user.id, self.project.id, VIEW_PERMISSION))
