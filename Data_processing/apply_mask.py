import glob
import numpy as np
import argparse
from sql_util import create_connection, execute_query, execute_read_query

size = 1024


parser = argparse.ArgumentParser()
parser.add_argument("--data",
                  nargs='+',
                  help="data to apply mask to (sql_table.column)")
data_types = parser.parse_args().data

connection = create_connection("./image.db")


def get_mask(size):
    w = h = size
    center = (int(w/2), int(h/2))
    radius = w/2 + 1
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center <= radius
    return mask


def apply_mask(filename):
    arr = np.load(filename)
    arr = np.nan_to_num(arr)
    arr = mask * arr
    np.save(filename, arr)


mask = get_mask(size)
for data in data_types:
    print(data)
    table, col = data.split(".")

    # query db
    get_data = f"""
    SELECT
        {col}
    FROM
        {table}
    """

    data_paths = (execute_read_query(connection, get_data))

    print(data_paths)
    for path in data_paths:
        path = path[0]
        if path not in [None, "NULL"]:
            apply_mask(path)
