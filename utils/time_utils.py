from datetime import datetime
from datetime import time
from datetime import timedelta


def time_this(func):
    def calc_time(*args, **kwargs):
        before = datetime.now()
        n_func = func(*args, **kwargs)
        after = datetime.now()
        print("Function {} elapsed time: {}s".format(func.__name__, after - before))
        return n_func
    return calc_time


def round_datetime(t, round_upper = False):
    try:
        small_delta = int(t.split('.')[-1].split('+')[0])
    except:
        small_delta = 0
    t = t.split('.')[0].split('+')[0]
    parsed_time = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S")
    if round_upper == True and small_delta > 0:
        parsed_time += timedelta(seconds=1)
    return parsed_time


def round_time(t, round_upper = False):
    try:
        small_delta = int(t.split('.')[-1].split('+')[0])
    except:
        small_delta = 0
    t = t.split('.')[0].split('+')[0]
    hours, minutes, seconds = t.split(':')
    parsed_time = timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
    if round_upper == True and small_delta > 0:
        parsed_time += timedelta(seconds=1)
    return parsed_time


def to_standard_ffmpeg_format(total_seconds):
    hours = int(total_seconds // 3600)
    minutes = int(total_seconds // 60 % 60)
    seconds = int(total_seconds % 60)
    ffmpeg_time_format = '{}:{}:{}'.format("0" + str(hours) if hours < 10 else hours,
                                           "0" + str(minutes) if minutes < 10 else minutes,
                                           "0" + str(seconds) if seconds < 10 else seconds)
    return ffmpeg_time_format