from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver

from experiments import auth
from experiments.models import Project
from experiments.models.user import Profile


@receiver(models.signals.post_save, sender=Project)
def add_user_roles_to_new_project(sender, instance, created, *args, **kwargs):
    """Add new roles for all internal users for this newly created project."""
    if created:
        for user in User.objects.all():
            auth.add_role(user.id, instance.id, user.profile.get_default_role())


@receiver(models.signals.post_delete, sender=Project)
def delete_user_roles_after_deleting_a_project(sender, instance, *args, **kwargs):
    """Delete all roles attached to a deleted project."""
    for user in User.objects.all():
        auth.remove_existing_role(user.id, instance.id)


@receiver(models.signals.post_delete, sender=User)
def delete_user_roles_after_deleting_a_user(sender, instance, *args, **kwargs):
    """Delete all roles for a deleted user attached to any project."""
    for project in Project.objects.all():
        auth.remove_existing_role(instance.id, project.id)


@receiver(models.signals.post_save, sender=User)
def create_user_profile_signal(sender, instance, created, **kwargs):
    """Create Profile for every new User."""
    if created:
        Profile.objects.create(user=instance)


@receiver(models.signals.post_save, sender=User)
def add_roles_to_all_projects_for_a_new_user(sender, instance, created, *args, **kwargs):
    """Add new roles for all projects for a newly created user."""
    if created:
        for project in Project.objects.all():
            auth.add_role(instance.id, project.id, instance.profile.get_default_role())
