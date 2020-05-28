import os
from typing import List
from django.db import connections
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from casbin_sqlalchemy_adapter import Adapter
import casbin

casbin.log.get_logger().enable_log(False)


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
    __enforcer = casbin.Enforcer(os.path.join(
        settings.CASBIN_ROOT, 'model.conf'), __adapter, False)

    @staticmethod
    def add_permission(user_id: int, instance_id: int, permission: str) -> None:
        """Add new permission to casbin rules"""
        pass
        # obj_id=get_obj_id_from_name(model, Authorization.__enforcer.add_permission_for_user(
        #    username, model, obj_id, action)

    @staticmethod
    def delete_permission(username: str, model: str,  str) -> None:
        """Delete permission from casbin rules"""
        pass
        # obj_id=get_obj_id_from_name(model, Authorization.__enforcer.delete_permission_for_user(
        #    username, model, obj_id, action)

    @staticmethod
    def get_user_policy(username: str) -> List[str]:
        """Get stored polcies for a given user"""
        return Authorization.__enforcer.get_filtered_policy(0, username)

    @staticmethod
    def get_user_roles(username: str) -> List[str]:
        """Get stored roles for a given user"""
        return Authorization.__enforcer.get_roles_for_user(username)

    @staticmethod
    def enforce(user_id: int, instance_id: str, action: str) -> bool:
        """Check if a user can do an action on an object (obj and model)."""
        # if User.objects.get(username=username).is_superuser:
        #     casbin.log.log_printf(
        #         f"Request: {username}, {model}, {_id}, {action} ---> True ")
        #     return True
        return Authorization.__enforcer.enforce(
            str(user_id), str(instance_id), action)
