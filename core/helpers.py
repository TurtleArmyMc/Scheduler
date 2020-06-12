import datetime
from calendar import monthrange


def format_date_iii(year=None, month=None, day=None, date=None) -> (int, int, int):
    # Return year, month, and day as a tuple of integers.
    if (date is not None):
        if (year is None and month is None and day is None):
            year = date.year
            month = date.month
            day = date.day
        else:
            raise SyntaxError("Pass either date object or year, month and day.")
    elif (year is None or month is None or day is None):
        raise SyntaxError("Pass either date object or year, month and day.")

    year = int(year)
    month = int(month)
    day = int(day)

    # Check if date is valid.
    try:
        datetime.date(year, month, day)
    except:
        raise

    return (year, month, day)


def format_date_ssi(year=None, month=None, day=None, date=None) -> (str, str, int):
    year, month, day = format_date_iii(year, month, day, date)
    return (str(year), str(month), day)


def format_date_sss(year=None, month=None, day=None, date=None) -> (str, str, str):
    year, month, day = format_date_iii(year, month, day, date)
    return (str(year), str(month), str(day))


def days_in_month(year, month) -> int:
    # Returns how many days there are in a given month.
    return monthrange(int(year), int(month))[1]


def get_current_year() -> int:
    return datetime.date.today().year


def get_current_month() -> int:
    return datetime.date.today().month


def get_current_day() -> int:
    return datetime.date.today().day


# Returns an abreviated weekday from date (Sun, Mon, Tue, etc.)
def get_weekday(year=None, month=None, day=None, date=None):
    year, month, day = format_date_iii(year, month, day, date)
    return datetime.date(year, month, day).strftime("%a")