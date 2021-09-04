import os
import glob
from re import A
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow.keras.backend as K
import tensorflow.compat.v1 as tf
import argparse
from datetime import datetime
import sys
sys.path.insert(1, './Data_processing')
from sql_util import create_connection, execute_query, execute_read_query




tf.disable_v2_behavior()
# initialise tensorflow
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
tf.Session(config=config)

# initialise KERAS_BACKEND
K.set_image_data_format('channels_last')
channel_axis = -1

# initialise os environment
os.environ['KERAS_BACKEND'] = 'tensorflow'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'


def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))


parser = argparse.ArgumentParser()
parser.add_argument("--model_name",
                    help="name of model",
                    default='UV_GAN_1'
                    )
parser.add_argument("--input_data",
                    help="data to input into model",
                    default='aia.np_path_normal'
                    )
parser.add_argument("--test_on_all",
                    help="if set run on all data (not just testing set)",
                    action='store_true'
                    )
parser.add_argument("--display_iter",
                    help="number of iterations between each test",
                    type=int,
                    default=20000
                    )
parser.add_argument("--start_iter",
                    help="Which iteration to start from",
                    type=int,
                    default=0
                    )
parser.add_argument("--max_iter",
                    help="total number of iterations",
                    type=int,
                    default=500000
                    )
args = parser.parse_args()


# connect to db
connection = create_connection("./image.db")

# set parameters
SLEEP_TIME = 1000
DISPLAY_ITER = args.display_iter
START_ITER = args.start_iter
if START_ITER == 0:
    START_ITER = DISPLAY_ITER
MAX_ITER = args.max_iter


ISIZE = 1024  # input size
NC_IN = 1  # number of channels in the output
NC_OUT = 1  # number of channels in the input
BATCH_SIZE = 1  # batch size

input_data = args.input_data
sql_table = input_data.split(".")[0]
get_input_data = f"""
SELECT
    {input_data},
    {sql_table}.date    
FROM
    {sql_table}
"""
input_data_paths = (execute_read_query(connection, get_input_data))


model_name = args.model_name
trial_name = f"{model_name}_on_{sql_table.upper()}"

test_months = (11, 12)


def get_month(date_str):
    date = datetime.strptime(date_str, "%Y.%m.%d_%H:%M:%S")
    return date.month


def grab_data(data_paths):
    for path, date in data_paths:
        if path == "NULL":
            continue
        if (not args.test_on_all) and (get_month(date) not in test_months):
            continue
        
        yield (path, date)

# during training, the model was saved every DISPLAY_ITER steps
# as such, test every DISPLAY_ITER.
ITER = START_ITER

while ITER <= MAX_ITER:
    SITER = '%07d' % ITER  # string representing the itteration

    # file path for the model of current itteration
    MODEL_NAME = f'./Models/{model_name}/ITER{SITER}.h5'

    # # file path to save the generated outputs from INPUT1 (nearside)
    # SAVE_PATH1 = RESULT_PATH1 + 'ITER' + SITER + '/'
    # os.mkdir(SAVE_PATH1) if not os.path.exists(SAVE_PATH1) else None

    EX = 0
    while EX < 1:
        if os.path.exists(MODEL_NAME):
            print('Starting Iter ' + str(ITER) + ' ...')
            EX = 1
        else:
            raise Exception('no model found at: ' + MODEL_NAME)

    # load the model
    MODEL = load_model(MODEL_NAME, compile=False)

    REAL_A = MODEL.input
    FAKE_B = MODEL.output
    # function that evaluates the model
    NET_G_GENERATE = K.function([REAL_A], [FAKE_B])

    output_folder = f"Data/{trial_name}/ITER{SITER}/"
    os.makedirs(output_folder) if not os.path.exists(output_folder) else None


    add_column_to_table = f"""
    ALTER TABLE
        {sql_table}
    ADD
        {model_name}_iter_{SITER}_path VARCHAR(255)
    """
    execute_query(connection, add_column_to_table)
    

    # generates the output (HMI) based on input image (A)
    def NET_G_GEN(A):
        output = [NET_G_GENERATE([A[i:i+1]])[0] for i in range(A.shape[0])]
        return np.concatenate(output, axis=0)
    
    data_paths = grab_data(input_data_paths)
    for path, date in data_paths:
        IMG = np.load(path) * 2 - 1
        save_name = f"{output_folder}MAG_{date}"

        # reshapes IMG tensor to (BATCH_SIZE, ISIZE, ISIZE, NC_IN)
        IMG.shape = (BATCH_SIZE, ISIZE, ISIZE, NC_IN)
        # output image (generated HMI)
        FAKE = NET_G_GEN(IMG)
        FAKE = FAKE[0]
        if NC_IN == 1:
            FAKE.shape = (ISIZE, ISIZE)
        else:
            FAKE.shape = (ISIZE, ISIZE, NC_OUT)
        np.save(save_name, FAKE)

        update_table = f"""
            UPDATE
                {sql_table}
            SET
                {model_name}_iter_{SITER}_path = "{save_name}"
            WHERE
                date = "{date}"
            """
        execute_query(connection, update_table)


    del MODEL
    K.clear_session()

    ITER += DISPLAY_ITER
