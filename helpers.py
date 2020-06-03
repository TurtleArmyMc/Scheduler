from datetime import date as datetime_date
from calendar import monthrange


def format_date(year=None, month=None, day=None, date=None):
    # Return year, month, and day with proper formatting.
    if (date is not None):
        if (year is None and month is None and day is None):
            year = date.year
            month = date.month
            day = date.day
        else:
            raise SyntaxError("Pass either date object or year, month and day.")
    elif (year is None or month is None or day is None):
        raise SyntaxError("Pass either date object or year, month and day.")

    # Check if date is valid.
    try:
        datetime_date(int(year), int(month), int(day))
    except:
        raise

    # year and month must be strings because they are used as json dictionary 
    # keys, while day must be an int because it is used to index an array.
    year = str(year)
    month = str(month)
    day = int(day)

    return (year, month, day)


def days_in_month(year, month):
    # Returns how many days there are in a given month.
    return monthrange(int(year), int(month))[1]


def get_current_year():
    return datetime_date.today().year


def get_current_month():
    return datetime_date.today().month


def get_current_day():
    return datetime_date.today().day