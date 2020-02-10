import os, django

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaging_tracking.settings")
    django.setup()
from experiments.models import *


class MeasurementsPopulator:

    def populate_cellgen_project(self):
        CellGenProject.objects.get_or_create(key="ML_HEA")[0].save()
        CellGenProject.objects.get_or_create(key="KB_CAH")[0].save()

    def populate_researchers(self):
        Researcher.objects.get_or_create(last_name="Khodak", first_name="Anton", employee_key="A_K")[0].save()
        Researcher.objects.get_or_create(last_name="Winslet", first_name="Mariam", employee_key="M_W")[0].save()

    def populate_tissues(self):
        Tissue.objects.get_or_create(name="Kidney")[0].save()
        Tissue.objects.get_or_create(name="Adrenal gland")[0].save()

    def populate_species(self):
        Tissue.objects.get_or_create(name="Kidney")[0].save()
        Tissue.objects.get_or_create(name="Adrenal gland")[0].save()

    def populate_microscopes(self):
        Microscope.objects.get_or_create(name="Phenix_PlateLoader")[0].save()
        Microscope.objects.get_or_create(name="Phenix")[0].save()

    def populate_technologies(self):
        Technology.objects.get_or_create(name="RNAscope 4-plex")[0].save()
        Technology.objects.get_or_create(name="RNAscope 8-plex")[0].save()

    def populate_measurement_numbers(self):
        MeasurementNumber.objects.get_or_create(name="1a")[0].save()
        MeasurementNumber.objects.get_or_create(name="1b")[0].save()

    def populate_low_mag_references(self):
        LowMagReference.objects.get_or_create(name="Reference")[0].save()
        LowMagReference.objects.get_or_create(name="1a")[0].save()

    def populate_mag_bin_overlap(self):
        MagBinOverlap.objects.get_or_create(name="10X_Bin2_5 % overlap")[0].save()
        MagBinOverlap.objects.get_or_create(name="20X_Bin1_7 % overlap")[0].save()

    def populate_zplanes(self):
        ZPlanes.objects.get_or_create(name="15x7")[0].save()
        ZPlanes.objects.get_or_create(name="10x2")[0].save()

    def populate_team_dirs(self):
        TeamDirectory.objects.get_or_create(name="t283_imaging")[0].save()
        TeamDirectory.objects.get_or_create(name="t876_imaging")[0].save()

    def populate_channels(self):
        ch1 = Channel.objects.get_or_create(name="Atto 425")
        ch2 = Channel.objects.get_or_create(name="Opal 520")

    def populate_targets(self):
        t1 = Target.objects.get_or_create(name="MYH11")
        t2 = Target.objects.get_or_create(name="dapB")
        t3 = Target.objects.get_or_create(name="POLR2A")
        t4 = Target.objects.get_or_create(name="BNC1")
        t5 = Target.objects.get_or_create(name="TTN")
        t6 = Target.objects.get_or_create(name="KCNJ8")
        t7 = Target.objects.get_or_create(name="ACKR1")

    def populate_channel_target_pairs(self):
        self.populate_channels()
        self.populate_targets()
        ch1 = Channel.objects.get(name="Atto 425")
        ch2 = Channel.objects.get(name="Opal 520")
        t1 = Target.objects.get(name="MYH11")
        t2 = Target.objects.get(name="dapB")
        t3 = Target.objects.get(name="POLR2A")
        cht1 = ChannelTarget.objects.get_or_create(channel=ch1, target=t1)
        cht2 = ChannelTarget.objects.get_or_create(channel=ch1, target=t2)
        cht3 = ChannelTarget.objects.get_or_create(channel=ch1, target=t3)
        cht4 = ChannelTarget.objects.get_or_create(channel=ch2, target=t1)
        cht5 = ChannelTarget.objects.get_or_create(channel=ch2, target=t2)
        cht6 = ChannelTarget.objects.get_or_create(channel=ch2, target=t3)

    def populate_samples(self):
        self.populate_tissues()
        t1 = Tissue.objects.get(name="Kidney")
        t2 = Tissue.objects.get(name="Adrenal gland")
        s1 = Sample.objects.get_or_create(id="L14-KID-0-FFPE-1-S3i",
                                          species=1,
                                          age="Adult",
                                          genotype="Unknown",
                                          background="Unknown",
                                          tissue=t1)
        s2 = Sample.objects.get_or_create(id="L14-ADR-0-FFPE-1-S3i",
                                          species=2,
                                          age="Adult",
                                          genotype="Unknown",
                                          background="Unknown",
                                          tissue=t2)

    def populate_slides(self):
        s1 = Slide.objects.get_or_create(barcode_id="S000000729")
        s2 = Slide.objects.get_or_create(barcode_id="S000000724")
        s3 = Slide.objects.get_or_create(barcode_id="S000000725")
        s4 = Slide.objects.get_or_create(barcode_id="S000000726")

    def populate_sections(self):
        self.populate_samples()
        self.populate_slides()
        s1 = Sample.objects.get(id="L14-KID-0-FFPE-1-S3i")
        s2 = Sample.objects.get(id="L14-ADR-0-FFPE-1-S3i")
        sl1 = Slide.objects.get(barcode_id="S000000729")
        sl2 = Slide.objects.get(barcode_id="S000000724")
        sc11 = Section.objects.get_or_create(number=1, sample=s1, slide=sl1)
        sc12 = Section.objects.get_or_create(number=2, sample=s1, slide=sl1)
        sc13 = Section.objects.get_or_create(number=3, sample=s1, slide=sl1)
        sc21 = Section.objects.get_or_create(number=1, sample=s2, slide=sl2)
        sc22 = Section.objects.get_or_create(number=2, sample=s2, slide=sl2)

    def populate_experiment(self):
        project = CellGenProject.objects.get(key="ML_HEA")
        Experiment.objects.get_or_create(name="20191220_ob5_kidney", project=project)[0].save()

    def populate_measurements(self):
        self.populate_measurement_numbers()
        self.populate_low_mag_references()
        self.populate_zplanes()
        self.populate_mag_bin_overlap()
        e = Experiment.objects.get(name="20191220_ob5_kidney")
        researcher = Researcher.objects.get(employee_key="A_K")
        sl1 = Slide.objects.get(barcode_id="S000000729")
        sl2 = Slide.objects.get(barcode_id="S000000724")

        t = Technology.objects.get(name="RNAscope 4-plex")
        td = TeamDirectory.objects.get(name="t283_imaging")

        mn1 = MeasurementNumber.objects.get(name="1a")
        mn2 = MeasurementNumber.objects.get(name="1b")
        lmr1 = LowMagReference.objects.first()
        lmr2 = LowMagReference.objects.last()
        mbo1 = MagBinOverlap.objects.first()
        mbo2 = MagBinOverlap.objects.last()
        z1 = ZPlanes.objects.first()
        z2 = ZPlanes.objects.last()
        m1 = Measurement.objects.get_or_create(researcher=researcher,
                                               experiment=e,
                                               technology=t,
                                               automated_slide_id="TM_RCC_00FZ",
                                               automated_plate_id="191010_174405-V",
                                               automated_slide_num=1,
                                               image_cycle=1,
                                               measurement=mn1,
                                               low_mag_reference=lmr1,
                                               mag_bin_overlap=mbo1,
                                               z_planes=z1,
                                               notes_1="Whole section; DAPI 520 570 650 // 425",
                                               notes_2="Tissue section failed",
                                               team_directory=td)
        m2 = Measurement.objects.get_or_create(researcher=researcher,
                                               experiment=e,
                                               technology=t,
                                               automated_slide_id="TM_RCC_00FW",
                                               automated_plate_id="191010_174402-V",
                                               automated_slide_num=1,
                                               image_cycle=1,
                                               measurement=mn2,
                                               low_mag_reference=lmr2,
                                               mag_bin_overlap=mbo2,
                                               z_planes=z2,
                                               notes_1="Whole section; DAPI 520 570 650 // 425",
                                               notes_2="Tissue section failed",
                                               team_directory=td)
        m3 = Measurement.objects.get_or_create(researcher=researcher,
                                               experiment=e,
                                               technology=t,
                                               automated_slide_id="TM_RCC_00FR",
                                               automated_plate_id="191010_174401-V",
                                               automated_slide_num=1,
                                               image_cycle=1,
                                               measurement=mn1,
                                               low_mag_reference=lmr2,
                                               mag_bin_overlap=mbo2,
                                               z_planes=z1,
                                               notes_1="Whole section; DAPI 520 570 650 // 425",
                                               notes_2="Tissue section failed",
                                               team_directory=td)

        ch1 = Channel.objects.get(name="Atto 425")
        ch2 = Channel.objects.get(name="Opal 520")

        t1 = Target.objects.get(name="MYH11")
        t2 = Target.objects.get(name="dapB")
        t3 = Target.objects.get(name="POLR2A")
        cht1 = ChannelTarget.objects.get(channel=ch1, target=t1)
        cht2 = ChannelTarget.objects.get(channel=ch1, target=t2)
        cht3 = ChannelTarget.objects.get(channel=ch1, target=t3)
        cht4 = ChannelTarget.objects.get(channel=ch2, target=t1)
        cht5 = ChannelTarget.objects.get(channel=ch2, target=t2)
        cht6 = ChannelTarget.objects.get(channel=ch2, target=t3)

        m1[0].channel_target_pairs.add(cht1)
        m1[0].channel_target_pairs.add(cht2)
        m1[0].channel_target_pairs.add(cht3)
        m3[0].channel_target_pairs.add(cht1)
        m3[0].channel_target_pairs.add(cht2)
        m3[0].channel_target_pairs.add(cht3)
        m2[0].channel_target_pairs.add(cht4)
        m2[0].channel_target_pairs.add(cht5)
        m2[0].channel_target_pairs.add(cht6)

        sc11 = Section.objects.get(number=1, slide=sl1)
        sc12 = Section.objects.get(number=2, slide=sl1)
        sc13 = Section.objects.get(number=3, slide=sl1)
        sc21 = Section.objects.get(number=1, slide=sl2)
        sc22 = Section.objects.get(number=2, slide=sl2)

        m1[0].sections.add(sc11)
        m1[0].sections.add(sc12)
        m1[0].sections.add(sc13)
        m2[0].sections.add(sc21)
        m2[0].sections.add(sc22)
        m3[0].sections.add(sc21)

    def populate_all(self):
        self.populate_cellgen_project()
        self.populate_researchers()
        self.populate_microscopes()
        self.populate_technologies()
        self.populate_team_dirs()
        self.populate_samples()
        self.populate_slides()
        self.populate_channel_target_pairs()
        self.populate_sections()
        self.populate_experiment()
        self.populate_measurement_numbers()
        self.populate_low_mag_references()
        self.populate_zplanes()
        self.populate_mag_bin_overlap()
        self.populate_measurements()


if __name__ == "__main__":
    p = MeasurementsPopulator()
    p.populate_all()
