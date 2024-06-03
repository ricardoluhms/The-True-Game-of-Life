#%%
### import modules
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modules.dataframe_mode import *

#%%40000
### create a complete city
df3 = time_function(generate_complete_city, 100, "Young Adult", 500, 1950,True)
#%% 
# check if folder exists
if not os.path.exists("C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/new_pipeline"):
    os.makedirs("C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/new_pipeline")
    
df3.to_csv("C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/new_pipeline/complete_city_test.csv", index=False)
# %%
