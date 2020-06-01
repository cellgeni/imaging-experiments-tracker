import os
from typing import Dict, List, Union

import casbin
import yaml
from casbin_sqlalchemy_adapter import Adapter
from django.conf import settings
from django.db import connections

RoleDefinitionT = Dict[str, List[str]]


class CasbinEnforcerFactory:

    @staticmethod
    def _create_connection_string():
        """Create a connection string for a database connection."""
        connection_params = connections['default'].get_connection_params()
        connection_string = "{vendor}://{user}:{password}@{host}:{port}/{database}"
        return connection_string.format(
            vendor=connections['default'].vendor,
            user=connection_params['user'],
            password=connection_params['password'],
            host=connection_params['host'],
            port=connection_params.get('port', 5432),
            database=connection_params['database'])

    @classmethod
    def _create_adapter(cls):
        """Create database adapter for casbin enforcer."""
        if connections['default'].vendor == "sqlite":
            connection_string = "sqlite://"
        else:
            connection_string = cls._create_connection_string()
        return Adapter(connection_string)

    @classmethod
    def create_enforcer(cls):
        """Return an instance of casbin enforcer."""
        adapter = cls._create_adapter()
        model_path = os.path.join(settings.CASBIN_ROOT, 'model.conf')
        return casbin.Enforcer(model_path, adapter, False)


class Authorization:
    """Authorization helper class that wraps casbin access control"""
    _enforcer = CasbinEnforcerFactory.create_enforcer()

    def __init__(self, roles_filename: str) -> None:
        with open(roles_filename) as f:
            self.roles = yaml.safe_load(f)

    def add_permission(self, user_id: int, project_id: int, permission: str) -> None:
        """Add new permission to casbin rules."""
        self._enforcer.add_permission_for_user(
            str(user_id), str(project_id), str(project_id), permission)

    def remove_permission(self, user_id: str, project_id: str,  permission: str) -> None:
        """Delete permission from casbin rules."""
        self._enforcer.delete_permission_for_user(
            str(user_id), str(project_id), str(project_id), permission)

    def _attach_role_definition(self, user_id: int, project_id: int, role_definition: RoleDefinitionT, role_name: str) -> None:
        """Add a role and permissions from a role definition to a user in a given project."""
        self.remove_existing_role(user_id, project_id)
        self._add_permissions_from_a_role_definition(role_definition, user_id, project_id)
        self._enforcer.add_role_for_user_in_domain(str(user_id), role_name, str(project_id))

    def _add_permissions_from_a_role_definition(self, role_definition: RoleDefinitionT, user_id: int, project_id: int) -> None:
        for permission in role_definition['permissions']:
            self.add_permission(user_id, project_id, permission)

    def remove_existing_role(self, user_id: int, project_id: int) -> None:
        """Remove an existing role if any from a user for a project."""
        current_role = self.get_role(user_id, project_id)
        if current_role:
            self.remove_role(user_id, project_id, current_role)

    def add_role(self, user_id: int, project_id: int, role_name: str) -> None:
        """Find a role in the list of roles and give it to a user in a given project."""
        for role in self.roles['roles']:
            if role['name'] == role_name:
                return self._attach_role_definition(user_id, project_id, role, role_name)
        raise ValueError("Unknown role")

    def get_role(self, user_id: int, project_id: int) -> Union[str, None]:
        """Return a role for a user in a given project."""
        roles = self._enforcer.get_roles_for_user_in_domain(
            str(user_id), str(project_id))
        if len(roles) > 1:
            raise AttributeError("A user should not have more than one role for a project")
        elif roles:
            return roles[0]
        else:
            return None

    def remove_role(self, user_id: int, project_id: int, role_name: str) -> None:
        """Remove a role for a user in a given project."""
        self._enforcer.delete_roles_for_user_in_domain(
            str(user_id), role_name, str(project_id))
        for policy in self._enforcer.get_permissions_for_user_in_domain(str(user_id), str(project_id)):
            self.remove_permission(policy[0], policy[1], policy[-1])

    def check_permission(self, user_id: int, project_id: str, permission: str) -> bool:
        """Check if a user has permission on an object."""
        return self._enforcer.enforce(str(user_id), str(project_id), str(project_id), permission)
