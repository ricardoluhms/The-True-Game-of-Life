#%%
### set system path
import os
import sys
import tqdm
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modules.person import Person_Life
import pandas as pd
### simulate generation of young adults
population = 1000
people_list = {}
year = 2024
if population is None:
    population = 1000

city_history_df_list = []
for _ in tqdm.tqdm(range(population)):
    current_person = Person_Life(age_range='Elder', current_year= year)

    current_person.generate_past_events()
    ### retrieve the last history of the person and the unique_name_id
    temp_history = current_person.history_df.iloc[-1].copy()
    unique_name_id = temp_history['unique_name_id']
    people_list[unique_name_id] = current_person
    city_history_df_list.append(current_person.history_df)
    #print(current_person.history_df.shape, len(current_person.history_df.columns))

city_history_df = pd.concat(city_history_df_list, axis=0)
#%%
### check number of deaths
print("Number of Deaths",city_history_df["death"].sum(),
      " out of ", len(city_history_df["unique_name_id"].unique()), " people")

### average age at death per gender
death_filter = city_history_df["death"] == 1
average_age_at_death = city_history_df[death_filter].groupby("gender").mean()["age"]
print("Average age at death by gender")
display(average_age_at_death.reset_index())

### check later how to handle someone that was created with Age X and died at Age X-Y

### check how many raise event are there for each person
events_type_mean_per_person = city_history_df[["unique_name_id","event"]].reset_index().\
                                            groupby(["unique_name_id","event"]).\
                                            count().reset_index()
### 
events_type_mean = round(events_type_mean_per_person.groupby("event").mean(),2)
print("Mean number of events per person")
display(events_type_mean)
### check gender distribution

gender_dist = city_history_df[["unique_name_id","gender"]].\
                                        drop_duplicates().\
                                        groupby("gender").count()
print("Gender distribution")
display(gender_dist.reset_index())

### filter by year
filter_year = city_history_df["year"] == year

### check age and career distribution
unique_person_carreer_by_age = city_history_df[filter_year].\
    groupby(["age", "career"]).\
    count()["unique_name_year_event_id"].\
    reset_index()
unique_person_carreer_by_age_piv = pd.pivot(unique_person_carreer_by_age, index="age", 
             columns="career", 
             values="unique_name_year_event_id")
unique_person_carreer_by_age_piv.fillna("", inplace=True)

print("Unique person career by age")
display(unique_person_carreer_by_age_piv)

# %%
### check income distribution - check negative values
### drop pocket money and part time jobs
#filter_income = city_history_df["income"] > 0
#valid_career = ['Part Time', 'Medium', 'Base', 'High','Very High']
valid_career = [ 'Medium', 'Base', 'High','Very High']
filter_career = city_history_df["career"].isin(valid_career)
#city_history_df_filter = city_history_df[filter_income & filter_career]
city_history_df_filter = city_history_df.copy()

a = city_history_df_filter["income"].fillna(0)
b = city_history_df_filter["age"]
### plot income vs age
import matplotlib.pyplot as plt
plt.hist(a, bins=50)
plt.show()

plt.scatter(b, a)
### check low income


# %%
