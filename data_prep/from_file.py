#%%
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
### read data from test_files
import pandas as pd

folder = os.path.dirname(__file__)
root_folder = os.path.abspath(os.path.join(folder, os.pardir))
file = os.path.join(root_folder, 
                    'test_files', 
                    'data', 
                    'test_city_500_init_pop_100_years_1950_start_year_2024_03_15_13_30.csv')
data = pd.read_csv(file,low_memory=False) 

#%%
### retrieve the current year from the data
current_year = data['year'].max()
### retrieve the population from the data
year_crit = data['year'] == current_year
is_alive = ~data['event'].str.lower().str.contains('death')
population = len(data[year_crit & is_alive])

history = data.copy()

### get deceased people and each person unique id is the key and the value is None
deceased_people = history[~is_alive]['unique_name_id'].unique()
deceased_people = {person: None for person in deceased_people}

# to add
#self.event = "Created"
#self.financial_institution = finance_institution

### generate person object from the data
for person_id in data["unique_name_id"].unique():
    



### Person File main inputs to load the person object
# gender:str =None, 
# first_name:str = None, 
# last_name:str = None, 
# current_year:int = None
# age_range: str = None, married: bool = False,
# parent_name_id_A: str = None
# parent_name_id_B: str = None
# children_name_id:list = []
# career: str = None
# age_range: str = None
# income: float = None
# loan: float = None
# loan_term: int = None
# balance: float = None
# married: bool = False
# parent_name_id_A: str = None
# parent_name_id_B: str = None
# children_name_id: list = []

#%%

person_data = data[data["unique_name_id"] == "Judy_Bell Evans_4550"]

### current year
current_year = person_data['year'].max()
### retrieve the population from the data
year_crit = person_data['year'] == current_year
last_event = person_data[year_crit].iloc[-1]
last_event.to_dict()




# %%
