from django.contrib import admin

from experiments.analysis import submit_analysis
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
    list_display = ["barcode_id"]
    search_fields = ["barcode_id"]
    inlines = [SectionInline]


class MeasurementAdmin(admin.ModelAdmin):
    model = Measurement
    actions = ['copy_measurement']
    list_display = ["uuid", "researcher", "experiment", "technology", "automated_slide_id",
                    "automated_plate_id", "automated_slide_num", "image_cycle",
                    "date", "measurement", "low_mag_reference", "mag_bin_overlap", "z_planes",
                    "notes_1", "notes_2", "export_location", "archive_location", "team_directory"]
    list_filter = ["researcher", "experiment", "technology", "automated_slide_id", "date",
                   "low_mag_reference", "mag_bin_overlap", "z_planes"]
    search_fields = ["uuid"]

    def copy_measurement(self, request, queryset):
        for obj in queryset:
            sections = obj.sections.all()
            channel_target_pairs = obj.channel_target_pairs.all()
            obj.pk = None
            obj.save()
            obj.sections.set(sections)
            obj.channel_target_pairs.set(channel_target_pairs)

    copy_measurement.short_description = "Copy measurement"


class MeasurementInline(admin.StackedInline):
    model = Measurement


class ExperimentAdmin(admin.ModelAdmin):
    model = Experiment
    inlines = [MeasurementInline]
    list_display = ["name", "project"]
    search_fields = ['slide__barcode_id', "name"]


class AnalysisAdmin(admin.ModelAdmin):
    model = Analysis
    actions = ['start']
    list_display = ["pk", "submitted_on", "status"]

    def start(self, request, queryset):
        for obj in queryset:
            submit_analysis(obj)
        message = f"{len(queryset)} analyses started. "
        self.message_user(request, message)

    start.short_description = "Start analysis"


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
imaging_tracking_admin.register(PipelineVersion)
imaging_tracking_admin.register(Registration)
imaging_tracking_admin.register(Stiching)
imaging_tracking_admin.register(OmeroDataset)
imaging_tracking_admin.register(OmeroProject)
imaging_tracking_admin.register(SangerGroup)
imaging_tracking_admin.register(SangerUser)
imaging_tracking_admin.register(ExternalUser)
imaging_tracking_admin.register(Analysis, AnalysisAdmin)
