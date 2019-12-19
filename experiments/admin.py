from django.contrib import admin

from experiments.models import *
from imaging_tracking.admin import imaging_tracking_admin


class SampleAdmin(admin.ModelAdmin):
    model = Sample
    list_display = ["id", "tissue", "species", "age", "genotype", "background"]
    list_filter = ["tissue", "species", "age", "genotype", "background"]


class SectionInline(admin.StackedInline):
    model = Section


class SlideAdmin(admin.ModelAdmin):
    model = Slide
    list_display = ["barcode_id", "automated_id"]
    search_fields = ["barcode_id", "automated_id"]
    inlines = [SectionInline]


class MeasurementAdmin(admin.ModelAdmin):
    model = Measurement
    # list_display = ["experiment__name", "slide__barcode_id", "technology", "measurement"]
    list_display = ["technology", "measurement", "team_directory"]


class MeasurementInline(admin.StackedInline):
    model = Measurement


class ExperimentAdmin(admin.ModelAdmin):
    model = Experiment
    inlines = [MeasurementInline]
    list_display = ["name", "project"]
    search_fields = ['slide__barcode_id', "name"]


imaging_tracking_admin.register(Slide, SlideAdmin)
imaging_tracking_admin.register(CellGenProject)
imaging_tracking_admin.register(Technology)
imaging_tracking_admin.register(Microscope)
imaging_tracking_admin.register(Researcher)
imaging_tracking_admin.register(Measurement, MeasurementAdmin)
imaging_tracking_admin.register(TeamDirectory)
imaging_tracking_admin.register(Sample, SampleAdmin)
imaging_tracking_admin.register(Channel)
imaging_tracking_admin.register(Target)
imaging_tracking_admin.register(Experiment, ExperimentAdmin)
