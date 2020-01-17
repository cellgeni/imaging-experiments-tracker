import logging
import os
import uuid
from datetime import datetime

import pandas as pd
from django.test import TestCase

from experiments.constants import *
from experiments.models import Researcher, CellGenProject, \
    Slide, ChannelTarget, Technology, Measurement, TeamDirectory, \
    Section, Target, Channel
from experiments.populate import Populator
from experiments.xls.import_xls import SpreadsheetImporter, ImageTrackingRow
from experiments.xls.me import MeasurementM2MFields, MeasurementParameters
from experiments.xls.sample_row import SampleRow


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_sample_info():
    return {
        UUID: str(uuid.uuid4()),
        MODE: CREATE_OR_UPDATE,
        RESEARCHER: str(Researcher.objects.first()),
        PROJECT: str(CellGenProject.objects.first()),
        SLIDE_BARCODE: str(Slide.objects.first()),
        AUTOMATED_PLATEID: "smth",
        AUTOMATED_SLIDEN: "smhw",
        TECHNOLOGY: str(Technology.objects.first()),
        IMAGE_CYCLE: 1,
        CHANNEL_TARGET1: str(ChannelTarget.objects.all()[0]),
        CHANNEL_TARGET2: str(ChannelTarget.objects.all()[1]),
        CHANNEL_TARGET3: str(ChannelTarget.objects.all()[2]),
        DATE: str(datetime.now()),
        MEASUREMENT: 1,
        LOW_MAG_REFERENCE: "smth",
        MAG_BIN_OVERLAP: "smth",
        SECTIONS: "1,2",
        ZPLANES: "28x1",
        NOTES_1: "SMTH",
        NOTES_2: "SMTH",
        EXPORT_LOCATION: "/SDKJKJ/SDKJKJ",
        ARCHIVE_LOCATION: "/SDKJKJ/SDKJK421J",
        TEAM_DIR: str(TeamDirectory.objects.first()),
    }


class SampleRowTestCase(TestCase):
    file = 'test_data/measurements_input1.xlsx'

    def setUp(self):
        p = Populator()
        p.populate_all()
        assert Researcher.objects.first()

    def test_write_row(self):
        sample_info = get_sample_info()
        assert sample_info[RESEARCHER]
        row = SampleRow(sample_info)
        row.write_sample(self.file)
        df = pd.read_excel(self.file)
        for key, value in sample_info.items():
            spreadsheet_value = df.loc[0, key]
            logger.debug(f"Key: {key}")
            logger.debug(f"Original value: {value}")
            logger.debug(f"Spreadsheet value: {spreadsheet_value}")
            assert value == spreadsheet_value

    def tearDown(self) -> None:
        os.remove(self.file)


class RowMeasurementTestCase(TestCase):

    def setUp(self):
        p = Populator()
        p.populate_all()

    def test_create(self):
        sl1 = Slide.objects.get(automated_id="ML_HEA_007Q", barcode_id="S000000729")

        sc11 = Section.objects.get(number=1, slide=sl1)
        sc12 = Section.objects.get(number=2, slide=sl1)
        ch1 = Channel.objects.get(name="Atto 425")
        t1 = Target.objects.get(name="MYH11")
        t2 = Target.objects.get(name="dapB")
        t3 = Target.objects.get(name="POLR2A")
        cht1 = ChannelTarget.objects.get(channel=ch1, target=t1)
        cht2 = ChannelTarget.objects.get(channel=ch1, target=t2)
        cht3 = ChannelTarget.objects.get(channel=ch1, target=t3)
        model = Measurement(id=uuid.uuid4(),
                            researcher=Researcher.objects.first(),
                            technology=Technology.objects.first(),
                            image_cycle=1,
                            date=datetime.now(),
                            measurement="1b",
                            low_mag_reference="kjkj",
                            mag_bin_overlap="kjk",
                            notes_1="kj",
                            notes_2="kjkj",
                            export_location="kkk",
                            archive_location="kkk",
                            team_directory=TeamDirectory.objects.first())
        m2mfields = MeasurementM2MFields(sections=[sc11, sc12],
                                         channel_target_pairs=[cht1, cht2, cht3])
        parameters = MeasurementParameters(model, m2mfields)
        ImageTrackingRow.create(parameters)
        assert parameters.were_created()


class SpreadsheetImportTestCase(TestCase):
    file = 'test_data/measurements_input2.xlsx'

    def setUp(self):
        p = Populator()
        p.populate_all()

    def test_object_creation(self):
        row = SampleRow(get_sample_info())
        row.write_sample(self.file)
        si = SpreadsheetImporter(self.file)
        si.import_spreadsheet()
        assert row.is_in_database()

    def tearDown(self) -> None:
        os.remove(self.file)
