from typing import Dict, Tuple, Iterable

from django.test import TestCase

from constants import *
from experiments.xls.column_importer import ColumnImporter
from experiments.xls.excel_row import ExcelRow
from experiments.models import *

RowT = Dict[str, str]


class SpreadsheetImportTestCase(TestCase):
    file = 'test_data/columns_input1.xlsx'

    def get_data(self) -> Tuple[RowT, RowT]:
        return {
            RESEARCHER: "AR",
            PROJECT: "TM_R2C",
            SLIDE_ID: "TM_RCC_00FZ",
            SLIDE_BARCODE: "TB14-2530-2-4",
            AUTOMATED_PLATEID: "191118_214002-V",
            AUTOMATED_SLIDEN: "N/A",
            TISSUE1: "Kidney (normal)",
            SAMPLE1: "L14-KID-0-FFPE-2-S4",
            TISSUE2: "HEART",
            SAMPLE2: "id",
            TISSUE3: "LEG",
            SAMPLE3: "id2",
            TECHNOLOGY: "some technology",
            CHANNEL1: "DAPI",
            TARGET1: "Nucleus",
            CHANNEL2: "Opal 520",
            TARGET2: "PECAM1 (IHC)",
            CHANNEL3: "Opal 570",
            TARGET3: "new",
            MEASUREMENT: "1a",
            LOW_MAG_REFERENCE: "Reference",
            MAG_BIN_OVERLAP: "10x",
            SECTION_NUM: "1,2",
            ZPLANES: "15*3",
        },{
            RESEARCHER: "MR",
            PROJECT: "TM_S2C",
            SLIDE_ID: "TS_RCC_00FZ",
            SLIDE_BARCODE: "AB14-2530-2-4",
            AUTOMATED_PLATEID: "A191118_214002-V",
            AUTOMATED_SLIDEN: 1,
            TISSUE1: "Kidney (not normal)",
            SAMPLE1: "L14",
            TISSUE2: "HEAT",
            SAMPLE2: "id3",
            TISSUE3: "LE",
            SAMPLE3: "id5",
            TECHNOLOGY: "some technology2",
            CHANNEL1: "DAPI",
            TARGET1: "Nucleus",
            CHANNEL2: "Opal 520",
            TARGET2: "PECAM1 CA8",
            CHANNEL3: "Opal 570",
            TARGET3: "old",
            MEASUREMENT: "1k",
            LOW_MAG_REFERENCE: "1",
            MAG_BIN_OVERLAP: "20x",
            SECTION_NUM: "1,2",
            ZPLANES: "15*9",
        }

    def import_data(self) -> None:
        si2 = ColumnImporter(self.file)
        si2.import_all_columns()

    def create_rows(self, rows: Iterable[RowT]):
        for i, r in enumerate(rows):
            row = ExcelRow(r)
            row.write_sample(self.file, i)
        self.import_data()

    def _test_samples(self, row: RowT):
        for s_column, t_column in SAMPLE_MAPPING.items():
            s = row.get(s_column)
            t = row.get(t_column)
            if s:
                sample = Sample.objects.get(id=s)
                if t:
                    tissue = Tissue.objects.get(name=t)
                    self.assertEqual(sample.tissue, tissue)

    def _test_sections(self, row: RowT, slide: Slide):
        sections = slide.section_set.all().order_by('number')
        sample_list = [SAMPLE1, SAMPLE2, SAMPLE3]
        for i, s in enumerate(sections):
            self.assertEqual(s.sample.id, row[sample_list[i]])

    def _test_slide(self, row: RowT):
        slide = Slide.objects.get(barcode_id=row[SLIDE_BARCODE])
        self._test_sections(row, slide)

    def _test_channel_targets(self, row: RowT):
        for ch_column, t_column in CHANNEL_TARGET_MAPPING.items():
            ch = row.get(ch_column)
            t = row.get(t_column)
            if ch and t:
                channel = Channel.objects.get(name=ch)
                target = Target.objects.get(name=t)
                self.assertTrue(ChannelTarget.objects.get(channel=channel, target=target))

    def _test_row(self, row: RowT):
        self.assertTrue(Researcher.objects.get(employee_key=row[RESEARCHER]))
        self.assertTrue(CellGenProject.objects.get(key=row[PROJECT]))
        self.assertTrue(Technology.objects.get(name=row[TECHNOLOGY]))
        self.assertTrue(MeasurementNumber.objects.get(name=row[MEASUREMENT]))
        self.assertTrue(LowMagReference.objects.get(name=row[LOW_MAG_REFERENCE]))
        self.assertTrue(MagBinOverlap.objects.get(name=row[MAG_BIN_OVERLAP]))
        self.assertTrue(ZPlanes.objects.get(name=row[ZPLANES]))
        self._test_samples(row)
        self._test_slide(row)
        self._test_channel_targets(row)

    def test_spreadsheet_upload(self):
        rows = self.get_data()
        self.create_rows(rows)
        for row in rows:
            self._test_row(row)