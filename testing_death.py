#%%
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from person import Person_Life
from city import City

###Create a city
city = City("Boludos City",population=2, current_year=1950, mode='testing')

#%%
person = Person_Life()

print(person.history_df['cause_of_death'])


# %%
