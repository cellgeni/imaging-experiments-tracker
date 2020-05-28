from django.db import models


class CasbinRule(models.Model):
    """Currently not used for anything, just mapped in case we need to access
    casbin_rules directly from the database"""
    ptype = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(
        db_column="v0", max_length=255, blank=True, null=True)
    instance_id = models.CharField(
        db_column="v1", max_length=255, blank=True, null=True)
    action = models.CharField(
        db_column="v2", max_length=255, blank=True, null=True)
    v3 = models.CharField(max_length=255, blank=True, null=True)
    v4 = models.CharField(max_length=255, blank=True, null=True)
    v5 = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'casbin_rule'
        unique_together = ['ptype', 'user_id', 'instance_id', 'action']
