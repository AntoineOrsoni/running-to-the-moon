import datetime
import time

def get_current_time() -> str:
    t = time.localtime()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", t)

    return current_time

def get_week_number(timestamp: str) -> int:
    time_splitted = timestamp.split()[0].split('-')

    year = int(time_splitted[0])
    month = int(time_splitted[1])
    day = int(time_splitted[2])

    return datetime.date(year, month, day).isocalendar()[1]