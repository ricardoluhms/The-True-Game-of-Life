#%%

### set the path GMl to the system path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.city import City
from modules.person import Person_Life
from modules.gml_constants import AGE_RANGES
import numpy as np

city = City("Boludos City",population=0, current_year=1950, mode='testing')
#%%
### simulate generation of young adults
population = 1
people_list = {}
year = 1950
if population is None:
    population = 1
for _ in range(population):
    current_person = Person_Life(age_range='Young Adult', current_year= year)

    ### a random max age to a teenager
    max_age = np.random.randint(AGE_RANGES['Teenager'][0],AGE_RANGES['Teenager'][1])

    current_person.teenager_life(max_age)
    ### retrieve the last history of the person and the unique_name_id
    temp_history = current_person.history_df.iloc[-1].copy()
    unique_name_id = temp_history['unique_name_id']
    people_list[unique_name_id] = current_person