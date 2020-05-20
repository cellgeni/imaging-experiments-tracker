from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from experiments.models import *
from imaging_tracking.admin import imaging_tracking_admin
from experiments.models.slide import Slide, Section


class SampleAdmin(admin.ModelAdmin):
    model = Sample
    list_display = ["name", "tissue", "species", "age", "genotype", "background"]
    list_filter = ["tissue", "species", "age", "genotype", "background"]


class SectionInline(admin.StackedInline):
    model = Section


class SlideAdmin(admin.ModelAdmin):
    model = Slide
    list_display = ["barcode"]
    search_fields = ["barcode"]
    inlines = [SectionInline]


class MeasurementAdmin(admin.ModelAdmin):
    model = Measurement
    list_display = ["researcher", "project", "technology",
                    "plate", "image_cycle",
                    "date", "measurement_number", "export_location", "archive_location", "team_directory"]

    list_filter = ["researcher", "project", "technology", "date",
                   "low_mag_reference", "mag_bin_overlap", "z_planes"]
    search_fields = [
        "researcher__login", "technology__name", "project__name", "notes_1",
        "notes_2"]


class MeasurementInline(admin.StackedInline):
    model = Measurement


imaging_tracking_admin.register(Slide, SlideAdmin)
imaging_tracking_admin.register(Project)
imaging_tracking_admin.register(Technology)
imaging_tracking_admin.register(Researcher)
imaging_tracking_admin.register(Measurement, MeasurementAdmin)
imaging_tracking_admin.register(TeamDirectory)
imaging_tracking_admin.register(Sample, SampleAdmin)
imaging_tracking_admin.register(Channel)
imaging_tracking_admin.register(ChannelTarget)
imaging_tracking_admin.register(Target)
imaging_tracking_admin.register(Plate)
imaging_tracking_admin.register(Experiment)
imaging_tracking_admin.register(ExportLocation)
imaging_tracking_admin.register(ArchiveLocation)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    readonly_fields = ('api_token',)


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


class ProjectRolAdmin(admin.ModelAdmin):
    model = ProjectRole
    list_display = ["role", "project"]
    ordering = ["project__name"]


class PermissionAdmin(admin.ModelAdmin):
    model = Permission
    list_display = ["codename", "description"]
    ordering = ["codename"]


class RoleAdmin(admin.ModelAdmin):
    model = Role
    list_display = ["name", "role_permissions"]
    ordering = ["name"]

    def role_permissions(self, obj):
        return ', '.join([p.codename for p in obj.permissions.all()])


imaging_tracking_admin.unregister(User)
imaging_tracking_admin.register(User, CustomUserAdmin)
imaging_tracking_admin.register(Role, RoleAdmin)
imaging_tracking_admin.register(Permission, PermissionAdmin)
imaging_tracking_admin.register(ProjectRole, ProjectRolAdmin)
