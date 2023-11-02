#%%
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from main import Person_Life, Person_Functions

df = pd.read_csv("unit_test_table.csv")

p = Person_Functions()

#%%
i =1
#temp_history_17 = df.iloc[0] # person under aged
#temp_history_18 = df.iloc[1] # person has income but not enough balance
#temp_history_18_1 = df.iloc[2] # person has both balance and income for self financing 
#temp_history_18_2 = df.iloc[3] # person has balance but not enough income
#temp_history_18_3 = df.iloc[4] # person has less balance and less income
temp_history_18 = df.iloc[1] #  18 big spender but has a car

print("This persons age:",df.iloc[i,7])
print("This persons income:",df.iloc[i,12])
print("This persons balance:",df.iloc[i,16])

print(p.get_a_car(temp_history=temp_history_18, finance_option="Car Loan"))

# %%
assert p.get_a_car(finance_option=None,temp_history=temp_history_18)=="Not Eligible to Buy a Car (Age Restriction)"
print("This is a Test")
# %%

print(p.get_a_car(finance_option=None,temp_history=temp_history_18))

# %%
