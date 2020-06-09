from typing import Union

from django.contrib.auth.models import User
from django.db import models

from experiments.constants import Role, ROLE_POLICY_TYPE, PERMISSION_POLICY_TYPE
from experiments.models.measurement import Project


class CasbinRule(models.Model):
    """Map model to access casbin_rules directly from the database."""
    # policy_type indicates whether this rule is a role (g) or a permission (p)
    policy_type = models.CharField(db_column="ptype", max_length=255, blank=True, null=True)
    user_id = models.CharField(db_column='v0', max_length=255, blank=True, null=True)
    # role_name field is a role when policy type is "g" and a domain when policy type is "p".
    role_name = models.CharField(db_column='v1', max_length=255, blank=True, null=True)
    project_id = models.CharField(db_column='v2', max_length=255, blank=True, null=True)
    action = models.CharField(db_column='v3', max_length=255, blank=True, null=True)
    v4 = models.CharField(max_length=255, blank=True, null=True)
    v5 = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'casbin_rule'
        app_label = 'auth'
        verbose_name = 'Project Role'
        verbose_name_plural = 'Project Roles'

    def __str__(self):
        if self.policy_type == PERMISSION_POLICY_TYPE:
            return f"User {self.user} has {self.action} permission on project {self.project}"
        if self.policy_type == ROLE_POLICY_TYPE:
            return f"User {self.user} has {self.role} role on project {self.project}"
        return ""

    @property
    def user(self) -> User:
        """Get the user associated with this permission or role."""
        return User.objects.get(id=int(self.user_id))

    @property
    def project(self) -> Project:
        """Get the project associated with this permission or role."""
        return Project.objects.get(id=int(self.project_id))

    @property
    def role(self) -> Union[Role, None]:
        """Get the role for this rule. If this is a permission return None"""
        if self.policy_type == ROLE_POLICY_TYPE:
            return Role(self.role_name)
        return None

    @property
    def permission(self) -> Union[str, None]:
        """Get the permission for this rule. If this is a role return None"""
        if self.policy_type == PERMISSION_POLICY_TYPE:
            return self.action
        return None
