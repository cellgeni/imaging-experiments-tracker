from typing import List, Dict

from experiments.models import ChannelTarget, Measurement, Section


class MeasurementM2MFields:

    def __init__(self, channel_target_pairs: List[ChannelTarget],
                 sections: List[Section]):
        self.channel_target_pairs = channel_target_pairs
        self.sections = sections


class MeasurementParameters:

    def __init__(self, model: Measurement, m2m_fields: MeasurementM2MFields):
        self.model = model
        self.m2m_fields = m2m_fields

    def create_db_object(self):
        self.model.save()
        for section in self.m2m_fields.sections:
            self.model.sections.add(section)
        for chtp in self.m2m_fields.channel_target_pairs:
            self.model.channel_target_pairs.add(chtp)

    def were_created(self):
        m = Measurement.objects.get(id=self.model.id)
        assert list(m.sections.all()) == self.m2m_fields.sections
        assert list(m.channel_target_pairs.all()) == self.m2m_fields.channel_target_pairs
        return True