from django.contrib.admin import AdminSite


class ImageTrackingAdminSite(AdminSite):
    site_header = 'Imaging Experiments Tracker'


image_tracking_admin = ImageTrackingAdminSite(name="admin")
