#%%
### remove Future Warning from pandas
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from main import Person_Life, City,Person_Functions# , Starter_Data_Person

import pandas as pd
# Create a city
#%%
city = City("Boludos City",population=2, current_year=1950)

person = 
### Creates a Marriage Candidate


city.age_up()
city.age_up()

#%%
city.age_up()

#%%
### Mariage Tests

### Test someone not of age

### Test someone who is already married

### Test Same Sex Marriage




### Maybe make people that suit the above needs and add them to the city and test with them








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
