from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User

from experiments.models import Project, Profile
from experiments import auth


@receiver(models.signals.post_save, sender=Project)
def add_user_roles_to_new_project(sender, instance, created, *args, **kwargs):
    """Add new roles for all internal users for this newly created project."""
    if created:
        for user in User.objects.all():
            auth.add_role(user.id, instance.id,
                          user.profile.get_default_role())


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

def create_roles_for_user(user:User) -> None:
    for project in Project.objects.all():
        auth.add_role(user.id, project.id,
                        user.profile.get_default_role())

@receiver(models.signals.post_save, sender=User)
def add_profile_and_roles_for_a_new_user(sender, instance, created, **kwargs):
    """Create profile for the user if not present and add roles all projects."""
    if created:
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)
        create_roles_for_user(instance)
