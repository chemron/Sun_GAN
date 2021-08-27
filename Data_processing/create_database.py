import sqlite3
from sqlite3 import Error
import numpy as np
from datetime import datetime, timedelta
import os
from bisect import bisect_left
import sys
sys.path.insert(1, './Data_collection')
from get_equivalent_time import get_stereo_time


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


def get_entry(mode, date):
    """ 
    returns (fits_path, np_path, date)
    if mode is 'phase_map', otherwise returns
    (fits_path, np_path, np_path_normal, date)

    """
    fits_path = f"Data/fits_{mode}/{mode.upper()}_{date}.fits"
    if not os.path.exists(fits_path):
        print(f"path: {fits_path} does not exist")
        fits_path = "NULL"

    np_path = f"Data/np_{mode}/{mode.upper()}_{date}.npy"
    if not os.path.exists(np_path):
        print(f"path: {np_path} does not exist")
        np_path = "NULL"

    if mode == 'phase_map':
        return f'("{fits_path}", "{np_path}", "{date}")'
    
    np_path_normal = f"Data/np_{mode.upper()}_normalised/{mode}_{date}.npy"
    if not os.path.exists(np_path_normal):
        print(f"path: {np_path_normal} does not exist")
        np_path_normal = "NULL"

    return f'("{fits_path}", "{np_path}", "{np_path_normal}", "{date}")'



def get_closest(dates, date):
    pos = bisect_left(dates, date)
    if pos == 0:
        return dates[0]
    if pos == len(dates):
        return dates[-1]
    before = dates[pos - 1]
    after = dates[pos]
    if after - date < date - before:
        return after
    else:
        return before



connection = create_connection("./image.db")

create_AIA_table = """
CREATE TABLE IF NOT EXISTS aia(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fits_path VARCHAR(255) NOT NULL,
    np_path VARCHAR(255),
    np_path_normal VARCHAR(255),
    date TEXT NOT NULL,
    hmi_id INTEGER,
    FOREIGN KEY (hmi_id) REFERENCES hmi (id)
    );
"""
execute_query(connection, create_AIA_table)


create_HMI_table = """
CREATE TABLE IF NOT EXISTS hmi(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fits_path VARCHAR(255) NOT NULL,
    np_path VARCHAR(255),
    np_path_normal VARCHAR(255),
    date TEXT NOT NULL,
    aia_id INTEGER,
    FOREIGN KEY (aia_id) REFERENCES aia (id)
    );
"""
execute_query(connection, create_HMI_table)


create_EUVI_table ="""
CREATE TABLE IF NOT EXISTS euvi(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fits_path VARCHAR(255) NOT NULL,
    np_path VARCHAR(255),
    np_path_normal VARCHAR(255),
    date TEXT NOT NULL,
    phase_map_id INTEGER,
    FOREIGN KEY (phase_map_id) REFERENCES phase_map (id)
    );
"""
execute_query(connection, create_EUVI_table)


create_phase_map_table ="""
CREATE TABLE IF NOT EXISTS phase_map(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fits_path VARCHAR(255) NOT NULL,
    np_path VARCHAR(255),
    projected_path VARCHAR(255),
    date TEXT NOT NULL,
    euvi_id INTEGER,
    FOREIGN KEY (euvi_id) REFERENCES euvi (id)
    );
"""
execute_query(connection, create_phase_map_table)


# insert data into database
for mode in ("AIA", "HMI", "EUVI", "phase_map"):
    insert_data = ""
    if mode == "phase_map":
        insert_data += \
        f"""
        INSERT INTO
            {mode} (fits_path, np_path, date)
        VALUES"""
    else:
        insert_data += \
        f"""
        INSERT INTO
            {mode} (fits_path, np_path, np_path_normal, date)
        VALUES"""
    
    dates = np.load(f"Data/np_objects/{mode}_dates.npy", allow_pickle=True)
    date_strings = [date.strftime("%Y.%m.%d_%H:%M:%S") for date in dates]
    for date in date_strings:
        insert_data += \
        f"""
            {get_entry(mode, date)},"""
    insert_data = insert_data[:-1] + ";\n"
    execute_query(connection, insert_data)



insert_hmi_id_into_aia = """
UPDATE
    aia
SET
    hmi_id = (
        SELECT id
        FROM hmi
        WHERE hmi.date = aia.date
        )
"""
execute_query(connection, insert_hmi_id_into_aia)


insert_aia_id_into_hmi = """
UPDATE
    hmi
SET
    aia_id = (
        SELECT id
        FROM aia
        WHERE aia.hmi_id = hmi.id
        )
"""
execute_query(connection, insert_aia_id_into_hmi)


# get matching phase map and euvi dates
get_phase_map_dates = "SELECT date FROM phase_map"
phase_map_dates = execute_read_query(connection, get_phase_map_dates)
get_euvi_dates = "SELECT date FROM euvi"
euvi_dates = execute_read_query(connection, get_euvi_dates)

phase_map_dates = np.sort(np.array([datetime.strptime(date[0], "%Y.%m.%d_%H:%M:%S") for date in phase_map_dates]))
euvi_dates = np.sort(np.array([datetime.strptime(date[0], "%Y.%m.%d_%H:%M:%S") for date in euvi_dates]))

euvi_phase_map_dates = []
for phase_map_date in phase_map_dates:
    ideal_euvi_date = get_stereo_time(phase_map_date)
    actual_euvi_date = get_closest(euvi_dates, ideal_euvi_date)
    difference = abs(ideal_euvi_date - actual_euvi_date)
    if  difference > timedelta(hours=2):
        print(f"Closest match is off by {difference}")
        continue
    else:
        euvi_phase_map_dates.append((actual_euvi_date.strftime("%Y.%m.%d_%H:%M:%S"), phase_map_date.strftime("%Y.%m.%d_%H:%M:%S")))


# update euvi and phasemap connecting ids
for euvi_date, phase_map_date in euvi_phase_map_dates:
    insert_phase_map_id_into_hmi = f"""
    UPDATE
        euvi
    SET
        phase_map_id = (
            SELECT id
            FROM phase_map
            WHERE phase_map.date = "{phase_map_date}"
            )
    WHERE
        euvi.date = "{euvi_date}"
    """ 
    execute_query(connection, insert_phase_map_id_into_hmi)

    insert_euvi_id_into_phase_map = f"""
    UPDATE
        phase_map
    SET
        euvi_id = (
            SELECT id
            FROM euvi
            WHERE euvi.date = "{euvi_date}"
            )
    WHERE
        phase_map.date = "{phase_map_date}"
    """ 
    execute_query(connection, insert_euvi_id_into_phase_map)

