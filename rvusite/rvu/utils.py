import datetime

def get_fiscal_year_start():
    """
    fiscal year starts 10/1.
    """
    now = datetime.datetime.now()
    fy_start = datetime.datetime(year=now.year, month=10, day=1)
    if now.month < 10:
        fy_start = datetime.datetime(year=now.year-1, month=10, day=1)
    return fy_start