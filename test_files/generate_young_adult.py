#%%
### set system path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modules.person import Person_Life
import pandas as pd
### simulate generation of young adults
population = 100
people_list = {}
year = 1950
if population is None:
    population = 1000

city_history_df_list = []
for _ in range(population):
    current_person = Person_Life(age_range='Young Adult', current_year= year)

    current_person.generate_past_events()
    ### retrieve the last history of the person and the unique_name_id
    temp_history = current_person.history_df.iloc[-1].copy()
    unique_name_id = temp_history['unique_name_id']
    people_list[unique_name_id] = current_person
    city_history_df_list.append(current_person.history_df)
    #print(current_person.history_df.shape, len(current_person.history_df.columns))

city_history_df = pd.concat(city_history_df_list, axis=0)
# %%
### 
city_history_df["gender"].isna().sum()

# %%
### filter by year
filter_year = city_history_df["year"] == year

### check age and career distribution
a = city_history_df[filter_year].\
    groupby(["age", "career"]).\
    count()["unique_name_year_event_id"].\
    reset_index()
b = pd.pivot(a, index="age", 
             columns="career", 
             values="unique_name_year_event_id")
b.fillna("", inplace=True)
b
# %%
