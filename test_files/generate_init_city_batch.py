#%%
### set system path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
### remove Future Warning from pandas
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from modules.city import City
import pandas as pd
### Add logging to the project
import logging
from tqdm import tqdm

### Start Parameters
batch_size = 500
population = 40000
current_year = 1950
today = pd.Timestamp("today").strftime("%Y_%m_%d") ### this will not include H and M to make merge  easier



years = 100
num_batches = population // batch_size

file_names = []
for i in range(num_batches):
    file_name = f'test_city_{population}_init_pop_{years}_years_{current_year}_start_year_{today}_batch_{i}'
    csv_file = f'data/batch/{file_name}.csv'
    log_file = f'code_logs/batch/{file_name}.log'

    logging.basicConfig(level=logging.INFO, 
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        datefmt='%I:%M:%S %p',
                        handlers=[logging.FileHandler(log_file, 
                                                    encoding='utf-8')])
    city = City("Test City",population=batch_size, current_year=1950, mode='default')
    city.history.to_csv(csv_file, index=False)
    file_names.append(csv_file)

# %%
