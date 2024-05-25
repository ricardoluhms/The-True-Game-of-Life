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
file_name_batch= "test_city_40000_init_pop_100_years_1950_start_year_2024_03_15_batch"
data_batch_folder = "data\\batch"
### check batch folder and count the number of files that start with the file_name_batch
folder = os.path.join(os.path.dirname(__file__), '..', 'test_files', data_batch_folder)
files = os.listdir(folder)
batch_files = [file for file in files if file.startswith(file_name_batch)]

#%%
df_list = []
for file_name_csv in batch_files:
    file_path = f'{folder}\\{file_name_csv}'
    data = pd.read_csv(file_path,low_memory=False)
    df_list.append(data)

data = pd.concat(df_list, axis=0, ignore_index=True)
#%%
### save the merged file
merged_file = f'{file_name_batch}_merged.csv'
merged_file_path = f'{folder}\\{merged_file}'
data.to_csv(merged_file_path, index=False)

# %%
