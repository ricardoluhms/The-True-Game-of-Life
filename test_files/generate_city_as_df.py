#%%
### import modules
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modules.dataframe_mode import *


#%%40000
df3 = time_function(generate_complete_city, 100, "Young Adult", 20000, 1950)
#%% check if folder exists
if not os.path.exists("C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/new_pipeline"):
    os.makedirs("C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/new_pipeline")
    
df3.to_csv("C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/new_pipeline/complete_city_test.csv", index=False)
#%%
population_histogram(df3)

#death_count_by_age(df3)