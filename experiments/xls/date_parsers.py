import datetime
from abc import abstractmethod
from typing import Tuple, Union

from pandas._libs.tslibs.timestamps import Timestamp


class DateParser:

    @staticmethod
    def raise_value_error(datestring: str):
        raise ValueError(f"Date must be in format DD.MM.YYYY or DD/MM/YYYY. A problematic string is: {datestring}")

    @abstractmethod
    def parse(self) -> datetime.date:
        pass


class StringDateParser(DateParser):

    def __init__(self, datestring: str):
        self.separator = self.get_separator(datestring)
        self.datestring = datestring

    @staticmethod
    def get_separator(datestring: str) -> str:
        if "." in datestring:
            return "."
        else:
            return "/"

    def get_valid_year(self, year: int) -> int:
        if year < 2000:
            year += 2000
        return year

    def split_date(self) -> Tuple[int, int, int]:
        date_array = list(map(lambda x: int(x), self.datestring.split(self.separator)))
        valid_year = self.get_valid_year(date_array[2])
        return valid_year, date_array[1], date_array[0]

    def parse(self) -> datetime.date:
        try:
            year, month, day = self.split_date()
            return datetime.date(year, month, day)
        except (AttributeError, ValueError, IndexError):
            self.raise_value_error(self.datestring)


class TimestampParser(DateParser):

    def __init__(self, datestring: Timestamp):
        self.timestamp = datestring

    def parse(self) -> datetime.date:
        return self.timestamp.date()


class DateParserFactory:

    @staticmethod
    def get_parser(datestring: Union[str, Timestamp]) -> DateParser:
        d_type = type(datestring)
        if d_type is str:
            return StringDateParser(datestring)
        elif d_type is Timestamp:
            return TimestampParser(datestring)
        else:
            # Excel transforms null values into floats like 0.0
            DateParser.raise_value_error(datestring)