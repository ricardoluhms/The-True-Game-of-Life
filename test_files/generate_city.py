#%%
### remove Future Warning from pandas
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from modules.city import City # , 
import pandas as pd
# Create a city
#%%

city = City("Boludos City",population=2, current_year=1950, mode='default')

city.age_up()
city.age_up()

#%%
city.age_up()

# %%
temp_list = []
for pep in city.people:
    temp_list.append(pep.history_df)
city.history_df = pd.concat(temp_list)
a = city.history_df
### check duplicated events in update_history
### check negative values in income - working on it
### check for loan term 0 even if a loan is taken - working on it
### check future career issues - working it

#%%
