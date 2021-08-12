from bisect import bisect_left
import numpy as np
from datetime import timedelta

phase_times, stereo_times = np.load("/home/csmi0005/Mona0028/adonea/" +
                                    "cameron/Honours/data_collection/" +
                                    "DATA/np_objects/phase_stereo_times.npy",
                                    allow_pickle=True).T


def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            + timedelta(hours=t.minute//30))


def get_stereo_time(phase_time):
    pos = bisect_left(phase_times, phase_time)
    if pos == 0:
        return stereo_times[0]
    if pos == len(phase_times):
        return stereo_times[-1]
    before = phase_times[pos - 1]
    after = phase_times[pos]
    if abs(after - phase_time) < abs(phase_time - before):
        return stereo_times[pos]
    else:
        return stereo_times[pos-1]


def get_phase_time(stereo_time):
    pos = bisect_left(stereo_times, stereo_time)
    if pos == 0:
        return phase_times[0]
    if pos == len(stereo_times):
        return phase_times[-1]
    before = stereo_times[pos - 1]
    after = stereo_times[pos]
    if abs(after - stereo_time) < abs(stereo_time - before):
        return phase_times[pos]
    else:
        return phase_times[pos-1]
