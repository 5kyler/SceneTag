#-*- coding: utf-8 -*-

# second: time (sec)
# frame_num: frame_num ( 1 ~ )
# time_stamp: HH:MM:SS.ssss
# time_code: HH:MM:SS;Frame

from datetime import timedelta


class TimeConverter:

    def __init__(self, frame_rate):
        self.frame_rate = frame_rate
        self.td = timedelta(0)
        self.is_set = False

    # Setter Section
    def set_second(self, seconds):
        self.td = timedelta(seconds=seconds)
        self.is_set = True

    def set_framenum(self, framenum):
        self.td = timedelta(seconds=framenum / self.frame_rate)
        self.is_set = True

    def set_timestamp(self, timestamp):
        pns = timestamp.split(':')
        seconds = 0
        for pn in pns:
            seconds *= 60
            seconds += float(pn)
        self.td = timedelta(seconds=seconds)
        self.is_set = True

    def set_timecode(self, timecode):
        pfns = timecode.split(';')
        pns = pfns[0].split(':')
        seconds = 0
        for pn in pns:
            seconds *= 60
            seconds += float(pn)

        seconds += int(pfns[1]) / self.frame_rate

        self.td = timedelta(seconds=seconds)
        self.is_set = True

    # Getter Section
    def get_seconds(self):
        if self.is_set:
            return self.td.total_seconds()
        else:
            return 0

    def get_framenum(self):
        if self.is_set:
            return int(round(self.td.total_seconds() * self.frame_rate))
        else:
            return 0

    def get_timestamp(self):
        if self.is_set:
            return str(self.td)
        else:
            return ''

    def get_timecode(self):
        if self.is_set:
            seconds = self.td.total_seconds()
            r_seconds = int(seconds)
            msec = seconds - r_seconds
            frame_num = int(round(msec * self.frame_rate))
            new_td = timedelta(seconds=int(self.td.total_seconds()))
            return str(new_td) + ';' + str(frame_num)
        else:
            return ''


def url_to_filepath(url):
    return 