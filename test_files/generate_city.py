#%%
### set system path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
### remove Future Warning from pandas
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from modules.city import City # , 
import pandas as pd
### Add logging to the project
import logging
from tqdm import tqdm

### Start Parameters
population = 10
current_year = 1950
mode = 'default'
### include hh mm ss in the file name
today = pd.Timestamp("today").strftime("%Y_%m_%d_%H_%M")
years = 100
file_name = f'test_city_{population}_init_pop_{years}_years_{current_year}_start_year_{today}'
csv_file = f'data/{file_name}.csv'
log_file = f'code_logs/{file_name}.log'

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    datefmt='%I:%M:%S %p',
                    handlers=[logging.FileHandler(log_file, 
                                                  encoding='utf-8')])

# Create a city
city = City("Test City",population=population, current_year=1950, mode='default')
#print(city.history)

### age up the city 100 years
### 200 minutes to run 100 years 
for i in tqdm(range(years)):
    city.age_up()

### rewrite the save to use current date as file name
city.history.to_csv(csv_file, index=False)

# %%

# create a dump file to remove older population entries

### Task 1 - Test the death within the city:
### are they dying and being removed from the city?

### Task 2 - Test New Borns:
### are they being added to the city?
### are they aging properly?

### Task 3 - check duplicated events in update_history

### Task 4 - check negative values in income

### Task 5 - check student loans - check for loan term 0 even if a loan is taken

### Task 6 -  future career issues - is everyone getting a career? Salary increase?

### Functionality - How to handle loan payments? (Done)

### Functionality - Age up the city X years (Done)

### Functionality - Create a city from a csv (Done)