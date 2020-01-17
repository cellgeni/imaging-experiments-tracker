import logging
import os

import pandas as pd

from django.core.exceptions import ObjectDoesNotExist

from experiments.constants import *
from experiments.models import Measurement


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SampleRow:

    def __init__(self, row):
        self.row = row

    def write_row(self, df):
        for column in self.row.keys():
            df.loc[0, column] = self.row[column]

    def write_sample(self, output):
        template_file = 'test_data/measurements_input.xlsx'
        assert os.path.exists(template_file)
        df = pd.read_excel(template_file)
        self.write_row(df)
        df.to_excel(output)
        assert os.path.exists(output)

    def is_in_database(self):
        try:
            m = Measurement.objects.get(id=self.row[UUID])
        except ObjectDoesNotExist:
            logger.info("Object is not in the database")
            return False
        assert str(m.researcher) == self.row[RESEARCHER]
        # assert str(m.) == self.row[PROJECT]
        assert str(m.automated_slide_num) == self.row[AUTOMATED_SLIDEN]
        assert str(m.automated_plate_id) == self.row[AUTOMATED_PLATEID]
        assert str(m.technology) == self.row[TECHNOLOGY]
        assert str(m.image_cycle) == self.row[IMAGE_CYCLE]
        assert m.date == self.row[DATE]
        assert str(m.measurement) == self.row[MEASUREMENT]
        assert str(m.low_mag_reference) == self.row[LOW_MAG_REFERENCE]
        assert str(m.mag_bin_overlap) == self.row[MAG_BIN_OVERLAP]
        assert str(m.z_planes) == self.row[ZPLANES]
        assert str(m.notes_1) == self.row[NOTES_1]
        assert str(m.notes_2) == self.row[NOTES_2]
        assert str(m.export_location) == self.row[EXPORT_LOCATION]
        assert str(m.archive_location) == self.row[ARCHIVE_LOCATION]
        assert str(m.team_directory) == self.row[TEAM_DIR]
        row_channel_targets = list(filter(None, [self.row.get(ch_t) for ch_t in
                                                 [CHANNEL_TARGET + str(x) for x in range(1, 6)]]))
        measurement_channel_targets = [str(cht) for cht in m.channel_target_pairs.all()]
        assert row_channel_targets == measurement_channel_targets
        sections = m.sections.all()
        for section in sections:
            assert section.slide_id == self.row[SLIDE_BARCODE]
            assert str(section.number) in self.row[SECTIONS]
        return True
