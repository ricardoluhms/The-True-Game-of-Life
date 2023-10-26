#%%
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from main import Person_Life, Person_Functions


person = Person_Life("Male",None,None,current_year=2023, age_range="Baby")

p = Person_Functions()

#%%
### Create a code generates one person and ages up one by one year and check if all the values are correct and life events are correct
for _ in range(20):
    person.age_up()

#%%

history_df = person.history_df

print(history_df)

excel_file_name = "single_person_history.xlsx"  
history_df.to_excel(excel_file_name, index=False)  

print(f"Data exported to {excel_file_name}")
#%%