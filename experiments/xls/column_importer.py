import pandas as pd

from experiments.xls.import_xls import ExcelImporter
from experiments.constants import *
from experiments.models import *


class ColumnImporter(ExcelImporter):

    def import_researchers(self):
        self.df[RESEARCHER].apply(lambda key: Researcher.objects.get_or_create(employee_key=key))

    def import_project(self):
        self.df[PROJECT].apply(lambda key: CellGenProject.objects.get_or_create(key=key))

    def import_low_mag_reference(self):
        self.df[LOW_MAG_REFERENCE].apply(lambda key: LowMagReference.objects.get_or_create(name=key))

    def import_technology(self):
        self.df[TECHNOLOGY].apply(lambda name: Technology.objects.get_or_create(name=name))

    def import_measurement_numbers(self):
        self.df[MEASUREMENT].apply(lambda name: MeasurementNumber.objects.get_or_create(name=name))

    def import_mag_bin_overlap(self):
        self.df[MAG_BIN_OVERLAP].apply(lambda name: MagBinOverlap.objects.get_or_create(name=name))

    def import_zplanes(self):
        self.df[ZPLANES].apply(lambda name: ZPlanes.objects.get_or_create(name=name))

    def import_sections(self, row: pd.Series, slide: Slide):
        for s_column in SAMPLE_MAPPING.keys():
            sample_id = row.get(s_column)
            if sample_id:
                sample = Sample.objects.get_or_create(id=sample_id)[0]
                Section.objects.get_or_create(number=int(s_column[-1]), sample=sample, slide=slide)

    def import_slides(self, row: pd.Series):
        slide = Slide.objects.get_or_create(barcode_id=row[SLIDE_BARCODE], automated_id=row[SLIDE_ID])[0]
        self.import_sections(row, slide)

    def import_channel_targets(self, row: pd.Series):
        for ch_name, t_name in CHANNEL_TARGET_MAPPING.items():
            ch = row.get(ch_name)
            t = row.get(t_name)
            if ch and t:
                channel = Channel.objects.get_or_create(name=ch)[0]
                target = Target.objects.get_or_create(name=t)[0]
                ChannelTarget.objects.get_or_create(channel=channel, target=target)
            elif not (ch or t):
                pass
            else:
                raise ValueError(f"One of the channel or target values is missing, channel: {ch}, target: {t}")

    def import_samples(self, row: pd.Series):
        for s_column, t_column in SAMPLE_MAPPING.items():
            s = row.get(s_column)
            t = row.get(t_column)
            if s and t:
                tissue = Tissue.objects.get_or_create(name=t)[0]
                Sample.objects.get_or_create(id=s, tissue=tissue)
            elif not (ch or t):
                pass
            else:
                raise ValueError(f"One of the sample or tissue values is missing, sample: {s}, tissue: {t}")

    def import_all_columns(self):
        self.import_researchers()
        self.import_project()
        self.import_technology()
        self.import_low_mag_reference()
        self.import_mag_bin_overlap()
        self.import_measurement_numbers()
        self.import_zplanes()
        for _, row in self.df.iterrows():
            self.import_channel_targets(row)
            self.import_samples(row)
            self.import_slides(row)
