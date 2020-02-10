import os, django

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaging_tracking.settings")
    django.setup()

from experiments.models import *
from experiments.populate.measurement import MeasurementsPopulator


class AnalysisPopulator:

    def __init__(self):
        m = MeasurementsPopulator()
        m.populate_all()

    def populate_pipelines(self):
        p = Pipeline.objects.get_or_create(name="stiching")[0]
        PipelineVersion.objects.get_or_create(name="1.0", pipeline=p)

    def populate_microscopes(self):
        Microscope.objects.get_or_create(name="Phenix_plateloader")
        Microscope.objects.get_or_create(name="Phenix")

    def populate_registrations(self):
        r = Registration.objects.get_or_create(reference_channel=Channel.objects.first())[0]
        m1 = Measurement.objects.first()
        m2 = Measurement.objects.last()
        assert m1 != m2
        r.measurements.add(m1)
        r.measurements.add(m2)

    def populate_stiching_zs(self):
        StichingZ.objects.get_or_create(name="Max_intensity")

    def populate_stichings(self):
        self.populate_stiching_zs()
        ch = Channel.objects.first()
        z = StichingZ.objects.first()
        Stiching.objects.get_or_create(reference_channel=ch, z=z)

    def populate_omero_projects(self):
        OmeroProject.objects.get_or_create(name="RV_END Endometrium epithelium - tissue")[0].save()

    def populate_omero_datasets(self):
        OmeroDataset.objects.get_or_create(name="WNT7A / NOTCH2 / NOTCH")[0].save()

    def populate_internal_groups(self):
        SangerGroup.objects.get_or_create(name="team 283")[0].save()

    def populate_internal_users(self):
        SangerUser.objects.get_or_create(name="at22")[0].save()
        SangerUser.objects.get_or_create(name="ak27")[0].save()

    def populate_external_users(self):
        ExternalUser.objects.get_or_create(email="pupkin@fastmail.com")[0].save()

    def populate_analyses_fields(self):
        self.populate_pipelines()
        self.populate_registrations()
        self.populate_stichings()
        self.populate_omero_projects()
        self.populate_omero_datasets()
        self.populate_internal_groups()
        self.populate_internal_users()
        self.populate_external_users()
        self.populate_microscopes()

    def populate_analyses(self):
        self.populate_analyses_fields()
        a1 = Analysis.objects.get_or_create(pipelineVersion=PipelineVersion.objects.first(),
                                            microscope=Microscope.objects.first(),
                                            registration=Registration.objects.first(),
                                            OMERO_project=OmeroProject.objects.first(),
                                            OMERO_DATASET=OmeroDataset.objects.first(),
                                            )[0]
        a1.stichings.add(Stiching.objects.first())
        a1.OMERO_internal_users.add(SangerUser.objects.first())
        a1.OMERO_internal_users.add(SangerUser.objects.last())
        a1.OMERO_external_users.add(ExternalUser.objects.first())
        a1.OMERO_internal_groups.add(SangerGroup.objects.first())


if __name__ == "__main__":
    ap = AnalysisPopulator()
    ap.populate_analyses()
