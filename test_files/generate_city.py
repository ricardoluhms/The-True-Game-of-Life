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

city = City("Test City",population=4, current_year=2000, mode='default')
#print(city.history)
#%%
### age up the city 100 years
for i in range(100):
    print("### Ageing up the city ###", city.current_year)

    city.age_up()
    ### average

# for i in tqdm.tqdm(range(300)):
#     city.age_up()
#     ### average
#%%
city.history.to_csv('test_city_loand_payment_spender_profile1.csv')
# %%
