from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin


class ImagingTrackingAdminSite(AdminSite):
    site_header = 'Imaging Experiments Tracker'


imaging_tracking_admin = ImagingTrackingAdminSite(name="admin")

imaging_tracking_admin.register(User, UserAdmin)
imaging_tracking_admin.register(Group)
