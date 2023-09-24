#%%
### remove Future Warning from pandas
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from main import Person_Life, City# , Starter_Data_Person
import pandas as pd
# Create a city
#%%
city = City("Boludos City",population=10, current_year=1950)

temp_list = []
for pep in city.people:
    temp_list.append(pep.history_df)
city.history_df = pd.concat(temp_list)
# print(len(city.history_df["unique_name_id"].unique()))
# print()
# print()

# cols = ["career","spender_prof","age","unique_name_id"]
# city.history_df[cols].sort_values(by="age",ascending=False).drop_duplicates().groupby(["career","spender_prof"]).count()
# #%%
# city.history_df[cols].sort_values(by="age",ascending=False).drop_duplicates().groupby(["career","spender_prof","age"]).count()

#city.age_up()

# %%
city.age_up()
# %%
### check duplicated events in update_history

### check negative values in income
#%%

# %%
