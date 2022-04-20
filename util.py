# Convert to decimal year
import datetime
def year_fraction(date):
    start = datetime.date(date.year, 1, 1).toordinal()
    year_length = datetime.date(date.year+1, 1, 1).toordinal() - start
    return date.year + float(date.toordinal() - start) / year_length

from datetime import datetime
def datetime2year(dt): 
    year_part = dt - datetime(year=dt.year, month=1, day=1)
    year_length = (
        datetime(year=dt.year + 1, month=1, day=1)
        - datetime(year=dt.year, month=1, day=1)
    )
    return dt.year + year_part / year_length


# Convert from decimal year
def decyear_todate(decyear):
    from datetime import datetime, timedelta
    year = int(decyear)
    rem = decyear - year
    base = datetime(year, 1, 1)
    return(base + timedelta(seconds=(base.replace(year=base.year + 1) - base).total_seconds() * rem))
    
