from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from experiments.models.user import Profile


class ImagingTrackingAdminSite(AdminSite):
    site_header = 'Imaging Experiments Tracker'


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]


imaging_tracking_admin = ImagingTrackingAdminSite(name="admin")

imaging_tracking_admin.register(User, CustomUserAdmin)
imaging_tracking_admin.register(Group)
