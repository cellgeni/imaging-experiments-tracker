import os
from typing import List, Union
from django.db import connections
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from casbin_sqlalchemy_adapter import Adapter
import casbin

import yaml
# def get_obj_id_from_name(model: str):
#     """Get id of object by type and name"""
#     ct = ContentType.objects.get(model=model)
#     obj_model = ct.get_object_for_this_type(name=model.id)


class Authorization:
    """Authorization helper class that wraps casbin access control"""
    # private class vars used to connect the enfonrcer to the backend database
    __connection_params = connections['default'].get_connection_params()
    __connection_string = "{vendor}://{user}:{password}@{host}:{port}/{database}"
    __adapter = Adapter(__connection_string.format(
        vendor=connections['default'].vendor,
        user=__connection_params['user'],
        password=__connection_params['password'],
        host=__connection_params['host'],
        port=__connection_params.get('port', 5432),
        database=__connection_params['database']))
    _enforcer = casbin.Enforcer(os.path.join(
        settings.CASBIN_ROOT, 'model.conf'), __adapter, False)

    def __init__(self, roles_filename: str) -> None:
        with open(roles_filename) as f:
            self.roles = yaml.load(f)

    @staticmethod
    def add_permission(user_id: int, project_id: int, permission: str) -> None:
        """Add new permission to casbin rules"""
        Authorization._enforcer.add_permission_for_user(
            str(user_id), str(project_id), str(project_id), permission)

    @staticmethod
    def remove_permission(user_id: str, project_id: str,  permission: str) -> None:
        """Delete permission from casbin rules"""
        Authorization._enforcer.delete_permission_for_user(
            str(user_id), str(project_id), str(project_id), permission)

    def add_role(self, user_id: int, project_id: int, role_name: str) -> None:
        """Add a role for a user in a given project."""
        for role in self.roles['roles']:
            if role['name'] == role_name:
                for permission in role['permissions']:
                    self.add_permission(user_id, project_id, permission)
                self._enforcer.add_role_for_user_in_domain(
                    str(user_id), role_name, str(project_id))

    def get_role(self, user_id: int, project_id: int) -> Union[str, None]:
        """Return a role for a user in a given project."""
        roles = self._enforcer.get_roles_for_user_in_domain(
            str(user_id), str(project_id))
        if roles:
            if len(roles) > 1:
                raise ImplementationError(
                    "A user should not have more than one project in a domain")
            else:
                return roles[0]
        return None

    def remove_role(self, user_id: int, project_id: int, role_name: str) -> None:
        """Remove a role for a user in a given project."""
        self._enforcer.delete_roles_for_user_in_domain(
            str(user_id), role_name, str(project_id))

    @staticmethod
    def get_user_roles(username: str) -> List[str]:
        """Get stored roles for a given user"""
        return Authorization._enforcer.get_roles_for_user(username)

    @staticmethod
    def enforce(user_id: int, project_id: str, action: str) -> bool:
        """Check if a user can do an action on an object (obj and model)."""
        # if User.objects.get(username=username).is_superuser:
        #     casbin.log.log_printf(
        #         f"Request: {username}, {model}, {_id}, {action} ---> True ")
        #     return True
        return Authorization._enforcer.enforce(
            str(user_id), str(project_id), str(project_id), action)
