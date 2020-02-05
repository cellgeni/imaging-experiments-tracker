import traceback
from functools import wraps

import pandas as pd

from experiments.xls import xls_logger as logger
from experiments.xls.import_xls import ExcelImporter
from experiments.constants import *
from experiments.models import *


def log_errors(func):
    @wraps(func)
    def f(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
        # func(*args, **kwargs)

    return f


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

    @log_errors
    def import_sections(self, row: pd.Series, slide: Slide):
        for s_column in SAMPLE_MAPPING.keys():
            sample_id = row.get(s_column)
            if sample_id:
                sample = Sample.objects.get_or_create(id=sample_id)[0]
                Section.objects.update_or_create(number=int(s_column[-1]), sample=sample, slide=slide)

    @log_errors
    def import_slides(self, row: pd.Series):
        try:
            slide = Slide.objects.get_or_create(barcode_id=row[SLIDE_BARCODE])[0]
            self.import_sections(row, slide)
        except KeyError as e:
            logger.error(f"The column name should be {SLIDE_BARCODE}")


    @log_errors
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

    @log_errors
    def import_samples(self, row: pd.Series):
        for s_column, t_column in SAMPLE_MAPPING.items():
            s = row.get(s_column)
            t = row.get(t_column)
            if s and t:
                tissue = Tissue.objects.get_or_create(name=t)[0]
                sample = Sample.objects.get_or_create(id=s)[0]
                sample.tissue = tissue
                sample.save()
            elif not (s or t):
                pass
            else:
                raise ValueError(f"One of the sample or tissue values is missing, sample: {s}, tissue: {t}")

    @log_errors
    def import_column(self, column):
        if column == RESEARCHER:
            self.import_researchers()
        elif column == PROJECT:
            self.import_project()
        elif column == LOW_MAG_REFERENCE:
            self.import_low_mag_reference()
        elif column == TECHNOLOGY:
            self.import_technology()
        elif column == MEASUREMENT:
            self.import_measurement_numbers()
        elif column == MAG_BIN_OVERLAP:
            self.import_mag_bin_overlap()
        elif column == ZPLANES:
            self.import_zplanes()
        logger.info(f"Imported {column}")

    def import_row(self, i, row, column):
        try:
            if column == SLIDE_BARCODE:
                self.import_slides(row)
            elif column == SAMPLE:
                self.import_samples(row)
            elif column == CHANNEL_TARGET:
                self.import_channel_targets(row)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"A problem importing row {i+1}, error: {e}")

    def import_all_columns(self):
        for column in [RESEARCHER, PROJECT, TECHNOLOGY, LOW_MAG_REFERENCE, MAG_BIN_OVERLAP, MEASUREMENT, ZPLANES]:
            self.import_column(column)
        for i, row in self.df.iterrows():
            for column in [SLIDE_BARCODE, SAMPLE, CHANNEL_TARGET]:
                self.import_row(i, row, column)
