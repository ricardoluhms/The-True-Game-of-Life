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
### age up the city 10 years
for i in range(10):
    print("### Ageing up the city ###", city.current_year)
    city.age_up()
    ### average

# for i in tqdm.tqdm(range(300)):
#     city.age_up()
#     ### average

# %%

### Task 1 - Test the death within the city:
### are they dying and being removed from the city?


#Check if people are dying, see what it looks like when the the city ages up and the people die

### check number of deaths
print("Number of Deaths",city.history["death"].sum(),
      " out of ", len(city.history["unique_name_id"].unique()), " people")

dead_people = city.deceased_people

alive_people = city.people_obj_dict

for person in dead_people:
    if person in alive_people:
        print("Error, dead person still in the city")
    else:
        print("Everything is working as intended")
    

#Save the people that died to a list, iterate throught he list and figure out if they are still in the city




#%%