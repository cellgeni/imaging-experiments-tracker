import logging
import os
from typing import Dict

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist

from experiments.constants import *
from experiments.models import Measurement
from experiments.xls import EXCEL_TEMPLATE, xls_logger as logger


class ExcelRow:

    def __init__(self, row: Dict):
        self.row = row

    def write_row(self, df: pd.DataFrame, row_num: int) -> None:
        for column in self.row.keys():
            df.loc[row_num, column] = self.row[column]

    def write_sample(self, output_file: str, row_num: int = 0) -> None:
        assert os.path.exists(EXCEL_TEMPLATE)
        df = pd.read_excel(EXCEL_TEMPLATE)
        self.write_row(df, row_num)
        df.to_excel(output_file)
        assert os.path.exists(output_file)

    def is_in_database(self) -> bool:
        try:
            m = Measurement.objects.get(uuid=self.row[UUID])
        except ObjectDoesNotExist:
            logger.info(f"Object with uuid {self.row[UUID]} is not in the database")
            return False
        data = list()
        data.append((str(m.researcher), self.row[RESEARCHER]))
        data.append((m.automated_slide_num, self.row[AUTOMATED_SLIDEN]))
        data.append((str(m.automated_plate_id), self.row[AUTOMATED_PLATEID]))
        data.append((str(m.technology), self.row[TECHNOLOGY]))
        data.append((m.image_cycle, self.row[IMAGE_CYCLE]))
        data.append((str(m.date).replace('+00:00', ''), self.row[DATE]))
        data.append((str(m.measurement), str(self.row[MEASUREMENT])))
        data.append((str(m.low_mag_reference), self.row[LOW_MAG_REFERENCE]))
        data.append((str(m.mag_bin_overlap), self.row[MAG_BIN_OVERLAP]))
        data.append((str(m.z_planes), self.row[ZPLANES]))
        data.append((str(m.notes_1), self.row[NOTES_1]))
        data.append((str(m.notes_2), self.row[NOTES_2]))
        data.append((str(m.export_location), self.row[EXPORT_LOCATION]))
        data.append((str(m.archive_location), self.row[ARCHIVE_LOCATION]))
        data.append((str(m.team_directory), self.row[TEAM_DIR]))
        row_channel_targets = set(filter(None, [self.row.get(ch_t) for ch_t in
                                                 [CHANNEL_TARGET + str(x) for x in range(1, 6)]]))
        measurement_channel_targets = {str(cht) for cht in m.channel_target_pairs.all()}
        data.append((row_channel_targets, measurement_channel_targets))
        for pair in data:
            if pair[0] != pair[1]:
                logger.error(f'Unequal pair: {pair}')
                return False
        sections = m.sections.all()
        for section in sections:
            if not (section.slide_id == self.row[SLIDE_BARCODE] and
                    str(section.number) in self.row[SECTIONS]):
                logger.error(f'problem with section: {section}')
                return False
        return True
