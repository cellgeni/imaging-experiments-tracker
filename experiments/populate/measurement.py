import django

from experiments.populate.slide import SlidesPopulator

from experiments.models import *


class MeasurementsPrerequisitesPopulator:

    @classmethod
    def populate_projects(cls):
        Project.objects.get_or_create(name="ML_HEA")[0].save()
        Project.objects.get_or_create(name="KB_CAH")[0].save()

    @classmethod
    def populate_researchers(cls):
        Researcher.objects.get_or_create(
            last_name="Khodak", first_name="Anton", login="A_K")[0].save()
        Researcher.objects.get_or_create(
            last_name="Winslet", first_name="Mariam", login="M_W")[0].save()

    @classmethod
    def populate_technologies(cls):
        Technology.objects.get_or_create(name="RNAscope 4-plex")[0].save()
        Technology.objects.get_or_create(name="RNAscope 8-plex")[0].save()

    @classmethod
    def populate_plates(cls):
        Plate.objects.get_or_create(name="190711_182307-V")[0].save()
        Plate.objects.get_or_create(name="2342341-F")[0].save()

    @classmethod
    def populate_measurement_numbers(cls):
        MeasurementNumber.objects.get_or_create(name="1a")[0].save()
        MeasurementNumber.objects.get_or_create(name="1b")[0].save()

    @classmethod
    def populate_low_mag_references(cls):
        LowMagReference.objects.get_or_create(name="Reference")[0].save()
        LowMagReference.objects.get_or_create(name="1a")[0].save()

    @classmethod
    def populate_mag_bin_overlap(cls):
        MagBinOverlap.objects.get_or_create(
            name="10X_Bin2_5 % overlap")[0].save()
        MagBinOverlap.objects.get_or_create(
            name="20X_Bin1_7 % overlap")[0].save()

    @classmethod
    def populate_zplanes(cls):
        ZPlanes.objects.get_or_create(name="15x7")[0].save()
        ZPlanes.objects.get_or_create(name="10x2")[0].save()

    @classmethod
    def populate_team_dirs(cls):
        TeamDirectory.objects.get_or_create(name="t283_imaging")[0].save()
        TeamDirectory.objects.get_or_create(name="t876_imaging")[0].save()

    @classmethod
    def populate_locations(cls):
        ExportLocation.objects.get_or_create(
            name="0HarmonyExports\ML_HEA\ML_HEA_1")[0].save()
        ExportLocation.objects.get_or_create(
            name="0HarmonyExports\ML_HEA\ML_HEA_2")[0].save()
        ArchiveLocation.objects.get_or_create(
            name="0HarmonyArchives\ML_HEA\ML_HEA_1")[0].save()
        ArchiveLocation.objects.get_or_create(
            name="0HarmonyArchives\ML_HEA\ML_HEA_2")[0].save()

    @classmethod
    def populate_channels(cls):
        ch1 = Channel.objects.get_or_create(name="Atto 425")
        ch2 = Channel.objects.get_or_create(name="Opal 520")

    @classmethod
    def populate_targets(cls):
        t1 = Target.objects.get_or_create(name="MYH11")
        t2 = Target.objects.get_or_create(name="dapB")
        t3 = Target.objects.get_or_create(name="POLR2A")
        t4 = Target.objects.get_or_create(name="BNC1")
        t5 = Target.objects.get_or_create(name="TTN")
        t6 = Target.objects.get_or_create(name="KCNJ8")
        t7 = Target.objects.get_or_create(name="ACKR1")

    @classmethod
    def populate_channel_target_pairs(cls):
        cls.populate_channels()
        cls.populate_targets()
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

    @classmethod
    def populate_all_prerequisites(cls):
        cls.populate_projects()
        cls.populate_plates()
        cls.populate_researchers()
        cls.populate_technologies()
        cls.populate_team_dirs()
        cls.populate_locations()
        cls.populate_channel_target_pairs()
        cls.populate_measurement_numbers()
        cls.populate_low_mag_references()
        cls.populate_zplanes()
        cls.populate_mag_bin_overlap()
        sp = SlidesPopulator()
        sp.populate_all()


class MeasurementsPopulator:

    @staticmethod
    def get_sample_measurement() -> Measurement:
        """Create an instance of Measurement for testing."""
        p1 = Project.objects.first()
        researcher = Researcher.objects.first()
        t = Technology.objects.first()
        td = TeamDirectory.objects.first()
        mn1 = MeasurementNumber.objects.first()
        lmr1 = LowMagReference.objects.first()
        mbo1 = MagBinOverlap.objects.first()
        z1 = ZPlanes.objects.first()
        return Measurement(researcher=researcher,
                           project=p1,
                           technology=t,
                           image_cycle=1,
                           measurement_number=mn1,
                           low_mag_reference=lmr1,
                           mag_bin_overlap=mbo1,
                           z_planes=z1,
                           notes_1="Whole section; DAPI 520 570 650 // 425",
                           notes_2="Tissue section failed",
                           team_directory=td)

    @staticmethod
    def _create_automated_plate_slots(measurement: Measurement) -> None:
        """Create instances of Slots obtained through automated Phenix process for a given measurement for testing."""
        for slot_num in range(1, MAX_SLOTS + 1):
            automated_slide = AutomatedSlide.objects.get_or_create(name="sssss")[
                0]
            p = Slot.objects.get_or_create(measurement=measurement,
                                           automated_slide=automated_slide,
                                           automated_slide_num=slot_num)[0]
            slide = Slide.objects.first()
            for section in slide.section_set.all():
                p.sections.add(section)

    @classmethod
    def create_automated_measurement_with_multiple_slots(cls) -> Measurement:
        """Create a measurement for testing with instances of Slots obtained through automated Phenix process."""
        m = cls.get_sample_measurement()
        m.save()
        cls._create_automated_plate_slots(m)
        return m

    @staticmethod
    def _create_manual_plate_slots(measurement: Measurement) -> None:
        """Create instances of Slots obtained through manual processing for a given measurement for testing."""
        pass

    @classmethod
    def create_manual_measurement_with_multiple_slots(cls) -> Measurement:
        """Create a measurement for testing with instances of Slots obtained through manual imaging."""
        mn2 = MeasurementNumber.objects.last()
        m = cls.get_sample_measurement()
        m.measurement_number = mn2
        m.save()
        cls._create_manual_plate_slots(m)
        return m


if __name__ == "__main__":
    MeasurementsPrerequisitesPopulator.populate_all_prerequisites()
