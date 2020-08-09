import datetime as dt
def convert_date(str_date: str, year: int=None):
    today = dt.date.today()

    t_month, t_day = map(int, str_date.split("/"))
    if year is None:
        year, month, day = map(int, str(today).split("-"))
        if t_month > month:
            t_year = year - 1
        elif t_month == month:
            if t_day > day:
                t_year = year - 1
            else:
                t_year = year
        else:
            t_year = year
        
    else:
        t_year = year
    
    return dt.datetime(year=t_year, month=t_month, day=t_day)