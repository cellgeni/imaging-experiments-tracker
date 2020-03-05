import uuid

import pandas as pd

from experiments.constants import UUID, MODE, MeasurementModes


class ColumnInjector:

    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_excel(self.filename)

    def inject_uuids(self) -> None:
        if UUID not in self.df.columns:
            self.df.insert(0, UUID, pd.Series([uuid.uuid4() for x in range(len(self.df))]))

    def inject_mode(self, mode: MeasurementModes) -> None:
        if MODE not in self.df.columns:
            self.df.insert(1, MODE, mode.value)

    def save_file(self) -> None:
        self.df.to_excel(self.filename, index=False)

    def inject_uuid_mode_columns(self) -> None:
        self.inject_uuids()
        self.inject_mode(MeasurementModes.CREATE_OR_UPDATE)
        self.save_file()
