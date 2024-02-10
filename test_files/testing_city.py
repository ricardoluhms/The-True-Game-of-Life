#%%
### set system path
import os
import sys
import tqdm
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#%%
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from modules.person import Person_Life
from modules.city import City

###Create a city
city = City("Boludos City",population=2, current_year=1950, mode='testing')

#%%
person = Person_Life()

print(person.history_df['cause_of_death'])


### Task 1 - Test the death within the city:
### are they dying and being removed from the city?

### Task 2 - Test New Borns:
### are they being added to the city?
### are they aging properly?

### Task 3 - check duplicated events in update_history

### Task 4 - check negative values in income

### Task 5 - check student loans - check for loan term 0 even if a loan is taken

### Task 6 -  future career issues - is everyone getting a career? Salary increase?

### Functionality - How to handle loan payments?

### Functionality - Age up the city X years

### Functionality - Create a city from a csv





# %%
