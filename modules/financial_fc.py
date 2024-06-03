#%%
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
from  modules.gml_constants import *

### limitations: 
# 01 - A couple will have always a proportional part of the income set to housing
# This means that if their salary increases, the housing part will increase as well
# 02 - A family with children will will not consider the increase in other expenses for each child
# 03 - Inflation is not considered

SPENDER_PROFILE = {'Average': 0.9, 'Big Spender': 1.05, 'Small Spender': 0.75, 'In-Debt': 0.5, 'Depressed': 0.4}

### percentage of expenditure based on age group sum should be 1 and
### housing & insurance multiplier for child and teenager should be the same 0
EXPEND_MULTIPLIER_BY_EXPENDITURE_GROUP = {'Baby': {'Housing': 0, 'Transportation & Food': 0, 'Healthcare': 0, 'Entertainment': 0, 'Insurance': 0, 'Savings': 1},
                                          'Child': {'Housing': 0, 'Transportation & Food': 0.4, 'Healthcare': 0, 'Entertainment': 0.4, 'Insurance': 0, 'Savings': 0.2},
                                          'Teenager': {'Housing': 0, 'Transportation & Food': 0.45, 'Healthcare': 0, 'Entertainment': 0.45, 'Insurance': 0, 'Savings': 0.1},
                                          'Young Adult': {'Housing': 0.4, 'Transportation & Food': 0.25, 'Healthcare': 0.1, 'Entertainment': 0.1, 'Insurance': 0.05, 'Savings': 0.1},
                                          'Adult': {'Housing': 0.4, 'Transportation & Food': 0.25, 'Healthcare': 0.1, 'Entertainment': 0.1, 'Insurance': 0.05, 'Savings': 0.1},
                                          'Elder': {'Housing': 0.35, 'Transportation & Food': 0.2, 'Healthcare': 0.3, 'Entertainment': 0.15, 'Insurance': 0, 'Savings': 0}} 

### transform EXPEND_MULTIPLIER_BY_EXPENDITURE_GROUP into a dataframe
def create_base_expenditure_df():
    df = pd.DataFrame(EXPEND_MULTIPLIER_BY_EXPENDITURE_GROUP).T
    df = df.reset_index()
    df = df.rename(columns={"index": "age_range"})
    ### rename columns to lowercase and replace spaces with underscore and add _rate
    df.columns = [col.replace(" & ", "_").replace(" ", "_").lower() + "_exp_rate" if col != "age_range" else col for col in df.columns]
    return df

EXPEND_MULTIPLIER_BY_EXPENDITURE_GROUP_DF = create_base_expenditure_df()

### create a column to generate the initial values of expenditure rates, spender_prof_rate and expenditure values
def create_initial_expenditure_values(df):
    df2 = df.copy()
    rate_cols = [col for col in EXPEND_MULTIPLIER_BY_EXPENDITURE_GROUP_DF.columns if "rate" in col]
    val_cols = [col.replace("rate", "value") for col in rate_cols]
    df2[rate_cols] = None
    df2[val_cols] = None
    df2["spender_prof_rate"] = None
    return df2

def update_expenditure_rates(df):
    rate_cols = [col for col in EXPEND_MULTIPLIER_BY_EXPENDITURE_GROUP_DF.columns if "rate" in col]
    cols = ["age_range"] + rate_cols + ["spender_prof","has_insurance_flag"]
    df2 = df.copy()[cols]
    ### remove df2["spender_prof"] == None
    non_non_crit = ~df2["spender_prof"].isna()
    if non_non_crit.sum() == 0:
        return df

    df2 = df2[non_non_crit].copy()
    ### use SPENDER_PROFILE to get the rate for each person plus a random value between 0 and 0.1
    df2["spender_prof_rate"] = df2["spender_prof"].apply(lambda x: SPENDER_PROFILE[x] + np.random.uniform(-0.1, 0.1)).round(2)
    ### merge the dataframe with EXPEND_MULTIPLIER_BY_EXPENDITURE_GROUP_DF
    df2 = df2.merge(EXPEND_MULTIPLIER_BY_EXPENDITURE_GROUP_DF, on="age_range", how="left")
    ### remove _x and rename _y columns
    df2 = df2.drop(columns=[col for col in df2.columns if col.endswith("_x")], errors='ignore')
    df2.columns = [col.replace("_y", "") for col in df2.columns]

    ### multiply the rate columns by the rate from spender_prof_rate
    for col in rate_cols:
        if col == "insurance_exp_rate":
            df2[col] = df2[col] * df2["has_insurance_flag"]*df2["spender_prof_rate"]
        else:
            df2[col] = df2[col] * df2["spender_prof_rate"]

    total_rate = df2[rate_cols].sum(axis=1)
    ### check if the total rate is greater than 1
    delta_rate = total_rate - 1
    ### if the total rate is greater than 1, deduct the extra from the savings_exp_rate
    ### if the savings_exp_rate is negative, set it to 0
    df2["savings_exp_rate"] = df2["savings_exp_rate"] - delta_rate
    df2.loc[df2["savings_exp_rate"] < 0, "savings_exp_rate"] = 0
    ### if the total rate is less than 1, add the difference to the savings_exp_rate
    delta_rate = 1 - df2[rate_cols].sum(axis=1)
    df2["savings_exp_rate"] = df2["savings_exp_rate"] + delta_rate

    df3_rest = df[~non_non_crit].copy()
    df3 = df[non_non_crit].copy()

    ### replace the _rate columns from the original dataframe df with the _rate columns from df2
    for col in rate_cols+["spender_prof_rate"]:
        df3[col] = df2[col]

    df3 = pd.concat([df3, df3_rest]).sort_index()

    return df3

### create the expenditure value columns - these will be that year's expenditure
def handle_expenditure_value(df):
    df2 = df.copy()
    income_crit = df2["income"] > 0
    spender_prof_crit = ~df2["spender_prof"].isna()
    crit = income_crit & spender_prof_crit
    if crit.sum() == 0:
        return df2
    
    has_income_df = df2[crit].copy()
    no_income_df = df2[~crit].copy()

    rate_cols = [col for col in has_income_df.columns if "rate" in col]
    for col in rate_cols:
        has_income_df[col.replace("rate", "value")] = has_income_df[col] * has_income_df["income"]

    df2 = pd.concat([has_income_df, no_income_df]).sort_index()

    return df2

def update_account_balance_v2(df):
    ### pay loan is handled in another function
    rate_cols = [col for col in EXPEND_MULTIPLIER_BY_EXPENDITURE_GROUP_DF.columns if "rate" in col]
    ### create val cols by replacing rate with value
    val_cols = [col.replace("rate", "value") for col in rate_cols]

    df2 = df.copy()
    ### get people who has income
    income_crit = df2["income"] > 0
    spender_prof_crit = ~df2["spender_prof"].isna()
    crit = income_crit & spender_prof_crit
    if crit.sum() == 0:
        return df2
    
    ### add income to balance
    df2.loc[crit, "balance"] = df2.loc[crit].apply(lambda x: x["balance"] + x["income"], axis=1)

    ### except for savings values that are added to the balance, the rest are subtracted from the balance
    for col in val_cols:
        if col != "savings_exp_value":
            df2.loc[crit, "balance"] = df2.loc[crit].apply(lambda x: x["balance"] - x[col], axis=1)

    return df2

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
    valid_career = list(INITIAL_INCOME_RANGES.keys())[1:]
    career_crit = df2["career"].isin(valid_career)
    if career_crit.sum() == 0:
        return df2

    df_no_career = df2[~career_crit]
    df_career = df2[career_crit]
    
    # Determine if each employee gets a raise
    df_career['raise_event'] = np.random.uniform(0, 1, len(df_career))
    df_career['raise_prob'] = df_career['career'].apply(lambda x: RAISE_DICT[x]["chance"])
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

def get_student_loan()

### if the person does not have the has_insurance_flag, 


### student loan

### pay off student loan

### get raise

### retirement

### life insurance

### buy a house