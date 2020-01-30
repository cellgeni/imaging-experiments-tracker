import logging
import os
import uuid
import datetime
from typing import Dict

import pandas as pd
from django.test import TestCase

from experiments.constants import *
from experiments.models.measurement import *
from experiments.populate import Populator
from experiments.xls.excel_row import ExcelRow
from experiments.xls.import_xls import SpreadsheetImporter, MeasurementRow
from experiments.xls.measurement_parameters import MeasurementM2MFields, MeasurementParameters
from experiments.xls import StreamLogging, xls_logger
from experiments.xls.measurement_parameters import MeasurementParametersParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExcelRowInfoGenerator:

    def __init__(self, d: Dict):
        self.d = d

    @staticmethod
    def get_todays_date():
        return datetime.date.today().strftime(Measurement.DATE_FORMAT)

    @classmethod
    def get_sample_info(cls) -> Dict:
        return {
            UUID: str(uuid.uuid4()),
            MODE: CREATE_OR_UPDATE,
            RESEARCHER: str(Researcher.objects.first()),
            PROJECT: str(CellGenProject.objects.first()),
            SLIDE_BARCODE: str(Slide.objects.first()),
            AUTOMATED_PLATEID: "smth",
            AUTOMATED_SLIDEN: 2,
            TECHNOLOGY: str(Technology.objects.first()),
            IMAGE_CYCLE: 1,
            CHANNEL_TARGET1: str(ChannelTarget.objects.all()[0]),
            CHANNEL_TARGET2: str(ChannelTarget.objects.all()[1]),
            CHANNEL_TARGET3: str(ChannelTarget.objects.all()[2]),
            DATE: cls.get_todays_date(),
            MEASUREMENT: str(MeasurementNumber.objects.first()),
            LOW_MAG_REFERENCE: str(LowMagReference.objects.first()),
            MAG_BIN_OVERLAP: str(MagBinOverlap.objects.first()),
            SECTIONS: "1,2",
            ZPLANES: str(ZPlanes.objects.first()),
            NOTES_1: "SMTH",
            NOTES_2: "SMTH",
            EXPORT_LOCATION: "/SDKJKJ/SDKJKJ",
            ARCHIVE_LOCATION: "/SDKJKJ/SDKJK421J",
            TEAM_DIR: str(TeamDirectory.objects.first()),
        }

    def get_info(self) -> Dict:
        result = {
            UUID: str(uuid.uuid4()),
            MODE: CREATE_OR_UPDATE,
        }
        result.update(self.d)
        return result

    def create_row(self) -> pd.Series:
        return pd.Series(self.get_info())


class ExcelRowTestCase(TestCase):
    file = 'test_data/measurements_input1.xlsx'

    def setUp(self) -> None:
        p = Populator()
        p.populate_all()
        self.assertTrue(Researcher.objects.first())

    def test_write_row(self) -> None:
        sample_info = ExcelRowInfoGenerator.get_sample_info()
        self.assertTrue(sample_info[RESEARCHER])
        row = ExcelRow(sample_info)
        row.write_sample(self.file)
        df = pd.read_excel(self.file)
        for key, value in sample_info.items():
            spreadsheet_value = df.loc[0, key]
            logger.debug(f"Key: {key}")
            logger.debug(f"Original value: {value}")
            logger.debug(f"Spreadsheet value: {spreadsheet_value}")
            self.assertEqual(value, spreadsheet_value)

    def tearDown(self) -> None:
        os.remove(self.file)


class MeasurementsParameterParserTestCase(TestCase):

    def setUp(self) -> None:
        p = Populator()
        p.populate_sections()
        p.populate_channel_target_pairs()

    def test_parse_sections(self):
        slide = Slide.get_random_slide_with_three_sections()
        info = {
            SLIDE_BARCODE: str(slide),
            SECTIONS: "1,3",
        }
        row = ExcelRowInfoGenerator(info).create_row()
        mpp = MeasurementParametersParser(row)
        section1 = Section.objects.get(number=1, slide=slide)
        section3 = Section.objects.get(number=3, slide=slide)
        self.assertEqual(mpp._parse_sections(), {section1, section3})

    def test_parse_channel_targets(self):
        cht1 = ChannelTarget.objects.all()[0]
        cht2 = ChannelTarget.objects.all()[1]
        cht3 = ChannelTarget.objects.all()[2]
        info = {
            CHANNEL_TARGET1: str(cht1),
            CHANNEL_TARGET2: str(cht2),
            CHANNEL_TARGET3: str(cht3),
        }
        row = ExcelRowInfoGenerator(info).create_row()
        mpp = MeasurementParametersParser(row)
        self.assertEqual(mpp._parse_channel_targets(), {cht1, cht2, cht3})

    def test_parse_section_numbers(self):
        self.assertEqual([1, 2, 3], MeasurementParametersParser._parse_section_numbers("1,2,3"))
        self.assertEqual([1, 2, 3], MeasurementParametersParser._parse_section_numbers("1, 2, 3"))
        self.assertEqual([1, 2, 3], MeasurementParametersParser._parse_section_numbers("1 , 2 ,3"))
        self.assertEqual([1], MeasurementParametersParser._parse_section_numbers("1"))
        self.assertEqual([1, 2], MeasurementParametersParser._parse_section_numbers("1.0, 2.0"))
        self.assertEqual([1], MeasurementParametersParser._parse_section_numbers(1))
        self.assertEqual([1], MeasurementParametersParser._parse_section_numbers(float(1.0)))
        with self.assertRaises(ValueError):
            MeasurementParametersParser._parse_section_numbers("cat, dog, 2")

    def test_parse_date(self):
        sample_date = datetime.date(2019, 2, 2)
        self.assertEqual(sample_date, MeasurementParametersParser._parse_date("2.2.2019"))
        self.assertEqual(sample_date, MeasurementParametersParser._parse_date("02/02/2019"))
        wrong_dates = ["1.13.2018", "some word", "1.2.18", "1 02 2019", "2019.12.3", '0.0', 0.0, 0]
        for wrong_date in wrong_dates:
            with self.assertRaises(ValueError):
                MeasurementParametersParser._parse_date(wrong_date)


class MeasurementParametersGenerator:

    @staticmethod
    def get_sample_parameters() -> MeasurementParameters:
        sl1 = Slide.objects.get(automated_id="ML_HEA_007Q", barcode_id="S000000729")

        sc11 = Section.objects.get(number=1, slide=sl1)
        sc12 = Section.objects.get(number=2, slide=sl1)
        cht1 = ChannelTarget.objects.all()[0]
        cht2 = ChannelTarget.objects.all()[1]
        cht3 = ChannelTarget.objects.all()[2]
        model = Measurement(researcher=Researcher.objects.first(),
                            automated_plate_id="kkjk",
                            automated_slide_num="N/A",
                            technology=Technology.objects.first(),
                            image_cycle=1,
                            date=datetime.date.today(),
                            measurement=MeasurementNumber.objects.get(name="1b"),
                            low_mag_reference=LowMagReference.objects.first(),
                            mag_bin_overlap=MagBinOverlap.objects.first(),
                            z_planes=ZPlanes.objects.first(),
                            notes_1="kj",
                            notes_2="kjkj",
                            export_location="kkk",
                            archive_location="kkk",
                            team_directory=TeamDirectory.objects.first())
        m2mfields = MeasurementM2MFields(sections={sc11, sc12},
                                         channel_target_pairs={cht1, cht2, cht3})
        return MeasurementParameters(model, m2mfields)


class MeasurementParametersTestCase(TestCase):

    def setUp(self):
        p = Populator()
        p.populate_all()

    def test_update_fields(self):
        parameters = MeasurementParametersGenerator.get_sample_parameters()
        uuid = parameters.create_db_object()
        self.assertTrue(parameters.were_created())
        sl1 = Slide.objects.first()
        sl2 = Slide.objects.last()
        self.assertNotEqual(sl1, sl2)
        sc11 = Section.objects.get(number=1, slide=sl1)
        sc12 = Section.objects.get(number=2, slide=sl2)
        cht1 = ChannelTarget.objects.all()[1]
        cht5 = ChannelTarget.objects.all()[5]
        model = Measurement(uuid=uuid,
                            researcher=Researcher.objects.last(),
                            technology=Technology.objects.last(),
                            image_cycle=1,
                            date=datetime.date(2019, 3, 4),
                            measurement=MeasurementNumber.objects.get(name="1a"),
                            low_mag_reference=LowMagReference.objects.last(),
                            mag_bin_overlap=MagBinOverlap.objects.last(),
                            z_planes=ZPlanes.objects.last(),
                            notes_1="kj",
                            notes_2="kjkj",
                            export_location="kkk",
                            archive_location="kkk",
                            team_directory=TeamDirectory.objects.first())
        m2mfields = MeasurementM2MFields(sections={sc11, sc12},
                                         channel_target_pairs={cht1, cht5})
        new_parameters = MeasurementParameters(model, m2mfields)
        new_parameters.update_db_object()
        self.assertTrue(new_parameters.were_created())
        self.assertFalse(parameters.were_created())


class MeasurementRowTestCase(TestCase):

    def setUp(self):
        p = Populator()
        p.populate_all()

    def test_create(self):
        parameters = MeasurementParametersGenerator.get_sample_parameters()
        MeasurementRow.create(parameters)
        self.assertTrue(parameters.were_created())


class StreamLoggingTestCase(TestCase):

    def test_logging(self):
        s1 = "a test string"
        s2 = "another test string"
        result = f"{s1}\n{s2}\n"
        with StreamLogging() as stream:
            xls_logger.info(s1)
            xls_logger.error(s2)
            data = stream.get_log()
        self.assertEqual(result, data)

    def test_handlers(self):
        self.assertFalse(xls_logger.handlers)
        with StreamLogging() as s:
            self.assertTrue(xls_logger.handlers)
        self.assertFalse(xls_logger.handlers)


class SpreadsheetImportTestCase(TestCase):
    file = 'test_data/measurements_input2.xlsx'

    def setUp(self):
        p = Populator()
        p.populate_all()

    def import_data(self) -> None:
        si2 = SpreadsheetImporter(self.file)
        si2.import_spreadsheet()

    def create_row(self) -> ExcelRow:
        row = ExcelRow(ExcelRowInfoGenerator.get_sample_info())
        row.write_sample(self.file)
        self.import_data()
        self.assertTrue(row.is_in_database())
        return row

    def test_object_creation(self):
        self.create_row()

    def test_object_update(self):
        row = self.create_row()
        new_row_info = {
            UUID: row.row[UUID],
            MODE: CREATE_OR_UPDATE,
            RESEARCHER: str(Researcher.objects.last()),
            PROJECT: str(CellGenProject.objects.last()),
            SLIDE_BARCODE: str(Slide.objects.last()),
            AUTOMATED_PLATEID: "DIFFERENT",
            AUTOMATED_SLIDEN: 5,
            TECHNOLOGY: str(Technology.objects.last()),
            IMAGE_CYCLE: 1,
            CHANNEL_TARGET1: str(ChannelTarget.objects.all()[3]),
            CHANNEL_TARGET2: str(ChannelTarget.objects.all()[4]),
            CHANNEL_TARGET3: str(ChannelTarget.objects.all()[5]),
            DATE: ExcelRowInfoGenerator.get_todays_date(),
            MEASUREMENT:  str(MeasurementNumber.objects.last()),
            LOW_MAG_REFERENCE: str(LowMagReference.objects.last()),
            MAG_BIN_OVERLAP: str(MagBinOverlap.objects.last()),
            SECTIONS: "2,3",
            ZPLANES: str(ZPlanes.objects.last()),
            NOTES_1: "NEW",
            NOTES_2: "ELSE",
            EXPORT_LOCATION: "/OTHER/MOTHER",
            ARCHIVE_LOCATION: "/OTHER/FATHER",
            TEAM_DIR: str(TeamDirectory.objects.last()),
        }
        new_row = ExcelRow(new_row_info)
        new_row.write_sample(self.file, 0)
        self.import_data()
        self.assertTrue(new_row.is_in_database())
        self.assertFalse(row.is_in_database())

    def test_object_delete(self):
        row = self.create_row()
        row.write_sample(self.file, 0)
        self.import_data()
        self.assertTrue(row.is_in_database())
        row.row[MODE] = DELETE
        row.write_sample(self.file, 0)
        self.import_data()
        self.assertFalse(row.is_in_database())

    def tearDown(self) -> None:
        os.remove(self.file)
