import os, django

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaging_tracking.settings")
# django.setup()
from experiments.models import *


def save(arr):
    for a in arr:
        a[0].save()


class Populator:

    def populate_cellgen_project(self):
        CellGenProject.objects.get_or_create(key="ML_HEA")[0].save()

    def populate_researchers(self):
        Researcher.objects.get_or_create(last_name="Khodak", first_name="Anton", employee_key="A_K")[0].save()

    def populate_tissues(self):
        Tissue.objects.get_or_create(name="Kidney")[0].save()
        Tissue.objects.get_or_create(name="Adrenal gland")[0].save()

    def populate_microscopes(self):
        Microscope.objects.get_or_create(name="Phenix_PlateLoader")[0].save()
        Microscope.objects.get_or_create(name="Phenix")[0].save()

    def populate_technologies(self):
        Technology.objects.get_or_create(name="RNAscope 4-plex")[0].save()

    def populate_team_dirs(self):
        TeamDirectory.objects.get_or_create(name="t283_imaging")[0].save()

    def populate_channels(self):
        ch1 = Channel.objects.get_or_create(name="Atto 425")
        ch2 = Channel.objects.get_or_create(name="Opal 520")
        save({ch1, ch2})

    def populate_targets(self):
        t1 = Target.objects.get_or_create(name="MYH11")
        t2 = Target.objects.get_or_create(name="dapB")
        t3 = Target.objects.get_or_create(name="POLR2A")
        t4 = Target.objects.get_or_create(name="BNC1")
        t5 = Target.objects.get_or_create(name="TTN")
        t6 = Target.objects.get_or_create(name="KCNJ8")
        t7 = Target.objects.get_or_create(name="ACKR1")
        save({t1, t2, t3, t4, t5, t6, t7})

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
        save({cht1, cht2, cht3, cht4, cht5, cht6})

    def populate_samples(self):
        self.populate_tissues()
        t1 = Tissue.objects.get(name="Kidney")
        t2 = Tissue.objects.get(name="Adrenal gland")
        s1 = Sample.objects.get_or_create(id="L14-KID-0-FFPE-1-S3i",
                                          species="human",
                                          age="Adult",
                                          genotype="Unknown",
                                          background="Unknown",
                                          tissue=t1)
        s2 = Sample.objects.get_or_create(id="L14-ADR-0-FFPE-1-S3i",
                                          species="human",
                                          age="Adult",
                                          genotype="Unknown",
                                          background="Unknown",
                                          tissue=t2)
        save({s1, s2})

    def populate_slides(self):
        s1 = Slide.objects.get_or_create(automated_id="ML_HEA_007Q", barcode_id="S000000729")
        s2 = Slide.objects.get_or_create(automated_id="ML_HEA_007R", barcode_id="S000000724")
        s3 = Slide.objects.get_or_create(automated_id="ML_HEA_007S", barcode_id="S000000725")
        s4 = Slide.objects.get_or_create(automated_id="ML_HEA_007P", barcode_id="S000000726")
        save({s1, s2, s3, s4})

    def populate_sections(self):
        self.populate_samples()
        self.populate_slides()
        s1 = Sample.objects.get(id="L14-KID-0-FFPE-1-S3i")
        s2 = Sample.objects.get(id="L14-ADR-0-FFPE-1-S3i")
        sl1 = Slide.objects.get(automated_id="ML_HEA_007Q", barcode_id="S000000729")
        sl2 = Slide.objects.get(automated_id="ML_HEA_007R", barcode_id="S000000724")
        sc11 = Section.objects.get_or_create(number=1, sample=s1, slide=sl1)
        sc12 = Section.objects.get_or_create(number=2, sample=s1, slide=sl1)
        sc13 = Section.objects.get_or_create(number=3, sample=s1, slide=sl1)
        sc21 = Section.objects.get_or_create(number=1, sample=s2, slide=sl2)
        sc22 = Section.objects.get_or_create(number=2, sample=s2, slide=sl2)
        save({sc11, sc12, sc13, sc21, sc22})

    def populate_experiment(self):
        project = CellGenProject.objects.get(key="ML_HEA")
        Experiment.objects.get_or_create(name="20191220_ob5_kidney", project=project)[0].save()

    def populate_measurements(self):
        e = Experiment.objects.get(name="20191220_ob5_kidney")
        researcher = Researcher.objects.get(employee_key="A_K")
        sl1 = Slide.objects.get(automated_id="ML_HEA_007Q", barcode_id="S000000729")
        sl2 = Slide.objects.get(automated_id="ML_HEA_007R", barcode_id="S000000724")

        t = Technology.objects.get(name="RNAscope 4-plex")
        td = TeamDirectory.objects.get(name="t283_imaging")

        m1 = Measurement.objects.get_or_create(researcher=researcher,
                                               experiment=e,
                                               technology=t,
                                               automated_plate_id="191010_174405-V",
                                               automated_slide_num=1,
                                               image_cycle=1,
                                               measurement="1b",
                                               low_mag_reference="1a",
                                               mag_bin_overlap="20X_Bin1_7%overlap",
                                               z_planes="28*1",
                                               notes_1="Whole section; DAPI 520 570 650 // 425",
                                               notes_2="Tissue section failed",
                                               team_directory=td)
        m2 = Measurement.objects.get_or_create(researcher=researcher,
                                               experiment=e,
                                               technology=t,
                                               automated_plate_id="191010_174402-V",
                                               automated_slide_num=1,
                                               image_cycle=1,
                                               measurement="1a",
                                               low_mag_reference="1b",
                                               mag_bin_overlap="20X_Bin1_7%overlap",
                                               z_planes="28*1",
                                               notes_1="Whole section; DAPI 520 570 650 // 425",
                                               notes_2="Tissue section failed",
                                               team_directory=td)
        m3 = Measurement.objects.get_or_create(researcher=researcher,
                                               experiment=e,
                                               technology=t,
                                               automated_plate_id="191010_174401-V",
                                               automated_slide_num=1,
                                               image_cycle=1,
                                               measurement="4b",
                                               low_mag_reference="1b",
                                               mag_bin_overlap="20X_Bin1_7%overlap",
                                               z_planes="25*1",
                                               notes_1="Whole section; DAPI 520 570 650 // 425",
                                               notes_2="Tissue section failed",
                                               team_directory=td)
        save({m1, m2, m3})

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
        self.populate_measurements()


if __name__ == "__main__":
    p = Populator()
    p.populate_all()
