from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver

from experiments import auth
from experiments.constants import ExportStatus
from experiments.image_files_operations import ImagePathChecker
from experiments.models import Project, Measurement
from experiments.models.user import Profile


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


def create_roles_for_user(user: User) -> None:
    """Create a default role for all projects for this user."""
    for project in Project.objects.all():
        auth.add_role(user.id, project.id, user.profile.get_default_role())


def create_profile_if_not_present_in_user(user: User) -> None:
    """
    Check if user has a profile, if it does not create one for it.
    When a user is created from the admin interface and no Profile properties are set,
    django does not create a profile for that user.
    """
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)


@receiver(models.signals.post_save, sender=User)
def add_profile_and_roles_for_a_new_user(sender, instance, created, **kwargs):
    """Create profile for the user if not present and add roles all projects."""
    if created:
        create_profile_if_not_present_in_user(instance)
        create_roles_for_user(instance)


# @receiver(models.signals.post_save, sender=Measurement)
def check_image_file_paths_signal(sender, instance, *args, **kwargs):
    if instance.exported and instance.export_status in (ExportStatus.NOT_VERIFIED, ExportStatus.FILES_NOT_PRESENT):
        ipc = ImagePathChecker(instance)
        ipc.check_paths()
