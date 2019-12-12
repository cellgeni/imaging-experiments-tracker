from django.contrib import admin

from experiments.models import *
from image_tracking.admin import image_tracking_admin


class SectionInline(admin.StackedInline):
    model = Section


class SlideAdmin(admin.ModelAdmin):
    model = Slide
    inlines = [SectionInline]


class MeasurementAdmin(admin.ModelAdmin):
    model = Measurement
    # list_display = ["experiment__name", "slide__barcode_id", "technology", "measurement"]
    list_display = ["technology", "measurement"]
    list_filter = ("microscope",)


class MeasurementInline(admin.StackedInline):
    model = Measurement


class ExperimentAdmin(admin.ModelAdmin):
    model = Experiment
    inlines = [MeasurementInline]
    list_display = ["name", "project", "team_directory"]
    search_fields = ['slide__barcode_id', "name"]


image_tracking_admin.register(Slide, SlideAdmin)
image_tracking_admin.register(CellGenProject)
image_tracking_admin.register(Section)
image_tracking_admin.register(Technology)
image_tracking_admin.register(Microscope)
image_tracking_admin.register(Researcher)
image_tracking_admin.register(Measurement, MeasurementAdmin)
image_tracking_admin.register(TeamDirectory)
image_tracking_admin.register(Sample)
image_tracking_admin.register(Channel)
image_tracking_admin.register(Target)
image_tracking_admin.register(Experiment, ExperimentAdmin)
