from datetime import datetime

from django.test import TestCase
import pandas as pd

from experiments.constants import *
from experiments.constants import METABASE_ENTITIES_SEPARATOR as E, \
    METABASE_SAMPLES_ATTRIBUTES_SEPARATOR as S, \
    METABASE_CHANNEL_TARGETS_SEPARATOR as C

from experiments.xls.xls_converters import MetabaseColumnGenerator, MetabaseToTemplateConverter


class MetabaseColumnGeneratorTestCase(TestCase):

    def test_generate_channel_target_columns(self):
        res = f"Atto 425{C}CD68{E}DAPI{C}Nucleus{E}Opal 520{C}PECAM1 (IHC){E}Opal 570{C}CA9{E}Opal 650{C}TPSB2"
        self.assertEqual(res, MetabaseColumnGenerator.generate_channel_targets({
            CHANNEL1: "Atto 425",
            TARGET1: "CD68",
            CHANNEL2: "DAPI",
            TARGET2: "Nucleus",
            CHANNEL3: "Opal 520",
            TARGET3: "PECAM1 (IHC)",
            CHANNEL4: "Opal 570",
            TARGET4: "CA9",
            CHANNEL5: "Opal 650",
            TARGET5: "TPSB2"
        }))

    def test_generate_metabase_samples(self):
        pass
        row = {
            SAMPLE1: "A29-HEA-2-FFPE-1-S14-iii",
            TISSUE1: "Heart (R ventricle)",
            AGE1: "age_1",
            GENOTYPE1: "genotype_1",
            BACKGROUND1: "background_1",
            SAMPLE3: "A29-HEA-4-FFPE-1-S6-i",
            TISSUE3: "tissue4",
            SAMPLE4: "A29-HEA-3-FFPE-1-S10-ii",
            TISSUE4: "tissue_2",
            AGE4: "age2",
            GENOTYPE4: "gen2",
            BACKGROUND4: "back2",
        }
        res = f"1{S}{row[SAMPLE1]}{S}{row[TISSUE1]}{S}{row[AGE1]}{S}{row[GENOTYPE1]}{S}{row[BACKGROUND1]}{E}" \
              f"3{S}{row[SAMPLE3]}{S}{row[TISSUE3]}{S}{S}{S}{E}" \
              f"4{S}{row[SAMPLE4]}{S}{row[TISSUE4]}{S}{row[AGE4]}{S}{row[GENOTYPE4]}{S}{row[BACKGROUND4]}"
        self.assertEqual(res, MetabaseColumnGenerator.generate_samples(row))

    def test_generate_date(self):
        year = 2019
        month = 11
        day = 18
        date_string = datetime(year=year, month=month, day=day).strftime(DATE_FORMAT)
        self.assertEqual(f"{year}-{month}-{day}T00:00:00Z", MetabaseColumnGenerator.generate_date(date_string))


class MetabaseToTemplateConverterTestCase(TestCase):

    def test_convert_channel_targets(self):
        ch1 = "Atto 425"
        ch2 = "DAPI"
        ch3 = "Opal 520"
        ch4 = "Opal 570"
        ch5 = "Opel 650"
        ch2_1 = "Cy3"
        t2_1 = "cDNA"
        t1 = "CD68"
        t2 = "Nucleus"
        t3 = "PECAM (IHC)"
        row1 = {
            CHANNEL1: ch1,
            TARGET1: t1,
            CHANNEL2: ch2,
            TARGET2: t2,
            CHANNEL3: ch3,
            TARGET3: t3,
            CHANNEL4: ch4,
            TARGET4: t1,
            CHANNEL5: ch5,
            TARGET5: t2
        }
        row2 = {
            CHANNEL1: ch2_1,
            TARGET1: t2_1
        }

        df = pd.DataFrame([{
            METABASE_CHANNEL_TARGETS: MetabaseColumnGenerator.generate_channel_targets(row1)
        }, {
            METABASE_CHANNEL_TARGETS: MetabaseColumnGenerator.generate_channel_targets(row2)
        },
        ])
        res = pd.DataFrame([
            row1, row2
        ])
        converter = MetabaseToTemplateConverter(df)
        converter.convert_channel_targets()
        self.assertTrue(res.equals(converter.df))

    def test_convert_samples(self):
        row1 = {
            SAMPLE1: "A29-HEA-2-FFPE-1-S14-iii",
            TISSUE1: "Heart (R ventricle)",
            AGE1: "age_1",
            GENOTYPE1: "genotype_1",
            BACKGROUND1: "background_1",
            SAMPLE3: "A29-HEA-4-FFPE-1-S6-i",
            TISSUE3: "tissue4",
            AGE3: "",
            GENOTYPE3: "",
            BACKGROUND3: "",
            SAMPLE4: "A29-HEA-3-FFPE-1-S10-ii",
            TISSUE4: "tissue_2",
            AGE4: "age2",
            GENOTYPE4: "gen2",
            BACKGROUND4: "back2",
        }
        row2 = {
            SAMPLE3: "A29-HEA-3-FFPE-1-S10-ii",
            TISSUE3: "tissue_2",
            AGE3: "age2",
            GENOTYPE3: "gen2",
            BACKGROUND3: "back2",
        }

        df = pd.DataFrame([{
            METABASE_SAMPLES: MetabaseColumnGenerator.generate_samples(row1)
        }, {
            METABASE_SAMPLES: MetabaseColumnGenerator.generate_samples(row2)
        },
        ])
        row1.update({
            SECTION_NUM: "1, 3, 4"
        })
        row2.update({
            SECTION_NUM: "3"
        })
        res = pd.DataFrame([
            row1, row2
        ])
        converter = MetabaseToTemplateConverter(df)
        converter.convert_samples()
        self.assertTrue(res.equals(converter.df))
