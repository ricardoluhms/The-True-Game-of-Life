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
    ### get the last record for each person
    df_last_record = df_all_records.sort_values(["unique_name_id", "year"]).drop_duplicates("unique_name_id", keep="last")
    ### this will be the dataframe to use for the lineage table
    ### check the total max year for the entire dataframe
    max_year = df_last_record["year"].max()
    ### flag the dead people in the last record
    dead_crit = df_last_record["unique_name_id"].isin(df_dead["unique_name_id"])
    df_last_record["is_dead"] = 0
    df_last_record.loc[dead_crit, "is_dead"] = 1
    
    ### lineage table (deceased_id, relateve_id, relation, priority, share)
    ### get people ids who are dead
    dead_cols = ["unique_name_id", "spouse_name_id", "existing_children_count", "balance", "has_insurance_flag"]
    last_record = ["unique_name_id", "spouse_name_id", "existing_children_count","parent_name_id_A", "parent_name_id_B","is_dead"]
    dead_people = df_dead[dead_cols].copy()
    last_record_slice = df_last_record[last_record].copy()
    ### assume that there is more than one record for each person in the alive_people dataframe
    ### sort the dataframe by unique_name_id and year and get the last record for each person
    

    ### spouse criteria
    spouses_ids = dead_people["spouse_name_id"].unique()
    spouse_crit = last_record_slice["unique_name_id"].isin(spouses_ids)
    cols2 = ["unique_name_id", "spouse_name_id"]
    alive_spouses = last_record_slice[spouse_crit][cols2].copy()
    ### rename the columns
    to_rename = {"unique_name_id": "relative_id", "spouse_name_id": "deceased_id"}
    alive_spouses = alive_spouses.rename(columns=to_rename)
    alive_spouses["relation"] = "Spouse"
    alive_spouses["priority"] = 1

    ### children criteria
    children_crit = dead_people["existing_children_count"] > 0
    deceased_ids_with_child = dead_people[children_crit]["unique_name_id"].unique()

    ### combine the alive_people so it has only one column for the parent_name_id
    potential_heirs_cp = alive_people.copy()

    pot_heirsA = potential_heirs_cp[["unique_name_id", "parent_name_id_A"]].copy()
    to_rename = {"unique_name_id": "relative_id", "parent_name_id_A": "deceased_id"}
    pot_heirsA = pot_heirsA.rename(columns=to_rename)

    pot_heirsB = potential_heirs_cp[["unique_name_id", "parent_name_id_B"]].copy()
    to_rename = {"unique_name_id": "relative_id", "parent_name_id_B": "deceased_id"}
    pot_heirsB = pot_heirsB.rename(columns=to_rename)

    ### drop heirs that are not children of the deceased
    potential_heirs = pd.concat([pot_heirsA, pot_heirsB]).sort_index()
    are_heirs = potential_heirs["deceased_id"].isin(deceased_ids_with_child)
    valid_heirs = potential_heirs[are_heirs].copy()
    valid_heirs["priority"] = 1
    valid_heirs["relation"] = "Heir"

    ### get the spouses of the children/heirs
    heirs_ids = valid_heirs["relative_id"].unique()
    heir_spouse_crit = alive_people["unique_name_id"].isin(heirs_ids)
    cols2 = ["unique_name_id", "spouse_name_id"]
    alive_heir_spouses = alive_people[heir_spouse_crit][cols2].copy()
    ### rename the columns
    to_rename = {"unique_name_id": "relative_id", "spouse_name_id": "heir_id"}
    alive_heir_spouses = alive_heir_spouses.rename(columns=to_rename)
    ### merge the valid_heirs with the alive_heir_spouses to get deceased_id
    alive_heir_spouses = alive_heir_spouses.merge(valid_heirs, 
                                                  left_on="relative_id", 
                                                  right_on="heir_id", how="left")
    alive_heir_spouses["relation"] = "Heir Spouse"
    alive_heir_spouses["priority"] = 2
    

    ### get the children of the heirs
    heir_children = potential_heirs.copy()
    to_rename = {"unique_name_id": "relative_id", "deceased_id": "heir_id"}
    heir_children = heir_children.rename(columns=to_rename)

    valid_heirs_ids = valid_heirs["relative_id"].unique()
    heir_children_crit = heir_children["heir_id"].isin(valid_heirs_ids)
    valid_heir_children = heir_children[heir_children_crit].copy()
    ### merge the valid_heirs_children with the heir_children to get the deceased_id
    valid_heir_children = valid_heir_children.merge(valid_heirs, 
                                                    left_on="heir_id", 
                                                    right_on="relative_id", how="left")
    valid_heir_children["relation"] = "Heir Child"
    valid_heir_children["priority"] = 3
    
    ### combine the dataframes
    lineage_table = pd.concat([alive_spouses, valid_heirs, 
                               alive_heir_spouses, valid_heir_children]).sort_index()
    return lineage_table

def lineage_table_share_distribution(lineage_table):
    ### use priority to distribute the share
    ### groupby deceased_id and priority and count the number of unique relative_id
    ### pivot the table to get the count of unique relative_id for each priority
    priorities = lineage_table.\
                    groupby(["deceased_id", "priority"])\
                    ["relative_id"].nunique().reset_index()


    priorities_pivot = priorities.pivot(index="deceased_id", columns="priority", values="relative_id").fillna(0).reset_index()
    priorities_pivot.columns = ["deceased_id", "priority_1", "priority_2", "priority_3"]


def estate_at_death(df_alive, df_dead):
    ### get the current balance and insurance
    ### if the person dies before insurance expires, then the insurance will added to the balance (no beneficiary assigned)
    ### criterias for estate_at_death
    ### count the number of children and check who are they and if they are alive
    ### check if the person has a spouse and if the spouse is alive
    ### simplified estate rules:-
    ### spouse: 50% of the balance
    ### children: 50% of the balance divided by the number of alive children
    ### if the person does not have a spouse or spouse is dead, then the children will get 100% of the balance divided by the number of children

    ### if child is dead, check if the child has a spouse and if the spouse is alive
    ### if the child has a spouse, then the spouse will get the child's share
    ### if the child has a spouse and the spouse is dead, then the grand children will get the child's share
    ### else money will be lost

    ### lineage table (deceased_id, relateve_id, relation, priority, share)


    ### get people ids who are dead
    dead_cols = ["unique_name_id", "spouse_name_id", "existing_children_count", "balance", "has_insurance_flag"]
    alive_cols = ["unique_name_id", "spouse_name_id", "existing_children_count","parent_name_id_A", "parent_name_id_B"]
    dead_people = df_dead[dead_cols].copy()
    alive_people = df_alive[alive_cols].copy()

    ### spouse criteria
    spouses_ids = dead_people["spouse_name_id"].unique()
    spouse_crit = alive_people["unique_name_id"].isin(spouses_ids)
    cols2 = ["unique_name_id", "spouse_name_id"]
    alive_spouses = alive_people[spouse_crit][cols2].copy()
    ### rename the columns
    to_rename = {"unique_name_id": "relative_id", "spouse_name_id": "deceased_id"}
    alive_spouses = alive_spouses.rename(columns=to_rename)
    alive_spouses["relation"] = "Spouse"
    alive_spouses["priority"] = 1

    ### children criteria
    children_crit = dead_people["existing_children_count"] > 0
    deceased_ids_with_child = dead_people[children_crit]["unique_name_id"].unique()

    ### combine the alive_people so it has only one column for the parent_name_id
    potential_heirs_cp = alive_people.copy()

    pot_heirsA = potential_heirs_cp[["unique_name_id", "parent_name_id_A"]].copy()
    to_rename = {"unique_name_id": "relative_id", "parent_name_id_A": "deceased_id"}
    pot_heirsA = pot_heirsA.rename(columns=to_rename)

    pot_heirsB = potential_heirs_cp[["unique_name_id", "parent_name_id_B"]].copy()
    to_rename = {"unique_name_id": "relative_id", "parent_name_id_B": "deceased_id"}
    pot_heirsB = pot_heirsB.rename(columns=to_rename)

    ### drop heirs that are not children of the deceased
    potential_heirs = pd.concat([pot_heirsA, pot_heirsB]).sort_index()
    are_heirs = potential_heirs["deceased_id"].isin(deceased_ids_with_child)
    valid_heirs = potential_heirs[are_heirs].copy()
    valid_heirs["priority"] = 1
    valid_heirs["relation"] = "Heir"

    ### get the spouses of the children/heirs
    heirs_ids = valid_heirs["relative_id"].unique()
    heir_spouse_crit = alive_people["unique_name_id"].isin(heirs_ids)
    cols2 = ["unique_name_id", "spouse_name_id"]
    alive_heir_spouses = alive_people[heir_spouse_crit][cols2].copy()
    ### rename the columns
    to_rename = {"unique_name_id": "relative_id", "spouse_name_id": "heir_id"}
    alive_heir_spouses = alive_heir_spouses.rename(columns=to_rename)
    ### merge the valid_heirs with the alive_heir_spouses to get deceased_id
    alive_heir_spouses = alive_heir_spouses.merge(valid_heirs, 
                                                  left_on="relative_id", 
                                                  right_on="heir_id", how="left")
    alive_heir_spouses["relation"] = "Heir Spouse"
    alive_heir_spouses["priority"] = 2
    

    ### get the children of the heirs
    heir_children = potential_heirs.copy()
    to_rename = {"unique_name_id": "relative_id", "deceased_id": "heir_id"}
    heir_children = heir_children.rename(columns=to_rename)

    valid_heirs_ids = valid_heirs["relative_id"].unique()
    heir_children_crit = heir_children["heir_id"].isin(valid_heirs_ids)
    valid_heir_children = heir_children[heir_children_crit].copy()
    ### merge the valid_heirs_children with the heir_children to get the deceased_id
    valid_heir_children = valid_heir_children.merge(valid_heirs, 
                                                    left_on="heir_id", 
                                                    right_on="relative_id", how="left")
    valid_heir_children["relation"] = "Heir Child"
    valid_heir_children["priority"] = 3
    
    ### combine the dataframes
    lineage_table = pd.concat([alive_spouses, valid_heirs, alive_heir_spouses, valid_heir_children]).sort_index()
    return lineage_table





### if the person does not have the has_insurance_flag, 


### student loan

### pay off student loan

### get raise

### retirement

### life insurance

# %%
##
### buy a house