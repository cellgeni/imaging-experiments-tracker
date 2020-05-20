import hashlib
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from experiments.models.base import NameModel
from experiments.models import Project
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    is_external = models.BooleanField(
        verbose_name="External user?", default=False)
    roles = models.ManyToManyField(
        verbose_name="Roles in projects", to="experiments.ProjectRole")
    api_token = models.CharField(
        'API token', max_length=40, default=None, null=True)

    def generate_api_token(self):
        self.api_token = hashlib.sha1(
            f"{self.user.username}{datetime.now()}").hexdigest()

    def has_perm_for(self, permission, project):
        """Checks if this user has a particular permission or a particular project."""
        if isinstance(project, Project):
            project = project.name
        for pr in self.roles.all():
            if permission in [p.codename for p in pr.role.permissions.all()] and pr.project.name == project:
                return True
        return False

    def get_projects(self, permission=None):
        """Gets projects this user has any permissions for or projects with a particular permission if given."""
        if permission is None:
            return [pr.project for pr in self.roles.all()]
        else:
            return [pr.project for pr in self.roles.all() if self.has_perm_for(
                permission, pr.project.name)]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class ProjectRole(models.Model):
    role = models.ForeignKey(
        to='experiments.Role', on_delete=models.CASCADE)
    project = models.ForeignKey(
        to='experiments.Project', on_delete=models.CASCADE)

    class Meta():
        unique_together = ['role', 'project']

    def __str__(self):
        return f"{self.project.name} - {self.role.name}"


class Role(NameModel):
    permissions = models.ManyToManyField(to='experiments.Permission')


class Permission(models.Model):
    codename = models.CharField(max_length=30, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.codename
