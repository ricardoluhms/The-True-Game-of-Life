#%%
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from main import Person_Life, Person_Functions

df = pd.read_csv("single_person_history_copy.csv")

p = Person_Functions()

#%%
temp_history_17 = df.iloc[0]
temp_history_18 = df.iloc[1]

print(p.get_a_car(finance_option=None,temp_history=temp_history_18))
# %%
assert p.get_a_car(finance_option=None,temp_history=temp_history_18)=="Not Eligible to Buy a Car (Age Restriction)"
print("This is a Test")
# %%

print(p.get_a_car(finance_option=None,temp_history=temp_history_18))

# %%
