#%%
### set system path
import os
import sys
import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

### remove Future Warning from pandas
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from modules.city import City # , 
import pandas as pd
import tqdm

# Create a city
#%%

city = City("Test City",population=1000, current_year=1950, mode='default')
#print(city.history)
#%%
### age up the city 100 years
for i in range(100):
    print("### Ageing up the city ###", city.current_year)
    city.age_up()
    ### average

# for i in tqdm.tqdm(range(300)):
#     city.age_up()
#     ### average
#%%
city.history.to_csv('test_city_1000_init_pop_100_years_1950_start_year_2024_02_11.csv')
# %%

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