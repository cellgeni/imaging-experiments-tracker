import datetime

import pandas as pd

from experiments import RowT, helpers
from experiments.constants import *
from experiments.constants import METABASE_ENTITIES_SEPARATOR as E, METABASE_CHANNEL_TARGETS_SEPARATOR as C
from experiments.helpers import get_sample_attributes_column_name
from experiments.xls.row_parser import ChannelTargetParser


class MetabaseColumnGenerator:

    @classmethod
    def generate_samples(cls, samples_dict: RowT) -> str:
        samples = []
        for i in range(1, MAX_SLOTS + 1):
            sample_id = samples_dict.get(get_sample_attributes_column_name(SAMPLE, i))
            if sample_id:
                sample_info = []
                sample_info.append(str(i))
                sample_info.append(sample_id)
                sample_info.append(samples_dict.get(get_sample_attributes_column_name(TISSUE, i), ""))
                sample_info.append(samples_dict.get(get_sample_attributes_column_name(AGE, i), ""))
                sample_info.append(samples_dict.get(get_sample_attributes_column_name(GENOTYPE, i), ""))
                sample_info.append(samples_dict.get(get_sample_attributes_column_name(BACKGROUND, i), ""))
                samples.append(METABASE_SAMPLES_ATTRIBUTES_SEPARATOR.join(sample_info))
        return METABASE_ENTITIES_SEPARATOR.join(samples)

    @classmethod
    def generate_channel_targets(cls, channel_targets: RowT) -> str:
        chtp = ChannelTargetParser(channel_targets)
        return f"{E}".join(f"{channel}{C}{target}"
                           for channel, target in chtp.get_channel_targets()
                           if channel and target)

    @classmethod
    def generate_date(cls, date_string: str) -> str:
        return datetime.datetime.strptime(date_string, DATE_FORMAT).strftime(METABASE_DATE_FORMAT)


class MetabaseToTemplateConverter:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def rename_columns(self):
        self.df.rename(columns=METABASE_TO_TEMPLATE_MAPPING, inplace=True)

    def convert_samples(self):
        for index, row in self.df.iterrows():
            indeces = []
            samples = row[METABASE_SAMPLES].split(METABASE_ENTITIES_SEPARATOR)
            for sample in samples:
                sample_info = sample.split(METABASE_SAMPLES_ATTRIBUTES_SEPARATOR)
                i = sample_info[0]
                indeces.append(i)
                self.df.loc[index, get_sample_attributes_column_name(SAMPLE, i)] = sample_info[1]
                self.df.loc[index, get_sample_attributes_column_name(TISSUE, i)] = sample_info[2]
                self.df.loc[index, get_sample_attributes_column_name(AGE, i)] = sample_info[3]
                self.df.loc[index, get_sample_attributes_column_name(GENOTYPE, i)] = sample_info[4]
                self.df.loc[index, get_sample_attributes_column_name(BACKGROUND, i)] = sample_info[5]
            self.df.loc[index, SECTION_NUM] = ", ".join(indeces)
        self.df.drop(METABASE_SAMPLES, axis=1, inplace=True)

    def convert_channel_targets(self):
        for index, row in self.df.iterrows():
            channel_targets = row[METABASE_CHANNEL_TARGETS].split(METABASE_ENTITIES_SEPARATOR)
            for i, channel_target in enumerate(channel_targets):
                channel, target = channel_target.split(METABASE_CHANNEL_TARGETS_SEPARATOR)
                self.df.loc[index, helpers.get_channel_column_name(i + 1)] = channel
                self.df.loc[index, helpers.get_target_column_name(i + 1)] = target
        self.df.drop(METABASE_CHANNEL_TARGETS, axis=1, inplace=True)

    def _convert_harmony_copy(self):
        self.df = self.df.astype({HARMONY_COPY: str})
        replacements = {
            "False": "No",
            "True": "Yes"
        }
        self.df[HARMONY_COPY] = self.df[HARMONY_COPY].replace(replacements)

    @staticmethod
    def generate_template_date(date_string: str) -> str:
        return datetime.datetime.strptime(date_string, METABASE_DATE_FORMAT).strftime(DATE_FORMAT)

    def _convert_date(self) -> None:
        self.df[DATE] = self.df[DATE].apply(self.generate_template_date)

    def convert_values(self) -> None:
        self._convert_harmony_copy()
        self._convert_date()

    def cleanup(self):
        self.df = self.df.replace({pd.np.nan: None})

    def convert(self) -> pd.DataFrame:
        self.rename_columns()
        self.convert_samples()
        self.convert_channel_targets()
        self.convert_values()
        self.cleanup()
        return self.df
