import datetime
import os
from typing import Dict, List, Set

import pandas as pd
from django.contrib.auth.models import User
from django.test import TestCase

from experiments import RowT, auth
from experiments.constants import *
from experiments.helpers import is_empty
from experiments.models import (ArchiveLocation, Channel, ChannelTarget,
                                ExportLocation, LowMagReference, MagBinOverlap,
                                Measurement, MeasurementNumber, Project,
                                Researcher, Section, Slide, Slot, Target,
                                TeamDirectory, Technology, ZPlanes)
from experiments.populate.measurement import MeasurementsPrerequisitesPopulator
from experiments.xls import EXCEL_TEMPLATE
from experiments.xls.measurement_importer import ExistingMeasurementFinder


class ExcelRowWriter:
    """Class for writing a dictionary of column-values into an Excel file."""
    default_template = EXCEL_TEMPLATE

    def __init__(self, row: RowT):
        self.row = row

    def _write_in_dataframe(self, df: pd.DataFrame, row_num: int) -> pd.DataFrame:
        row = pd.Series(self.row)
        if len(df) <= row_num:
            df = df.append(row, ignore_index=True)
        else:
            df.loc[row_num] = row
        return df

    def _get_target_file(self, output_file: str):
        assert os.path.exists(self.default_template)
        return output_file if os.path.exists(output_file) else self.default_template

    def write_in_file(self, output_file: str, row_num: int = 0) -> None:
        target_file = self._get_target_file(output_file)
        df = pd.read_excel(target_file)
        df = self._write_in_dataframe(df, row_num)
        df.to_excel(output_file, index=False)


class ExcelRow:
    """A class to represent a row in Excel and supporting operations on this row"""

    def __init__(self, row: RowT):
        self.row = row
        self.writer = ExcelRowWriter(row)

    def write_to_file(self, output_file: str, row_num: int = 0) -> None:
        """Write this row to a file."""
        return self.writer.write_in_file(output_file, row_num)


class ExcelRowInfoGenerator:

    def __init__(self, d: Dict):
        self.d = d

    @staticmethod
    def get_todays_date():
        """Generate today's date in a valid format. """
        return datetime.date.today().strftime(DATE_FORMAT)

    @classmethod
    def get_sample_row(cls) -> RowT:
        """
        Generate valid (all keys must be present in the databases, all required keys are present)
        exemplary dictionary of strings for testing that can be interpreted as an Excel row
        """
        ch1 = Channel.objects.first()
        ch2 = Channel.objects.last()
        t1 = Target.objects.get_or_create(name="MYH11")
        t2 = Target.objects.get_or_create(name="dapB")
        t3 = Target.objects.get_or_create(name="POLR2A")
        return {
            RESEARCHER: str(Researcher.objects.first()),
            PROJECT: str(Project.objects.first()),
            SLIDE_BARCODE: str(Slide.objects.first().barcode),
            SLIDE_ID: "TM_RCC_00FY",
            AUTOMATED_PLATEID: "smth",
            AUTOMATED_SLIDEN: 1,
            TECHNOLOGY: str(Technology.objects.first()),
            IMAGE_CYCLE: 1,
            TISSUE1: "any",
            SAMPLE1: "any",
            TISSUE2: "any2",
            SAMPLE2: "any2",
            TISSUE3: "any3",
            SAMPLE3: "any3",
            CHANNEL1: str(ch1),
            TARGET1: str(t1),
            CHANNEL2: str(ch2),
            TARGET2: str(t2),
            CHANNEL3: str(ch1),
            TARGET3: str(t2),
            CHANNEL4: str(ch2),
            TARGET4: str(t3),
            DATE: cls.get_todays_date(),
            MEASUREMENT_NUMBER: str(MeasurementNumber.objects.first()),
            LOW_MAG_REFERENCE: str(LowMagReference.objects.first()),
            MAG_BIN_OVERLAP: str(MagBinOverlap.objects.first()),
            SECTION_NUM: "1,2",
            ZPLANES: str(ZPlanes.objects.first()),
            NOTES_1: "SMTH",
            NOTES_2: "SMTH",
            POST_STAIN: "smth",
            HARMONY_COPY: "Yes",
            EXPORT_LOCATION: str(ExportLocation.objects.first()),
            ARCHIVE_LOCATION: str(ArchiveLocation.objects.first()),
            TEAM_DIR: str(TeamDirectory.objects.first()),
        }


class MeasurementImportBaseTestCase(TestCase):

    def setUp(self):
        MeasurementsPrerequisitesPopulator.populate_all_prerequisites()
        self.user_id = self._create_owner_user()

    def _create_owner_user(self) -> int:
        """Create a user that has Owner role on all projects and return user id."""
        user = User.objects.get_or_create(username="test", password="test")[0]
        for project in Project.objects.all():
            auth.add_role(user.id, project.id, Role.OWNER)
        return user.id

    def compare_pair(self, pair):
        if not (is_empty(pair[0]) and is_empty(pair[1])):
            self.assertEqual(pair[0], pair[1])

    def _compare_fields(self, fields: List):
        for pair in fields:
            self.compare_pair(pair)

    def compare_section(self, section: Section, row: RowT):
        if str(section.number) in row[SECTION_NUM]:
            # TODO: check sample
            self.assertEqual(section.slide.barcode.name, row[SLIDE_BARCODE])

    def _compare_sections(self, measurement: Measurement, row: RowT):
        slot = Slot.objects.get(measurement=measurement,
                                automated_slide_num=int(row.get(AUTOMATED_SLIDEN)),
                                automated_slide__name=row.get(SLIDE_ID))
        for section in slot.sections.all():
            self.compare_section(section, row)

    def _create_channel_targets(self, row) -> Set[str]:
        result = set()
        for i in range(1, MAX_CHANNELS + 1):
            channel_column = CHANNEL + f"{i}"
            target_column = TARGET + f"{i}"
            channel_name = row.get(channel_column)
            target_name = row.get(target_column)
            if channel_name and target_name:
                result.add(channel_name + ChannelTarget.SEPARATOR + target_name)
        return result

    def check_row_is_in_database(self, row: RowT):
        """Check whether a measurement that corresponds to this row is in the database."""
        
        m = ExistingMeasurementFinder(row).get_existing_measurement_from_a_row()
        self.assertTrue(m)
        if not m:
            return
        data = list()
        data.append((str(m.researcher), row.get(RESEARCHER)))
        data.append((str(m.project), row.get(PROJECT)))
        data.append((str(m.plate), row.get(AUTOMATED_PLATEID)))
        data.append((str(m.technology), row.get(TECHNOLOGY)))
        data.append((m.image_cycle, row.get(IMAGE_CYCLE)))
        data.append((m.date.strftime(DATE_FORMAT), row.get(DATE)))
        data.append((str(m.measurement_number), str(row.get(MEASUREMENT_NUMBER))))
        data.append((str(m.low_mag_reference), row.get(LOW_MAG_REFERENCE)))
        data.append((str(m.mag_bin_overlap), row.get(MAG_BIN_OVERLAP)))
        data.append((str(m.z_planes), row.get(ZPLANES)))
        data.append((str(m.notes_1), row.get(NOTES_1)))
        data.append((str(m.notes_2), row.get(NOTES_2)))
        data.append((str(m.post_stain), row.get(POST_STAIN)))
        # TODO: data.append((str(m.harmony_copy_deleted), row.get(HARMONY_COPY)))
        data.append((str(m.export_location), row.get(EXPORT_LOCATION)))
        data.append((str(m.archive_location), row.get(ARCHIVE_LOCATION)))
        data.append((str(m.team_directory), row.get(TEAM_DIR)))
        row_channel_targets = self._create_channel_targets(row)
        measurement_channel_targets = {str(cht) for cht in m.channel_target_pairs.all()}
        data.append((row_channel_targets, measurement_channel_targets))
        self._compare_fields(data)
        self._compare_sections(m, row)

    def check_row_is_not_in_database(self, row: RowT):
        with self.assertRaises(AssertionError):
            self.check_row_is_in_database(row)
