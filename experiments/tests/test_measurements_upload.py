import datetime
import logging
import os
from typing import Dict

import pandas as pd
from django.test import TestCase, TransactionTestCase

from experiments.constants import *
from experiments.models.measurement import *
from experiments.populate import MeasurementsPopulator
from experiments.xls import xls_logger
from experiments.xls.excel_row import ExcelRow, RowT
from experiments.xls.file_importers import MeasurementsFileImporter
from experiments.xls.measurement_importer import MeasurementRow
from experiments.xls.measurement_parameters import MeasurementM2MFields, MeasurementParameters, \
    MeasurementParametersParser
from experiments.xls.stream_logging import StreamLogging

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
            SLIDE_ID: "TM_RCC_00FY",
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
            SECTION_NUM: "1,2",
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
        p = MeasurementsPopulator()
        p.populate_all()
        self.assertTrue(Researcher.objects.first())

    def test_write_row(self) -> None:
        sample_info = ExcelRowInfoGenerator.get_sample_info()
        self.assertTrue(sample_info[RESEARCHER])
        row = ExcelRow(sample_info)
        row.write_in_file(self.file)
        df = pd.read_excel(self.file)
        for key, value in sample_info.items():
            spreadsheet_value = df.loc[0, key]
            logger.debug(f"Key: {key}")
            logger.debug(f"Original value: {value}")
            logger.debug(f"Spreadsheet value: {spreadsheet_value}")
            self.assertEqual(value, spreadsheet_value)

    def _write_in_file(self, row: Dict[str, str]):
        row = ExcelRow(row)
        row.write_in_file(self.file, 0)

    def test_overwriting_old_values(self):
        row1 = {SLIDE_ID: "val1"}
        self._write_in_file(row1)
        df = pd.read_excel(self.file)
        self.assertEqual(df.loc[0, SLIDE_ID], "val1")
        row2 = {AUTOMATED_PLATEID: "val2",
                AUTOMATED_SLIDEN: "val3"}
        self._write_in_file(row2)
        df = pd.read_excel(self.file)
        self.assertEqual(df.loc[0, AUTOMATED_PLATEID], "val2")
        self.assertEqual(df.loc[0, AUTOMATED_SLIDEN], "val3")
        self.assertTrue(pd.isnull(df.loc[0, SLIDE_ID]))

    def tearDown(self) -> None:
        os.remove(self.file)


class MeasurementsParameterParserTestCase(TestCase):

    def setUp(self) -> None:
        p = MeasurementsPopulator()
        p.populate_sections()
        p.populate_channel_target_pairs()

    def test_parse_sections(self):
        slide = Slide.get_random_slide_with_three_sections()
        info = {
            SLIDE_BARCODE: str(slide),
            SECTION_NUM: "1,3",
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
        with self.assertRaises(ValidationError):
            MeasurementParametersParser._parse_section_numbers("cat, dog, 2")

    def test_parse_date(self):
        sample_date = datetime.date(2019, 2, 2)
        self.assertEqual(sample_date, MeasurementParametersParser._parse_date("2.2.2019"))
        self.assertEqual(sample_date, MeasurementParametersParser._parse_date("02/02/2019"))
        wrong_dates = ["1.13.2018", "some word", "1 02 2019", "2019.12.3", '0.0', 0.0, 0]
        for wrong_date in wrong_dates:
            with self.assertRaises(ValueError):
                MeasurementParametersParser._parse_date(wrong_date)


class MeasurementParametersGenerator:

    @staticmethod
    def get_sample_parameters() -> MeasurementParameters:
        sl1 = Slide.objects.get(barcode_id="S000000729")
        sc11 = Section.objects.get(number=1, slide=sl1)
        sc12 = Section.objects.get(number=2, slide=sl1)
        cht1 = ChannelTarget.objects.all()[0]
        cht2 = ChannelTarget.objects.all()[1]
        cht3 = ChannelTarget.objects.all()[2]
        model = Measurement(researcher=Researcher.objects.first(),
                            automated_slide_id="TM_RCC_00FZ",
                            automated_plate_id="kkjk",
                            automated_slide_num=1,
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
        p = MeasurementsPopulator()
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
                            automated_slide_id="TM_RCC_02FZ",
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
        p = MeasurementsPopulator()
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


class MeasurementsImportTestCase(TransactionTestCase):
    file = 'test_data/measurements_input2.xlsx'
    importer = MeasurementsFileImporter(file)

    def setUp(self):
        p = MeasurementsPopulator()
        p.populate_all()

    def write_row_dict_in_file(self, row_dict: RowT) -> ExcelRow:
        row = ExcelRow(row_dict)
        row.write_in_file(self.file)
        return ExcelRow(row_dict)

    def import_row_dict_into_db(self, row_dict: RowT) -> ExcelRow:
        row = self.write_row_dict_in_file(row_dict)
        self.importer.import_file()
        return row

    def import_sample_row_into_db(self) -> ExcelRow:
        return self.import_row_dict_into_db(ExcelRowInfoGenerator.get_sample_info())

    def test_object_creation(self):
        row = self.import_sample_row_into_db()
        self.assertTrue(row.is_in_database())

    def test_object_update(self):
        row = self.import_sample_row_into_db()
        self.assertTrue(row.is_in_database())
        new_row_info = {
            UUID: row.row[UUID],
            MODE: CREATE_OR_UPDATE,
            RESEARCHER: str(Researcher.objects.last()),
            PROJECT: str(CellGenProject.objects.last()),
            SLIDE_BARCODE: str(Slide.objects.last()),
            SLIDE_ID: "TM_RCC_00FY",
            TECHNOLOGY: str(Technology.objects.last()),
            IMAGE_CYCLE: 1,
            CHANNEL_TARGET1: str(ChannelTarget.objects.all()[3]),
            CHANNEL_TARGET2: str(ChannelTarget.objects.all()[4]),
            CHANNEL_TARGET3: str(ChannelTarget.objects.all()[5]),
            DATE: ExcelRowInfoGenerator.get_todays_date(),
            MEASUREMENT: str(MeasurementNumber.objects.last()),
            LOW_MAG_REFERENCE: str(LowMagReference.objects.last()),
            MAG_BIN_OVERLAP: str(MagBinOverlap.objects.last()),
            SECTION_NUM: "2,3",
            ZPLANES: str(ZPlanes.objects.last()),
            NOTES_1: "NEW",
            NOTES_2: "ELSE",
            EXPORT_LOCATION: "/OTHER/MOTHER",
            ARCHIVE_LOCATION: "/OTHER/FATHER",
            TEAM_DIR: str(TeamDirectory.objects.last()),
        }
        new_row = ExcelRow(new_row_info)
        self.import_row_dict_into_db(new_row_info)
        self.assertTrue(new_row.is_in_database())
        self.assertFalse(row.is_in_database())

    def test_object_delete(self):
        row = self.import_sample_row_into_db()
        self.assertTrue(row.is_in_database())
        row.row[MODE] = DELETE
        row = self.import_row_dict_into_db(row.row)
        self.assertFalse(row.is_in_database())

    def test_row_with_only_required_columns(self):
        row_dict = {
            UUID: uuid.uuid4(),
            MODE: CREATE_OR_UPDATE,
            RESEARCHER: str(Researcher.objects.last()),
            PROJECT: str(CellGenProject.objects.last()),
            SLIDE_BARCODE: str(Slide.objects.last()),
            TECHNOLOGY: str(Technology.objects.first()),
            SLIDE_ID: "TM_RCC_004Y",
            IMAGE_CYCLE: 1,
            CHANNEL_TARGET1: str(ChannelTarget.objects.all()[3]),
            DATE: ExcelRowInfoGenerator.get_todays_date(),
            MEASUREMENT: str(MeasurementNumber.objects.last()),
            MAG_BIN_OVERLAP: str(MagBinOverlap.objects.last()),
            SECTION_NUM: "2,3",
            EXPORT_LOCATION: "/OTHER/MOTHER",
            TEAM_DIR: str(TeamDirectory.objects.last()),
        }
        row = self.import_row_dict_into_db(row_dict)
        self.assertTrue(row.is_in_database())

    def test_inserting_duplicate_measurement(self):
        row = self.import_sample_row_into_db()
        self.assertTrue(row.is_in_database())
        row.row[UUID] = uuid.uuid4()
        row = self.import_row_dict_into_db(row.row)
        self.assertFalse(row.is_in_database())

    def test_row_with_automated_plate_id_and_automated_slide_num(self):
        row = self.import_sample_row_into_db()
        self.assertTrue(row.is_in_database())
        Measurement.objects.get(uuid=row.row[UUID]).delete()
        row.row.pop(AUTOMATED_SLIDEN)
        row = self.import_row_dict_into_db(row.row)
        self.assertFalse(row.is_in_database())

    def tearDown(self) -> None:
        os.remove(self.file)
