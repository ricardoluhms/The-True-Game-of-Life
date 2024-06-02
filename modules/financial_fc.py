#%%
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
from  modules.gml_constants import *

#### 

def update_account_balance(df):
    df2 = df.copy()
    ### get people who has income
    income_crit = df2["income"] > 0
    spender_prof_crit = df2["spender_prof"] != None
    crit = income_crit & spender_prof_crit
    if crit.sum() == 0:
        return df2
    

    ### using apply and lambda
    df2.loc[crit, "balance"] = df2.loc[crit].apply(
        lambda x: x["balance"] + x["income"]*SPENDER_PROFILE[x["spender_prof"]], axis=1)
    return df2

def get_a_raise(df):
    df2 = df.copy()

    ### check if the person has a career except for "Pocket Money"
    career_crit = df2["career"].isin(INITIAL_INCOME_RANGES.keys()[1:])
    if career_crit.sum() == 0:
        return df2

    df_no_career = df2[~career_crit]
    df_career = df2[career_crit]
    
    # Determine if each employee gets a raise
    df_career['raise_event'] = np.random.uniform(0, 1, len(df_career))
    df_career['raise_prob'] = df_career['career_path'].apply(lambda x: RAISE_DICT[x]["chance"])
    df_career['gets_raise'] = df_career['raise_event'] <= df_career['raise_prob']
    
    # Split dataframe into those who get a raise and those who do not
    df_gets_raise = df_career[df_career['gets_raise']].copy()
    df_no_raise = df_career[~df_career['gets_raise']].copy()
    
    # Update salary for those who get a raise
    df_gets_raise['hike_range'] = df_gets_raise['career'].apply(lambda x: RAISE_DICT[x]["hike_range"])
    df_gets_raise['random_rate'] = df_gets_raise['hike_range'].apply(lambda x: np.random.uniform(x[0], x[1]))
    df_gets_raise['income'] = round(df_gets_raise['income'] * (1 + df_gets_raise['random_rate']), 2)
    df_gets_raise['event'] += "Got a Raise"
       
    # Combine the two parts back together
    updated_df = pd.concat([df_gets_raise, df_no_raise,df_no_career]).sort_index()

    # Drop the temporary columns
    updated_df = updated_df.drop(columns=['raise_event', 'raise_prob', 'hike_range', 'random_rate'], errors='ignore')
    
    return updated_df

### review spender profile and add expenditure columns and a savings column
### include a column that shows initial transfer money from parents
### check how to increase expenditure based on number of children within an age group
### create a column to determine the number of dependents within an age group

### student loan

### pay off student loan

### get raise

### retirement

### life insurance

### buy a house