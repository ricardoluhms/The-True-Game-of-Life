#%%
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import random
import numpy as np
try:
    from  modules.gml_constants import *
except :
    from  gml_constants import *
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
    df2["spender_prof_rate"] = df2["spender_prof"].apply(lambda x: SPENDER_PROFILE[x] + np.random.uniform(-0.05, 0.05)).round(2)
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

def student_loan(df):
    """Calculate and update loan details based on tuition fees."""
    df2 = df.copy()
    
    ### eligibility for student loan
    ### - person must not have a career but must have a future career
    no_career_check = ~df2["career"].isin(list(INITIAL_INCOME_RANGES.keys())[2:-1])
    future_career_check = df2["future_career"].isin(list(INITIAL_INCOME_RANGES.keys())[2:-1])
    crit = no_career_check & future_career_check
    if crit.sum() == 0:
        return df2
    could_get_loan = df2[crit].copy()
    will_not_get_loan = df2[~crit].copy()

    ### get the tuition due
    could_get_loan["tuition_due"] = could_get_loan["future_career"].apply(lambda x: TUITION_FEES[x])

    ### need a loan? if balance is less than tuition due, then need a loan
    need_loan_crit = could_get_loan["tuition_due"] > could_get_loan["balance"]
    need_loan = could_get_loan[need_loan_crit].copy()
    no_need_loan = could_get_loan[~need_loan_crit].copy()

    ### update the balance for those who do not need a loan
    no_need_loan["balance"] = no_need_loan["balance"] - no_need_loan["tuition_due"]

    ### first loan? if loan is None, then it is the first loan
    ### first loan we set loan_interest_rate and loan_term
    ### else we just update the loan
    first_loan_crit = need_loan["loan"].isna()
    first_loan = need_loan[first_loan_crit].copy()
    not_first_loan = need_loan[~first_loan_crit].copy()
    
    ### if balance is less than 0, then the person needs a loan to pay for the tuition and nega

    first_loan["loan_term"] = first_loan["future_career"].apply(lambda x: YEARS_OF_STUDY[x]+8)
    first_loan["interest_rate"] = first_loan["future_career"].apply(lambda x: random.uniform(STUDENT_LOAN_INTEREST_RATES[0], 
                                                                                             STUDENT_LOAN_INTEREST_RATES[1]))
    
    need_loan_p2 = pd.concat([first_loan, not_first_loan]).sort_index()
    need_loan_p2["loan"] = 0

    ### loan will be the tuition due plus the interest rate - this solves if the balance is negative and add it to the loan
    need_loan_p2["loan"] += (need_loan_p2["tuition_due"] - need_loan_p2["balance"]) *\
                            (1 + need_loan_p2["interest_rate"])**need_loan_p2["loan_term"]
    need_loan_p2["balance"] = 0
    ### drop the tuition due column
    need_loan_p2 = need_loan_p2.drop(columns=["tuition_due"], errors='ignore')
    no_need_loan = no_need_loan.drop(columns=["tuition_due"], errors='ignore')

    ### combine the dataframes
    updated_df = pd.concat([no_need_loan, need_loan_p2, will_not_get_loan]).sort_index()

    return updated_df

def change_spender_profile(df,crit, spender_prof_mod = 0.1):
    ### if current rate is less than the SPENDER_PROFILE -0.05, then demote using SPENDER_PROFILE_DECREASE
    ### if current rate is greater than the SPENDER_PROFILE +0.05, then promote using SPENDER_PROFILE_INCREASE
    df2 = df.copy()
    ### get people who has spender_prof
    spender_prof_crit = ~df2["spender_prof"].isna()
    if spender_prof_crit.sum() == 0:
        return df2
    
    will_change = crit & spender_prof_crit

    df_will_change = df2[will_change].copy()
    df_no_change = df2[~will_change].copy()
    ### reverse the SPENDER_PROFILE_DECREASE
    SPENDER_PROFILE_INCREASE = {v: k for k, v in SPENDER_PROFILE_DECREASE.items()}

    df_will_change["new_spender_prof_rate"] = df_will_change["spender_prof_rate"] + spender_prof_mod

    current_min_base_rate = df_will_change["spender_prof"].apply(lambda x: SPENDER_PROFILE[x] - 0.05)
    current_max_base_rate = df_will_change["spender_prof"].apply(lambda x: SPENDER_PROFILE[x] + 0.05)

    ### will demote spender_prof ?
    demote_crit = df_will_change["new_spender_prof_rate"] < current_min_base_rate
    df_will_change.loc[demote_crit, "new_spender_prof_rate"] = df_will_change.loc[demote_crit, "spender_prof_rate"].apply(lambda x: SPENDER_PROFILE_DECREASE[x] if x in SPENDER_PROFILE_DECREASE else None)

    ### will promote spender_prof ?
    promote_crit = df_will_change["new_spender_prof_rate"] > current_max_base_rate
    df_will_change.loc[promote_crit, "new_spender_prof_rate"] = df_will_change.loc[promote_crit, "spender_prof_rate"].apply(lambda x: SPENDER_PROFILE_INCREASE[x] if x in SPENDER_PROFILE_INCREASE else None)

    df_will_change["spender_prof_rate"] = df_will_change["new_spender_prof_rate"]
    df_will_change = df_will_change.drop(columns=["new_spender_prof_rate"], errors='ignore')

    updated_df = pd.concat([df_will_change, df_no_change]).sort_index()

    return updated_df             

def pay_loan(df):
    df2 = df.copy()

    ### check if the person has a loan
    loan_crit = df2["loan"] > 0
    if loan_crit.sum() == 0:
        return df2

    ### get people who has loan
    loan_df = df2[loan_crit].copy()
    no_loan_df = df2[~loan_crit].copy()

    ### check if the person is still a student - if so, do not pay the loan it can be paid after graduation
    student_crit = ~loan_df["career"].isin(list(INITIAL_INCOME_RANGES.keys())[2:-1])

    student_skip_loan_pay_df = loan_df[student_crit].copy()
    should_pay_loan_df = loan_df[~student_crit].copy()

    ### can the person pay the loan?
    ### scenario 1: balance is greater than or equal the loan
    ### subtract the loan from the balance
    ### subtract the amount paid from the loan
    ### if loan term is 0, then remove the loan

    ### scenario 2: balance is less than the loan
    ### 2A: balance is positive
    ### subtract the balance from the loan
    ### set the balance to 0
    ### interest rate is applied to the loan
    ### reduce the spender_prof_rate by 0.1

    ### 2B: balance is negative
    ### set the balance to 0
    ### interest rate is applied to the loan
    ### reduce the spender_prof_rate by 0.15

    ### scenario 2A and 2B are combined in the same function
    ### apply change_spender_profile to reduce the spender_prof_rate by 0.1 or 0.15

    ### add a column default count to keep track of the number of defaults
    amount_to_pay = should_pay_loan_df["loan"]/should_pay_loan_df["loan_term"]
    low_balance_crit = (should_pay_loan_df["balance"] < amount_to_pay) & (should_pay_loan_df["balance"] > 0)
    negative_balance_crit = should_pay_loan_df["balance"] < 0
    can_pay_crit = should_pay_loan_df["balance"] >= amount_to_pay

    ### Scenario 1 - pay the loan
    should_pay_loan_df.loc[can_pay_crit, "balance"] = should_pay_loan_df.loc[can_pay_crit, "balance"] - amount_to_pay
    should_pay_loan_df.loc[can_pay_crit, "loan_term"] = should_pay_loan_df.loc[can_pay_crit, "loan_term"] - 1
    should_pay_loan_df.loc[can_pay_crit, "loan"] = should_pay_loan_df.loc[can_pay_crit, "loan"] - amount_to_pay
    if should_pay_loan_df["loan_term"].min() == 0:
        should_pay_loan_df.loc[should_pay_loan_df["loan_term"] == 0, "loan"] = 0
        should_pay_loan_df.loc[should_pay_loan_df["loan_term"] == 0, "interest_rate"] = 0
        should_pay_loan_df.loc[should_pay_loan_df["loan_term"] == 0, "event"] = "Loan Payment Complete"
    else:
        should_pay_loan_df["event"] = "Loan Payment OK"

    ### Scenario 2 - pay the loan with balance less than the amount to pay and get a default and change slightly spender_prof_rate
    should_pay_loan_df = change_spender_profile(should_pay_loan_df, low_balance_crit, -0.1)
    should_pay_loan_df = change_spender_profile(should_pay_loan_df, negative_balance_crit, -0.15)

    should_pay_loan_df.loc[low_balance_crit, "loan"] = (should_pay_loan_df.loc[low_balance_crit, "loan"] -\
                                                         should_pay_loan_df.loc[low_balance_crit, "balance"])*\
                                                        (1 + should_pay_loan_df.loc[low_balance_crit, "interest_rate"])
    should_pay_loan_df.loc[low_balance_crit, "balance"] = 0
    should_pay_loan_df.loc[low_balance_crit, "default_count"] = should_pay_loan_df.loc[low_balance_crit, "default_count"] + 1
    should_pay_loan_df.loc[low_balance_crit, "event"] = f"Loan Default {should_pay_loan_df.loc[low_balance_crit, 'default_count']}"

    should_pay_loan_df.loc[negative_balance_crit, "loan"] = (should_pay_loan_df.loc[negative_balance_crit, "loan"])*\
                                                        (1 + should_pay_loan_df.loc[negative_balance_crit, "interest_rate"])
    ### balance will continue negative and should not be set to 0
    should_pay_loan_df.loc[negative_balance_crit, "default_count"] = should_pay_loan_df.loc[negative_balance_crit, "default_count"] + 1
    should_pay_loan_df.loc[negative_balance_crit, "event"] = f"Loan Default {should_pay_loan_df.loc[negative_balance_crit, 'default_count']}"

    updated_df = pd.concat([should_pay_loan_df, student_skip_loan_pay_df, no_loan_df]).sort_index()

    return updated_df

def lineage_table(df_all_records, df_dead):
    """
    df_all_records: dataframe with all records
    df_dead: dataframe with all dead people in the current year
    """
    import pandas as pd

    ### Get the last record for each person
    df_last_record = df_all_records.sort_values(["unique_name_id", "year"]).drop_duplicates("unique_name_id", keep="last")
    
    ### Check the total max year for the entire dataframe
    max_year = df_last_record["year"].max()
    
    ### Flag the dead people in the last record
    dead_crit = df_last_record["unique_name_id"].isin(df_dead["unique_name_id"])
    df_last_record["is_dead"] = 0
    df_last_record.loc[dead_crit, "is_dead"] = 1

    ### Lineage table (deceased_id, relative_id, relation, priority, share)
    ### Get people IDs who are dead
    dead_cols = ["unique_name_id", "spouse_name_id", "existing_children_count", "balance", "has_insurance_flag"]
    last_record = ["unique_name_id", "spouse_name_id", "existing_children_count", "parent_name_id_A", "parent_name_id_B", "is_dead"]
    dead_people = df_dead[dead_cols].copy()
    last_record_slice = df_last_record[last_record].copy()
    
    ### Spouse criteria
    spouses_ids = dead_people["spouse_name_id"].unique()
    spouse_crit = last_record_slice["unique_name_id"].isin(spouses_ids)
    cols2 = ["unique_name_id", "spouse_name_id", "is_dead"]
    all_spouses = last_record_slice[spouse_crit][cols2].copy()
    
    ### Rename the columns
    to_rename = {"unique_name_id": "relative_id", "spouse_name_id": "deceased_id"}
    all_spouses = all_spouses.rename(columns=to_rename)
    all_spouses["relation"] = "Spouse"
    all_spouses["priority"] = 1
    all_spouses["priority_for_share"] = 1

    ### Set priority to 0 if the spouse is dead
    all_spouses.loc[all_spouses["is_dead"] == 1, "priority_for_share"] = 0

    ### Children criteria
    children_crit = dead_people["existing_children_count"] > 0
    deceased_ids_with_child = dead_people[children_crit]["unique_name_id"].unique()

    ### Combine the alive_people so it has only one column for the parent_name_id
    potential_heirs_cp = last_record_slice.copy()
    cols2 = ["unique_name_id", "parent_name_id_A", "is_dead"]
    pot_heirsA = potential_heirs_cp[cols2].copy()
    to_rename = {"unique_name_id": "relative_id", "parent_name_id_A": "deceased_id"}
    pot_heirsA = pot_heirsA.rename(columns=to_rename)

    cols2 = ["unique_name_id", "parent_name_id_B", "is_dead"]
    pot_heirsB = potential_heirs_cp[cols2].copy()
    to_rename = {"unique_name_id": "relative_id", "parent_name_id_B": "deceased_id"}
    pot_heirsB = pot_heirsB.rename(columns=to_rename)

    ### Drop heirs that are not children of the deceased
    potential_heirs = pd.concat([pot_heirsA, pot_heirsB]).sort_index()
    are_heirs = potential_heirs["deceased_id"].isin(deceased_ids_with_child)
    valid_heirs = potential_heirs[are_heirs].copy()
    valid_heirs["priority"] = 1
    valid_heirs["priority_for_share"] = 1
    valid_heirs["relation"] = "Heir"

    ### Set priority to 0 if the heir is dead
    valid_heirs.loc[valid_heirs["is_dead"] == 1, "priority_for_share"] = 0

    ### Get the list of dead heirs - it will be used to get the spouses of the heirs
    dead_heirs_ids = valid_heirs[valid_heirs["is_dead"] == 1]["relative_id"].unique()

    ### Get spouses of the dead heirs
    heir_spouse_crit = last_record_slice["unique_name_id"].isin(dead_heirs_ids)
    cols2 = ["unique_name_id", "spouse_name_id", "is_dead"]
    alive_heir_spouses = last_record_slice[heir_spouse_crit][cols2].copy()
    
    ### Rename the columns
    to_rename = {"unique_name_id": "relative_id", "spouse_name_id": "heir_id"}
    alive_heir_spouses = alive_heir_spouses.rename(columns=to_rename)
    
    ### Merge the valid_heirs with the alive_heir_spouses to get deceased_id
    alive_heir_spouses = alive_heir_spouses.merge(valid_heirs, 
                                                  left_on="relative_id", 
                                                  right_on="heir_id", how="left")
    alive_heir_spouses["relation"] = "Heir Spouse"
    alive_heir_spouses["priority_for_share"] = 2
    alive_heir_spouses["priority"] = 2
    
    ### Set priority to 0 if the heir spouse is dead
    alive_heir_spouses.loc[alive_heir_spouses["is_dead"] == 1, "priority_for_share"] = 0

    ### Get IDs of spouses of heirs that died
    dead_heir_spouses_ids = alive_heir_spouses[alive_heir_spouses["is_dead"] == 1]["relative_id"].unique()

    ### Get the children of the heirs
    heir_children_crit = potential_heirs["deceased_id"].isin(dead_heirs_ids) & potential_heirs["relative_id"].isin(dead_heir_spouses_ids)
    heir_children = potential_heirs[heir_children_crit].copy()
    to_rename = {"unique_name_id": "relative_id", "deceased_id": "heir_id"}
    heir_children = heir_children.rename(columns=to_rename)

    ### Merge the valid_heir_children with the heir_children to get the deceased_id
    heir_children = heir_children.merge(valid_heirs, 
                                        left_on="heir_id", 
                                        right_on="relative_id", how="left")
    
    ### Check if both heir and heir's spouse are dead, then set priority to 2
    valid_heir_children_crit = (heir_children["is_dead"] == 1) & heir_children["heir_id"].isin(dead_heir_spouses_ids)
    heir_children.loc[valid_heir_children_crit, "relation"] = "Heir Child"
    heir_children["priority_for_share"] = 3
    heir_children["priority"] = 3
    heir_children.loc[valid_heir_children_crit, "priority"] = 3

    ### Set priority to 0 for all other heir children
    heir_children.loc[~valid_heir_children_crit, "priority_for_share"] = 0

    ### Filter only valid heir children
    valid_heir_children = heir_children[valid_heir_children_crit].copy()
    
    ### Combine the dataframes
    lineage_table = pd.concat([all_spouses, valid_heirs, 
                               alive_heir_spouses, valid_heir_children]).sort_index()
    return lineage_table

def lineage_table_share_distribution(lineage_table):
    
    ### return the share distribution table
    lineage_table2 = lineage_table.copy()

    ### groupby deceased_id and priority and count the number of unique relative_id
    pivot_priority = lineage_table2.groupby(["deceased_id", "priority"])["relative_id"].nunique().reset_index()
    pivot_priority = pivot_priority.pivot(index="deceased_id", columns="priority", values="relative_id").fillna(0)

    ### groupby deceased_id and priority_for_share and count the number of unique relative_id
    pivot_priority_for_share = lineage_table2.groupby(["deceased_id", "priority_for_share"])["relative_id"].nunique().reset_index()
    pivot_priority_for_share = pivot_priority_for_share.pivot(index="deceased_id", columns="priority_for_share", values="relative_id").fillna(0)

    ### pivot each groupby table to get the count of unique relative_id for each priority and priority_for_share
    pivot_tt_ratio = pivot_priority_for_share.div(pivot_priority)
    pivot_tt_ratio = pivot_tt_ratio.fillna(0)

    ### in pivot_tt_ratio, multiply the (1-pivot_tt_ratio[1]) by (pivot_tt_ratio[2]).
    pivot_tt_ratio[2] = (1-pivot_tt_ratio[1]) * pivot_tt_ratio[2]
    ### in pivot_tt_ratio, multiply the (1-pivot_tt_ratio[2]) by (pivot_tt_ratio[3]).
    pivot_tt_ratio[3] = (1-pivot_tt_ratio[2]) * pivot_tt_ratio[3]

    ### table 4 will be the updated pivot_tt_ratio divided table 2
    ind_pivot_tt_ratio_updated = pivot_tt_ratio.div(pivot_priority_for_share)
    ind_pivot_tt_ratio_updated = ind_pivot_tt_ratio_updated.fillna(0)

    ### melt table 4 to get the share distribution as a dataframe with deceased_id, priority_for_share, share
    ind_pivot_tt_ratio_updated = ind_pivot_tt_ratio_updated.reset_index()
    ind_pivot_tt_ratio_updated = pd.melt(ind_pivot_tt_ratio_updated, id_vars="deceased_id",
                                            value_vars=[1, 2, 3], var_name="priority_for_share", value_name="share")

    ### merge the share distribution with the lineage_table to get the share for each deceased_id, priority_for_share
    lineage_table2 = lineage_table2.merge(ind_pivot_tt_ratio_updated, on=["deceased_id", "priority_for_share"], how="left")

    return lineage_table2

def share_distribution(df_all_records, df_dead):

    max_year = df_all_records["year"].max()
    max_year_crit = df_all_records["year"] == max_year
    current_year_df = df_all_records[max_year_crit].copy()

    if len(df_dead) == 0:
        return current_year_df

    lineage_table2 = lineage_table(df_all_records, df_dead)
    share_distribution = lineage_table_share_distribution(lineage_table2)
    ### get the balance of the deceased_id and multiply by the share
    ### get max year

    ### get the balance of the deceased_id and multiply by the share
    df_dead = df_dead[["unique_name_id", "balance"]].copy()
    df_dead = df_dead.rename(columns={"unique_name_id": "deceased_id"})
    share_distribution = share_distribution.merge(df_dead, on="deceased_id", how="left")
    share_distribution["share_value"] = share_distribution["share"] * share_distribution["balance"]

    ### get the relative_id and the share_value
    share_distribution = share_distribution[["relative_id", "share_value"]].copy()
    share_distribution = share_distribution.rename(columns={"relative_id": "unique_name_id"})
    ### merge the share_value with the current year dataframe and add to the balance
    current_year_df = current_year_df.merge(share_distribution, on="unique_name_id", how="left")
    ### fill the NaN values with 0 for share_value
    current_year_df["share_value"] = current_year_df["share_value"].fillna(0)
    current_year_df["balance"] = current_year_df["balance"] + current_year_df["share_value"]
    current_year_df = current_year_df.drop(columns=["share_value"], errors='ignore')

    return current_year_df
### if the person does not have the has_insurance_flag, 

### retirement

### life insurance - include life stage
def calculate_health_score(df):
    # Normalize and calculate the health score
    df['bmi_score'] = np.where((df['bmi'] >= 18.5) & (df['bmi'] <= 24.9), 1, 0)
    df['bp_score'] = np.where((df['blood_pressure_systolic'] < 130) & (df['blood_pressure_diastolic'] < 85), 1, 0)
    df['cholesterol_score'] = np.where((df['cholesterol_ldl'] < 130) & (df['cholesterol_hdl'] > 40), 1, 0)
    df['blood_sugar_score'] = np.where(df['blood_sugar'] < 100, 1, 0)
    df['physical_activity_score'] = np.where(df['physical_activity'] >= 3, 1, 0)
    df['diet_score'] = np.where(df['diet_score'] >= 7, 1, 0)
    df['sleep_score'] = np.where((df['sleep_hours'] >= 7) & (df['sleep_hours'] <= 9), 1, 0)
    df['chronic_conditions_score'] = np.where(df['chronic_conditions'] == 0, 1, 0)
    df['smoking_score'] = np.where(df['smoking_status'] == 0, 1, 0)
    df['alcohol_score'] = np.where(df['alcohol_consumption'] <= 2, 1, 0)
    df['stress_score'] = np.where(df['stress_level'] <= 4, 1, 0)
    df['mental_health_score'] = np.where(df['mental_health_conditions'] == 0, 1, 0)
    df['checkup_score'] = df['regular_checkups']
    
    df['health_score'] = (
        df['bmi_score'] + df['bp_score'] + df['cholesterol_score'] + df['blood_sugar_score'] +
        df['physical_activity_score'] + df['diet_score'] + df['sleep_score'] + df['chronic_conditions_score'] +
        df['smoking_score'] + df['alcohol_score'] + df['stress_score'] + df['mental_health_score'] +
        df['checkup_score']
    ) / 13 * 100  # Scale to 0-100
    
    return df

def calculate_term_insurance_premium(df):
    # Base premium rate per $1000 face amount
    base_rate = 0.05
    
    # Calculate premium based on age, face amount, and other criteria
    df['premium'] = (
        df['face_amount'] / 1000 * base_rate *
        (1 + (df['age'] - 25) * 0.05) *  # Age factor
        (1.2 if df['gender'] == 'male' else 1.1) *  # Gender factor
        (2 if df['smoker'] else 1) *  # Smoking factor
        (1 + (100 - df['health_score']) / 100) *  # Health factor
        (1 + df['occupation_risk'] / 10) *  # Occupation risk factor
        (1.5 if df['risky_hobbies'] else 1)  # Risky hobbies factor
    )
    
    return df

def calculate_risk_tolerance_and_insurance(df):
    # Calculate risk tolerance based on quantified metrics
    df['risk_tolerance'] = (
        df['num_children'] * -1 +  # More children, lower risk tolerance
        df['homeowner'].astype(int) * 2 +  # Homeownership increases risk tolerance
        (df['income_level'] // 10000) +  # Higher income increases risk tolerance
        (df['health_score'] // 10)  # Better health increases risk tolerance
    )
    
    # Determine likelihood of buying life insurance based on life events
    df['likely_to_buy_life_insurance'] = (
        (df['num_children'] > 0) |
        (df['marital_status'] == 'married') |
        (df['homeowner'] == True) |
        (df['income_level'] > 75000) |
        (df['health_score'] < 80) |
        (df['divorce_status'] == True) |
        (df['bereavement_status'] == True)
    )
    
    return df
# %%
##
### buy a house
### house size, price, mortgage, downpayment, interest rate, term, monthly payment
### house size is determined by the number of children and the career
### create function to calculate the house size
### create function to calculate the house price
### create function to calculate the loan amount
### create function to calculate the monthly payment