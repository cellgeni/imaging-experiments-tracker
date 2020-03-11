import os
from typing import Dict, List, Any

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from experiments.constants import *
from experiments.models import Measurement
from experiments.xls import EXCEL_TEMPLATE, xls_logger as logger

RowT = Dict[str, str]


class ExcelRowWriter:
    """
    Writes a dictionary of column-values into an Excel file
    """
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


class ExcelRowComparator:
    """
    Checks whether a dictionary of column-values corresponds to an entry in the database
    """

    def __init__(self, row: RowT):
        self.row = row

    @staticmethod
    def is_empty(s: Any):
        return s is None or s == "" or s == "nan" or s == "None" or pd.isna(s)

    def _compare_pairs(self, pairs: List) -> bool:
        for pair in pairs:
            if not (self.is_empty(pair[0]) and self.is_empty(pair[1])) and pair[0] != pair[1]:
                logger.error(f'Unequal pair: {pair}')
                return False
        return True

    def _compare_sections(self, sections: QuerySet) -> bool:
        for section in sections:
            if not (section.slide_id == self.row[SLIDE_BARCODE] and
                    str(section.number) in self.row[SECTION_NUM]):
                logger.error(f'problem with section: {section}')
                return False
        return True

    def is_in_database(self) -> bool:
        try:
            m = Measurement.objects.get(uuid=self.row.get(UUID))
        except Measurement.DoesNotExist:
            logger.info(f"Object with uuid {self.row.get(UUID)} is not in the database")
            return False
        data = list()
        data.append((str(m.researcher), self.row.get(RESEARCHER)))
        data.append((m.automated_slide_num, str(self.row.get(AUTOMATED_SLIDEN))))
        data.append((str(m.automated_plate_id), self.row.get(AUTOMATED_PLATEID)))
        data.append((str(m.technology), self.row.get(TECHNOLOGY)))
        data.append((m.image_cycle, self.row.get(IMAGE_CYCLE)))
        data.append((m.date.strftime(Measurement.DATE_FORMAT), self.row.get(DATE)))
        data.append((str(m.measurement), str(self.row.get(MEASUREMENT))))
        data.append((str(m.low_mag_reference), self.row.get(LOW_MAG_REFERENCE)))
        data.append((str(m.mag_bin_overlap), self.row.get(MAG_BIN_OVERLAP)))
        data.append((str(m.z_planes), self.row.get(ZPLANES)))
        data.append((str(m.notes_1), self.row.get(NOTES_1)))
        data.append((str(m.notes_2), self.row.get(NOTES_2)))
        data.append((str(m.export_location), self.row.get(EXPORT_LOCATION)))
        data.append((str(m.archive_location), self.row.get(ARCHIVE_LOCATION)))
        data.append((str(m.team_directory), self.row.get(TEAM_DIR)))
        row_channel_targets = set(filter(None, [self.row.get(ch_t) for ch_t in
                                                [CHANNEL_TARGET + str(x) for x in range(1, 6)]]))
        measurement_channel_targets = {str(cht) for cht in m.channel_target_pairs.all()}
        data.append((row_channel_targets, measurement_channel_targets))
        return self._compare_pairs(data) and self._compare_sections(m.sections.all())


class ExcelRow:
    """
    A mediator for common operations on a dictionary of column-values
    """

    def __init__(self, row: RowT):
        self.row = row
        self.comparator = ExcelRowComparator(row)
        self.writer = ExcelRowWriter(row)

    def is_in_database(self) -> bool:
        return self.comparator.is_in_database()

    def write_in_file(self, output_file: str, row_num: int = 0) -> None:
        return self.writer.write_in_file(output_file, row_num)
