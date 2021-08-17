#!/usr/bin/env python3
# Python code for retrieving SDO-HMI/AIA data
from sunpy.net import Fido, attrs as a

from datetime import datetime, timedelta
import astropy.units as u  # for AIA
import argparse
import numpy as np
import os
import requests
from multiprocessing import Pool, cpu_count
import drms
import time

from requests.exceptions import ConnectionError
from urllib.error import HTTPError


# can make multiple queries and save the details to files based on the AR and
# retrieve the data later


parser = argparse.ArgumentParser()
parser.add_argument("--instruments",
                    nargs="+",
                    help="Download data from these instruments",
                    default=['AIA', 'HMI', 'EUVI']
                    )
parser.add_argument("--start",
                    help="start date for AIA and HMI",
                    default='2010-06-01 00:00:00')
parser.add_argument("--end",
                    help="end date for AIA and HMI",
                    default='2020-01-01 00:00:00')
parser.add_argument("--cadence",
                    help="AIA and HMI cadence in hours",
                    type=int,
                    default=12
                    )
parser.add_argument("--path",
                    help="directory to store data",
                    default='./Data/'
                    )
parser.add_argument("--email",
                    default="csmi0005@student.monash.edu")
args = parser.parse_args()

email = args.email


def get_search_args(instrument: str, wavelength: int,  series: str, segment: str):

    wavelength = wavelength*u.AA
    search_args = []
    if series == "STEREO_A":
        # args for stereo data
        search_args = [
            a.Wavelength(wavelength),
            a.Source(series),
            a.Instrument(instrument),
            a.Sample(12*u.hour)
        ]
    else:
        # args for SDO data
        search_args = [
            a.jsoc.Notify(email),
            a.jsoc.Series(series),
            a.jsoc.Segment(segment),
            a.Sample(12*u.hour)
            ]

        if wavelength != 0:
            search_args.append(a.jsoc.Wavelength(wavelength))

    return search_args


def search_data(s_time, f_time, e_time):
        if e_time > f_time:
            e_time = f_time

        start = s_time.strftime("%Y-%m-%d %H:%M:%S")
        end = e_time.strftime("%Y-%m-%d %H:%M:%S")

        arg = arg_no_time + [a.Time(start, end)]

        res = Fido.search(*arg)
        return res



def get_SDO_data(instrument: str, start: str, end: str, cadence: int,
              path: str, fmt: str, arg_no_time: list):
    
    path = f"{path}fits_{instrument}/"
    # time between searches
    cadence = timedelta(hours=cadence)
    # start time for downloading
    s_time = datetime.fromisoformat(start)
    # time of end of downloading
    f_time = datetime.fromisoformat(end)
    # take data from 8 days at a time
    step_time = timedelta(days=8)
    # time of end of this step:
    e_time = s_time + step_time

    while True:
        res = search_data(s_time, f_time, e_time)
        
        # get response object:
        table = res.tables[0]

        # get time string of final end time of results
        if len(table) == 0:
            print(f"{s_time} to {e_time}: Empty table")
            if e_time >= f_time:
                print("finish on empty table")
                return
            else:
                s_time = e_time
                e_time += step_time
                continue

        # get times:
        times = []

        # slightly different formatting for STEREO and SDO
        # if instrument == "EUVI":
        #         for t in table["Start Time"]:
        #             t = str(t).strip('.000')
        #             # account for leap second in 2016
        #             if t == "2016-12-31 23:59:60":
        #                 time = "2017-01-01 00:00:00"
        #             else:
        #                 time = t
        #             times.append(datetime.strptime(time, fmt))
        # else:
        for t in table["T_REC"]:
            # account for leap second in 2016
            if t == "2016-12-31T23:59:60Z":
                time = "2017-01-01T00:00:00Z"
            else:
                time = t
            times.append(datetime.strptime(time, fmt))
        times = np.array(times)

        index, dates = get_index(times, s_time, e_time, cadence)

        request = get_request(instrument, res, index)

        if request.has_failed():
            s_time = e_time
            e_time += timedelta(days=1)
            continue

        urls = request.urls.url.reindex(index).dropna()

        os.makedirs(path) if not os.path.exists(path) else None

        filenames = []

        for date in  dates:
            if date.hour == 11 or date.hour == 23:
                date += timedelta(hours=1)
            filename = f"{path}{instrument}_{date.year}.{date.month:0>2}." \
                       f"{date.day:0>2}_{date.hour:0>2}:00:00.fits"
            filenames.append(filename)

        n_cpus = min(cpu_count(), 8)
        print(f"downloading {len(urls)} files with {n_cpus} cpus.")
        pool = Pool(n_cpus)
        arg = list(zip(urls, filenames))
        try:
            pool.starmap(download_url, arg)
        except ConnectionError as e:
            print(e)
        except HTTPError as e:
            print(e)
            print("Could not download:")
            print(arg)
        pool.close()
        pool.join()


        # start of next run:
        if e_time >= f_time:
            return

        s_time = e_time
        e_time += step_time


def get_STEREO_data(instrument: str, start: str, end: str, cadence: int,
              path: str, fmt: str, arg_no_time: list):
    
    path = f"{path}fits_{instrument}/"
    # time between searches
    cadence = timedelta(hours=cadence)
    # start time for downloading
    s_time = datetime.fromisoformat(start)
    # time of end of downloading
    f_time = datetime.fromisoformat(end)
    # take data from 8 days at a time
    step_time = timedelta(days=8)
    # time of end of this step:
    e_time = s_time + step_time

    while True:
        res = search_data(s_time, f_time, e_time)

        Fido.fetch(res, path=path)

        # start of next run:
        if e_time >= f_time:
            return

        s_time = e_time
        e_time += step_time



        
def get_index(times, start: datetime, end: datetime, cadence: timedelta):
    # get index and dates of every cadence timestep in times
    index = []
    dates = []
    # current time:
    current = start

    i = 0
    while i < len(times):
        # previous time in times
        p_time = times[i-1]
        # current time in times
        time = times[i]
        if time > current:
            # if the previous time was closer to current:
            if (current - p_time) < (time - current):
                time = p_time
                i = i - 1
            # add the time to the index if close enough
            if (time - current) < timedelta(hours=2):
                index.append(i)
                dates.append(time)
            current += cadence
        i += 1

    return index, dates


def get_request(instrument, res, index):
    if instrument == "EUVI":
        pass
    else:
        # get response
        jsoc_response = list(res.responses)[0]
        # get block (info about response)
        block = jsoc_response.query_args[0]
        # data string
        ds = jsoc_response.client._make_recordset(**block)
        # client for drms
        cd = drms.Client(email=block.get('notify', ''))
        request = cd.export(ds, method='url', protocol='fits')

        print("waiting for request", end="")
        while request.status == 0:
            print(".", end="")
            time.sleep(5)

        print("\ndone")

    return request


def download_url(url, filename):
    print("downloading: ", filename.split("/")[-1])
    # assumes that the last segment after the / represents the file name
    # if url is abc/xyz/file.txt, the file name will be file.txt
    r = requests.get(url, stream=True)
    if r.status_code == requests.codes.ok:
        with open(filename, 'wb') as f:
            for data in r:
                f.write(data)
        return


for instrument in args.instruments:
    # date string format
    if instrument == "AIA":
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        wavelength = 304
        series = 'aia.lev1_euv_12s'
        segment = 'image'
    elif instrument == "HMI":
        fmt = '%Y.%m.%d_%H:%M:%S_TAI'
        wavelength = 0
        series = 'hmi.m_45s'
        segment = "magnetogram"
    elif instrument == "EUVI":
        fmt = "%Y-%m-%d %H:%M:%S"
        wavelength = 304
        series = 'STEREO_A'
        segment = None
    else:
        raise Exception("Only accepts AIA, HMI or EUVI instrument")

    
    # get search args (excluding start/end times)
    arg_no_time = get_search_args(
        instrument=instrument,
        wavelength=wavelength,
        segment=segment,
        series=series
        )

    # get data
    if instrument == "EUVI":    
        get_STEREO_data(instrument=instrument,
            start=args.start,
            end=args.end,
            cadence=args.cadence,
            path=args.path,
            fmt=fmt,
            arg_no_time=arg_no_time)
    
    else:
        get_SDO_data(instrument=instrument,
            start=args.start,
            end=args.end,
            cadence=args.cadence,
            path=args.path,
            fmt=fmt,
            arg_no_time=arg_no_time)