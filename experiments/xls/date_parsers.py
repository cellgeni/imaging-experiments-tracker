import datetime
from abc import abstractmethod
from typing import Tuple, Union

from pandas._libs.tslibs.timestamps import Timestamp

ValidDateType = Union[str, Timestamp, datetime.datetime, datetime.date]


class AbstractDateParser:

    @staticmethod
    def raise_value_error(date_string: str):
        raise ValueError(f"Date must be in format DD.MM.YYYY or DD/MM/YYYY or DD-MM-YYYY. "
                         f"The problematic string is: {date_string}")

    @abstractmethod
    def parse(self) -> datetime.date:
        """Return a date object from a given object. """
        pass


class StringDateParser(AbstractDateParser):

    def __init__(self, date_string: str):
        self.separator = self.get_separator(date_string)
        self.date_string = date_string

    @staticmethod
    def get_separator(date_string: str) -> str:
        """Return the symbol that separates year, month, day. in a string"""
        for separator in {'.', '-'}:
            if separator in date_string:
                return separator
        default_separator = "/"
        return default_separator

    @staticmethod
    def get_valid_year(year: int) -> int:
        """If year is 19, make it 2019."""
        if year < 2000:
            year += 2000
        return year

    def split_date(self) -> Tuple[int, int, int]:
        """Extract year, month, day from a date string. """
        date_array = list(map(lambda x: int(x), self.date_string.split(self.separator)))
        valid_year = self.get_valid_year(date_array[2])
        return valid_year, date_array[1], date_array[0]

    def parse(self) -> datetime.date:
        """Return a date object from a string. """
        try:
            year, month, day = self.split_date()
            return datetime.date(year, month, day)
        except (AttributeError, ValueError, IndexError):
            self.raise_value_error(self.date_string)


class TimestampParser(AbstractDateParser):

    def __init__(self, date_string: Timestamp):
        self.timestamp = date_string

    def parse(self) -> datetime.date:
        """Return a date object from a timestamp. """
        return self.timestamp.date()


class DatetimeDateParser(AbstractDateParser):
    def __init__(self, date: datetime.date):
        self.date = date

    def parse(self) -> datetime.date:
        """
        Return a date object from a date object.
        This class is needed to comply with the interface of AbstractDateParser
        even if date is already a datetime.date object.
        """
        return self.date


class DateParserFactory:

    @staticmethod
    def get_parser(date_object: ValidDateType) -> AbstractDateParser:
        """Return a parser for a given type of an object. """
        d_type = type(date_object)
        if d_type is str:
            return StringDateParser(date_object)
        elif d_type is Timestamp or d_type is datetime.datetime:
            return TimestampParser(date_object)
        elif d_type is datetime.date:
            return DatetimeDateParser(date_object)
        else:
            # Excel transforms null values into floats like 0.0
            AbstractDateParser.raise_value_error(date_object)


class DateParser:

    @staticmethod
    def parse_date(date_object: ValidDateType) -> datetime.date:
        return DateParserFactory.get_parser(date_object).parse()
