import os
from datetime import datetime
import numpy as np
import cv2
from sql_util import create_connection, execute_query, execute_read_query


q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
percentiles = np.load(f"Data/np_objects/phase_map_percentiles.npy").T
dates = np.load(f"Data/np_objects/phase_map_dates.npy", allow_pickle=True)
w = h = 1024

abs_max = abs(np.max(percentiles[-1]))
abs_min = abs(np.min(percentiles[0]))

print(f"Absolute max: {abs_max}, Absolute min: {abs_min}")

clip_max = np.max([abs_max, -abs_min])
# to get data between -0.5 and 0.5, and centered about 0
noramlisation_factor = 1.0/(clip_max * 2)

def insert_into_db(connection, path, id):
    insert_path = f"""
    UPDATE
        phase_map
    SET
        np_path_normal = "{path}"
    WHERE
        id = {id}
    """
    execute_query(connection, insert_path)

get_phase_map_paths = """
SELECT
    np_path,
    date,
    id
FROM
    phase_map
"""

connection = create_connection("./image.db")
output = execute_read_query(connection, get_phase_map_paths)

output_dir = "Data/np_phase_map_normalised/"

# normal percentiles and corresponding dates
normal_p = []
normal_d = []


for phase_map_np_path, date, id in output:
    img = np.load(phase_map_np_path)

    img = img * noramlisation_factor
    img += 0.5
    try:
        img = cv2.resize(img, dsize=(w, h))
        save_name = f"{output_dir}PHASE_MAP_{date}"
        np.save(save_name, img)
        insert_into_db(connection, save_name, id)
        percentiles = np.nanpercentile(img, q)
        if percentiles is not None:
            normal_p.append(percentiles)
            normal_d.append(datetime.strptime(date, "%Y.%m.%d_%H:%M:%S"))
    except cv2.error as e:
        print(f"{date}: {e}")
    except IndexError as e:
        print(f"{date}: {e}")


percentile_dir = "Data/np_objects/"
os.makedirs(percentile_dir) if not os.path.exists(percentile_dir) else None

np.save(f"{percentile_dir}phase_map_normal_percentiles", normal_p)
np.save(f"{percentile_dir}phase_map_normal_dates", normal_d)
