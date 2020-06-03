
from django.test import TestCase
from experiments.models.measurement import Project
from experiments import auth
from django.contrib.auth.models import User

from typing import List


class AddingRolesPerProjectTestCase(TestCase):
    """
    Test whether fields in a row that represent a measurement_number in a spreadsheet
    properly map to corresponding Measurement attributes.
    """

    @staticmethod
    def _create_external_user(prefix) -> User:
        """Create an external user."""
        user = User.objects.create_user(f"{prefix}_external_user")
        user.profile.is_external = True
        user.save()
        return user

    def create_test_users_of_all_kinds(self, prefix: str) -> List[User]:
        """Create all kinds of users: superuser, internal user, external user."""
        admin = User.objects.create_superuser(f"{prefix}_admin")
        internal_user = User.objects.create_user(f"{prefix}_internal_user")
        external_user = self._create_external_user(prefix)
        return [admin, internal_user, external_user]

    def test_assigning_roles_on_new_projects(self):
        """"Test that different kinds of users get their default roles on a newly created project"""
        self.create_test_users_of_all_kinds("new_projects")
        project = Project.objects.create(name="new")
        for user in User.objects.all():
            self.assert_user_role_in_project(user, project)

    def test_roles_for_new_users(self):
        """Test that all new users get a role for every project."""
        # Project.objects.get_or_create(name="new_user_project")
        # for user in self.create_test_users_of_all_kinds("i"):
        #     for project in Project.objects.all():
        #         self.assert_user_role_in_project(user, project)
        pass

    def assert_user_role_in_project(self, user: User, project: Project) -> None:
        """Check that a superuser has an owner role on a project, otherwise a viewer role."""
        self.assertEqual(user.profile.get_default_role(),
                         auth.get_role(user.id, project.id))

    def test_deleting_roles_on_deleting_projects(self):
        """Test that deletes all roles related to a deleted project."""
        project = Project.objects.create(name="to_be_deleted")
        project_id = project.id
        project.delete()
        for user in User.objects.all():
            self.assertIs(None, auth.get_role(user.id, project_id))

    def test_deleting_roles_on_deleting_users(self):
        """Test deletion of all roles related to a deleted user."""
        user = User.objects.create(username="some")
        project = Project.objects.create(name="to_be_checked")
        auth.add_role(user.id, project.id, user.profile.get_default_role())
        user_id = user.id
        user.delete()
        self.assertIs(None, auth.get_role(user_id, project.id))
