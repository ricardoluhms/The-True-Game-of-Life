#%%
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
### read data from test_files
import pandas as pd
from modules.city import City

file_path = "C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/batch/test_city_40000_init_pop_100_years_1950_start_year_2024_03_15_batch_merged.csv"
data = pd.read_csv(file_path,low_memory=False)

data2 = data[data['year'] == data["year"].max()]


#%%
city = City(name="test_city", population=1, data=data2.head(5000), mode="from_file")
#
# %%
import tqdm
for i in tqdm.tqdm(range(10)):
    city.age_up()
  

### functionalities backlog
    
### faster age up using city dataframe  and numpy
### it will create temporary columns to store calculations and then drop them
### this will allow for faster calculations and less memory usage
 


# %%
mask = data["unique_name_id"] == "Patricia_Butler_8024"

data[mask]
# %%
mask2 = data2["unique_name_id"] == "Patricia_Butler_8024"

data2[mask2]
# %%
