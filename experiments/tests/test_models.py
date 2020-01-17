from django.test import TestCase

from experiments.models import ChannelTarget


class ChannelTargetTestCase(TestCase):

    def test_parse_channel_and_target_name_from_str(self):
        ch1 = "Atto 425"
        ch2 = "Opal"
        t1 = "dapB"
        cht1 = f'{ch1} -> {t1}'
        cht2 = f'{ch2} -> {t1}'
        assert (ch1, t1) == ChannelTarget.get_channel_and_target_from_str(cht1)
        assert (ch2, t1) == ChannelTarget.get_channel_and_target_from_str(cht2)
        assert (ch1, t1) != ChannelTarget.get_channel_and_target_from_str(cht2)
        with self.assertRaises(ValueError):
            ChannelTarget.get_channel_and_target_from_str(f"{ch1} - {t1}")
        with self.assertRaises(ValueError):
            ChannelTarget.get_channel_and_target_from_str(23)
