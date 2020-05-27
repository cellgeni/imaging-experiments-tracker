import os
from typing import List
from django.db import connections
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from casbin_sqlalchemy_adapter import Adapter
import casbin

casbin.log.get_logger().enable_log(True)


def get_obj_id_from_name(obj_type: str, obj_name: str) -> int:
    """Get id of object by type and name"""
    ct = ContentType.objects.get(model=obj_type)
    obj_model = ct.get_object_for_this_type(name=obj_name)
    return obj_model.id


class Authz:
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
    __enforcer = casbin.Enforcer(
        os.path.join(settings.CASBIN_ROOT, 'model.conf'),
        __adapter, True)

    @staticmethod
    def add_permission(username: str, obj_type: str, obj_name: str, action: str) -> None:
        """Add new permission to casbin rules"""
        obj_id = get_obj_id_from_name(obj_type, obj_name)
        Authz.__enforcer.add_permission_for_user(
            username, obj_type, obj_id, action)

    @staticmethod
    def delete_permission(username: str, obj_type: str, obj_name: str, action: str) -> None:
        """Delete permission from casbin rules"""
        obj_id = get_obj_id_from_name(obj_type, obj_name)
        Authz.__enforcer.delete_permission_for_user(
            username, obj_type, obj_id, action)

    @staticmethod
    def get_user_policy(username: str) -> List[str]:
        """Get stored polcies for a given user"""
        return Authz.__enforcer.get_filtered_policy(0, username)

    @staticmethod
    def get_user_roles(username: str) -> List[str]:
        """Get stored roles for a given user"""
        return Authz.__enforcer.get_roles_for_user(username)

    @staticmethod
    def enforce(username: str, obj_type: str = None, obj_name: str = None, action: str = None, obj_id: int = None) -> bool:
        """Checks if a user can do an action on an object (obj and obj_type)."""
        # does this user exist?
        if not User.objects.filter(username=username).exists():
            casbin.log.log_printf(f"User {username} does not exist ---> False ")
            return False
        # are we enforcing a name or an id?
        _id = obj_id or get_obj_id_from_name(obj_type, obj_name)
        # is this user a superuser?
        if User.objects.get(username=username).is_superuser:
            casbin.log.log_printf(f"Request: {username}, {obj_type}, {_id}, {action} ---> True ")
            return True

        return Authz.__enforcer.enforce(username, obj_type, str(_id), action)
