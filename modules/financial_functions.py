#%%
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import random
import numpy as np
try:
    from  modules.constants import *
except :
    from  modules.constants import *
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

def update_expenditure_value_v2(df):
    df2 = df.copy()
    income_crit = df2["income"] > 0
    spender_prof_crit = ~df2["spender_prof"].isna()
    crit = income_crit & spender_prof_crit

    if crit.sum() == 0:
        return df2

    has_income_df = df2[crit].copy()
    no_income_df = df2[~crit].copy()

    rate_cols = [col for col in has_income_df.columns if "rate" in col]
    
    # Update XXX_exp_value based on income and XXX_exp_rate columns
    ### cols that does not update directly from the rate housing_exp_value, savings_exp_value and loan_exp_value

    ### loan_exp_rate should not be updated

    for col in rate_cols:
        if col != "loan_exp_rate":
            has_income_df[col.replace("rate", "value")] = has_income_df[col] * has_income_df["income"]

    ### special cases for those who have a house and those who have a loan

    # Split those with income into:
    
    has_house_crit = has_income_df["house_id"].notna() | (has_income_df["house_id"] != "None") | (has_income_df["house_id"] != "")
    has_loan_crit = has_income_df["loan_exp_value"] > 0
    loan_due_higher_than_housing = has_income_df["loan_exp_value"]> has_income_df["housing_exp_value"]

    ### create the combinations of the crit
    crit_a = ~has_house_crit & ~has_loan_crit # A - No House and No Loan - no changes in exp_values and exp_rates
    crit_b = ~has_house_crit & has_loan_crit # B - No House and Has Loan - no changes in exp_values and exp_rates because loan_exp_rate was updated in pay_loan function
    crit_c = has_house_crit & ~has_loan_crit # C - Has House and No Loan - housing_exp_value and savings_exp_value will be updated using 70% of the current values and the remaining 30% will go to savings_exp_value
    crit_d = has_house_crit & has_loan_crit & loan_due_higher_than_housing
    crit_e = has_house_crit & has_loan_crit & ~loan_due_higher_than_housing
    # D - Has House and Has Loan and Loan is greater than the housing value
    # D.1 - Subtract loan_exp_value from housing_exp_value to avoid counting it twice
    # D.2 - Set housing_exp_value and rate to 0 because the loan is greater than the house value and balance was already updated in pay_loan function
    # E - Has House and Has Loan and Loan is less than the housing value
    # E.1 - Subtract loan_exp_value from housing_exp_value to avoid counting it twice
    # E.2 - Add the remaining housing_exp_value to savings_exp_value
    # E.3 - Set housing_exp_value and rate to 0, and update savings_exp_value and rate

    no_house_no_loan_df = has_income_df[crit_a].copy()
    no_house_has_loan_df = has_income_df[crit_b].copy()
    has_house_no_loan_df = has_income_df[crit_c].copy()
    has_house_has_loan_df_plus = has_income_df[crit_d].copy()
    has_house_has_loan_df_minus = has_income_df[crit_e].copy()

    has_house_no_loan_df["savings_exp_value"] += has_house_no_loan_df["housing_exp_value"] * 0.3
    has_house_no_loan_df["housing_exp_value"] = has_house_no_loan_df["housing_exp_value"] * 0.7
    has_house_no_loan_df["savings_exp_rate"] = has_house_no_loan_df["savings_exp_value"]/has_house_no_loan_df["income"]
    has_house_no_loan_df["housing_exp_rate"] = has_house_no_loan_df["housing_exp_value"]/has_house_no_loan_df["income"]

    has_house_has_loan_df_plus["housing_exp_value"] = 0
    has_house_has_loan_df_plus["housing_exp_rate"] = 0

    has_house_has_loan_df_minus["savings_exp_value"] += has_house_has_loan_df_minus["housing_exp_value"] - has_house_has_loan_df_minus["loan_exp_value"]
    has_house_has_loan_df_minus["housing_exp_value"] = 0
    has_house_has_loan_df_plus["housing_exp_rate"] = 0
    has_house_has_loan_df_minus["savings_exp_rate"] = has_house_has_loan_df_minus["savings_exp_value"]/has_house_has_loan_df_minus["income"]

    updated_df = pd.concat([no_income_df, no_house_no_loan_df, no_house_has_loan_df, 
                            has_house_no_loan_df, has_house_has_loan_df_plus, has_house_has_loan_df_minus]).sort_index()
    
    return updated_df

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
    ### savings_exp_value continues in the balance because there is no need to subtract it (no savings account)
    ### loan value is also not subtracted from the balance because it is handled in the pay_loan function
    do_not_subtract = ["savings_exp_value", "loan_exp_value"]

    for col in val_cols:
        if col not in do_not_subtract:
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

    should_pay_loan_df["amount_to_pay"] = should_pay_loan_df["loan"]/should_pay_loan_df["loan_term"]

    low_balance_crit = (should_pay_loan_df["balance"] < should_pay_loan_df["amount_to_pay"]) & (should_pay_loan_df["balance"] > 0)
    negative_balance_crit = should_pay_loan_df["balance"] < 0
    can_pay_crit = should_pay_loan_df["balance"] >= should_pay_loan_df["amount_to_pay"]

    ### Scenario 1 - pay the loan
    should_pay_loan_df.loc[can_pay_crit, "balance"] = should_pay_loan_df.loc[can_pay_crit, "balance"] - should_pay_loan_df["amount_to_pay"]
    should_pay_loan_df.loc[can_pay_crit, "loan_term"] = should_pay_loan_df.loc[can_pay_crit, "loan_term"] - 1
    should_pay_loan_df.loc[can_pay_crit, "loan"] = should_pay_loan_df.loc[can_pay_crit, "loan"] - should_pay_loan_df["amount_to_pay"]

    should_pay_loan_df.loc[can_pay_crit,"loan_exp_val"] += should_pay_loan_df["amount_to_pay"]
    should_pay_loan_df.loc[can_pay_crit,"loan_exp_rate"] += should_pay_loan_df["amount_to_pay"]/should_pay_loan_df.loc[can_pay_crit,"income"]


    if should_pay_loan_df["loan_term"].min() == 0:
        should_pay_loan_df.loc[should_pay_loan_df["loan_term"] == 0, "loan"] = 0
        should_pay_loan_df.loc[should_pay_loan_df["loan_term"] == 0, "interest_rate"] = 0
        should_pay_loan_df.loc[should_pay_loan_df["loan_term"] == 0, "event"] = "Loan Payment Complete"
    else:
        should_pay_loan_df["event"] = "Loan Payment OK"

    ### Scenario 2 - pay the loan with balance less than the amount to pay and get a default and change slightly spender_prof_rate
    should_pay_loan_df = change_spender_profile(should_pay_loan_df, low_balance_crit, -0.1)
    should_pay_loan_df = change_spender_profile(should_pay_loan_df, negative_balance_crit, -0.15)

    should_pay_loan_df.loc[low_balance_crit,"loan_exp_val"] += should_pay_loan_df.loc[low_balance_crit, "balance"]
    should_pay_loan_df.loc[low_balance_crit,"loan_exp_rate"] += should_pay_loan_df.loc[low_balance_crit, "balance"]/should_pay_loan_df.loc[low_balance_crit,"income"]

    ### not paid amount will be added to the loan with interest rate

    not_paid_amount = should_pay_loan_df.loc[low_balance_crit, "amount_to_pay"] - should_pay_loan_df.loc[low_balance_crit, "balance"]
    added_interest = not_paid_amount*(1 + should_pay_loan_df.loc[low_balance_crit, "interest_rate"])
    should_pay_loan_df.loc[low_balance_crit, "loan"] = should_pay_loan_df.loc[low_balance_crit, "loan"]+added_interest
    
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

def life_moment_score(df_all_records, df_dead):
    df2 = df_all_records.copy()

    max_year = df2["year"].max()

    ### 1. got married 
    # - use calculate marriage cost - also might trigger a loan
    # - increase the chance of buying life insurance 
    # - increase the chances of buying a house - also might trigger a loan
    ### 2. birth of a child
    # - increase the chance of buying life insurance
    # - increase the cost of living
    # - increase the chance of buying a house - also might trigger a loan
    ### 3. death of a relative
    # - increases the chance of buying life insurance

    ### Get the last and current year records

    max_year_crit = df2["year"] == max_year
    prev_year_crit = df2["year"] == max_year - 1

    ### cols to check for life moments
    life_moment_cols = ["unique_name_id", "marital_status", "existing_children_count", "parent_name_id_A", "parent_name_id_B","spouse_name_id"]
    current_year_df = df2[max_year_crit].copy()[life_moment_cols]
    previous_year_df = df2[prev_year_crit].copy()[life_moment_cols]

    ### Compare the two dataframes to get the life moments by unique_name_id
    life_moments = current_year_df.merge(previous_year_df, on="unique_name_id", how="left", suffixes=("", "_prev"))
    marital_crit = life_moments["marital_status"] != life_moments["marital_status_prev"]
    baby_born = life_moments["existing_children_count"] != life_moments["existing_children_count_prev"]
    life_moments["life_moment_score"] = 0
    life_moments.loc[marital_crit, "life_moment_score"] += 1
    life_moments.loc[baby_born, "life_moment_score"] += 1
    
    ### Get the deceased people in 3 parts  - parents, children, spouse
    deceased_ids = df_dead["unique_name_id"].unique()

    ### if deceased_id is in parent_name_id_A or parent_name_id_B, then the person affected by grief is the unique_name_id
    child_grief_crit = life_moments["parent_name_id_A"].isin(deceased_ids) | life_moments["parent_name_id_B"].isin(deceased_ids)
    life_moments.loc[child_grief_crit, "life_moment_score"] += 1

    ### if deceased_id is in spouse_name_id, then the person affected by grief is the unique_name_id
    spouse_grief_crit = life_moments["spouse_name_id"].isin(deceased_ids)
    life_moments.loc[spouse_grief_crit, "life_moment_score"] += 1

    ### if deceased_id is in unique_name_id, then the person affected by grief is the parent_name_id_A or parent_name_id_B
    parent_grief_crit = previous_year_df["unique_name_id"].isin(deceased_ids)
    parent_a_ids = previous_year_df[parent_grief_crit]["parent_name_id_A"].unique()
    parent_b_ids = previous_year_df[parent_grief_crit]["parent_name_id_B"].unique()

    parent_grief_crit = life_moments["unique_name_id"].isin(parent_a_ids) | life_moments["unique_name_id"].isin(parent_b_ids)
    life_moments.loc[parent_grief_crit, "life_moment_score"] += 1

    ### update the life_moment_score df2 in the current year only
    df2 = df2.merge(life_moments[["unique_name_id", "life_moment_score"]], on="unique_name_id", how="left")
    ### this generates 2 columns - life_moment_score_x and life_moment_score_y
    ### keep only the life_moment_score_y for the current year and keep
    df2["life_moment_score"] = df2["life_moment_score_x"]
    ### replace life_moment_score current year with life_moment_score_y
    df2.loc[max_year_crit, "life_moment_score"] = df2.loc[max_year_crit, "life_moment_score_y"]
    ### drop the life_moment_score_x and life_moment_score_y columns
    df2 = df2.drop(columns=["life_moment_score_x", "life_moment_score_y"], errors='ignore')
    return df2

def get_house_price_from_room_count(room_count:int):
    ### get house size_range_m2 from HOUSE_SIZE_DF
    rcount_filt = HOUSE_DF["room_count"] == room_count
    size_range = HOUSE_DF[rcount_filt]["house_size_range_m2"].values[0]
    ### randomly select a house size from the size_range
    house_size = random.uniform(size_range[0], size_range[1])
    ### get the house price from the house size
    min_house_price = HOUSE_DF[rcount_filt]["min_price_per_m2"].values[0]
    max_house_price = HOUSE_DF[rcount_filt]["max_price_per_m2"].values[0]
    house_price = house_size * random.uniform(min_house_price, max_house_price)

    return house_price

def solve_couples_distinct_house(df):
    ### get the current year and check if there are married people that have distinct houses
    max_year = df["year"].max()
    max_year_crit = df["year"] == max_year
    married_crit = df["marriage_status"] == True
    
    cols = ["unique_name_id", "spouse_name_id","house_id","house_price",
            "loan","loan_term","loan_interest_rate"]
    
    married_current = max_year_crit & married_crit
    current_year_df = df[married_current].copy()[cols]
    if married_current.sum() == 0:
        return df
    
    person_a = current_year_df.copy().drop(columns=["spouse_name_id"], errors='ignore')
    person_b = current_year_df.copy().drop(columns=["unique_name_id"], errors='ignore')
    ### rename spouse_name_id to unique_name_id
    person_b = person_b.rename(columns={"spouse_name_id": "unique_name_id"})
    ### merge the two dataframes and add suffixes
    merged_df = person_a.merge(person_b, on="unique_name_id", how="left", suffixes=("_a", "_b"))
    ### check if the house_id is the same
    same_house_crit = merged_df["house_id_a"] == merged_df["house_id_b"]

    ### drop the same house_id
    differnt_houses_df = merged_df[~same_house_crit].copy()

    ### criteria 1 - A has a house and B does not have a house (None)
    a_has_house_crit = differnt_houses_df["house_id_a"].notna()
    b_has_no_house_crit = differnt_houses_df["house_id_b"].isna()

    a_has_H_b_nH = differnt_houses_df[a_has_house_crit & b_has_no_house_crit].copy()
    a_has_H_b_nH["house_id_b"] = a_has_H_b_nH["house_id_a"]
    ### split the house price to A and B
    a_has_H_b_nH["house_price_b"] = a_has_H_b_nH["house_price_a"]/2
    a_has_H_b_nH["house_price_a"] = a_has_H_b_nH["house_price_a"]/2

    ### review the loan and loan term for A and B - refinance both loans
    ### bring the loan to the current base value, use the same loan term

    base_value_a = a_has_H_b_nH["loan_a"]/\
                   ((1 + a_has_H_b_nH["loan_interest_rate_a"])**\
                   a_has_H_b_nH["loan_term_a"])
    
    base_value_b = a_has_H_b_nH["loan_b"]/\
                   ((1 + a_has_H_b_nH["loan_interest_rate_b"])**\
                    a_has_H_b_nH["loan_term_b"])

    ### get min rate and max loan term to refinance the loan and split the loan
    min_rate = a_has_H_b_nH[["loan_interest_rate_a", "loan_interest_rate_b"]].min(axis=1)
    max_term = a_has_H_b_nH[["loan_term_a", "loan_term_b"]].max(axis=1)

    total_value = (base_value_a + base_value_b)* (1 + min_rate)**max_term

    a_has_H_b_nH["loan_a"] = total_value/2
    a_has_H_b_nH["loan_b"] = total_value/2
    a_has_H_b_nH["loan_term_a"] = max_term
    a_has_H_b_nH["loan_term_b"] = max_term
    a_has_H_b_nH["loan_interest_rate_a"] = min_rate
    a_has_H_b_nH["loan_interest_rate_b"] = min_rate

    ### criteria 2 - A does not have a house and B has a house - Solved in criteria 1

    ### criteria 3 - A has a house and B has a house but different house_id
    a_has_house_crit = differnt_houses_df["house_id_a"].notna()
    b_has_house_crit = differnt_houses_df["house_id_b"].notna()
    diff_house_id_crit = differnt_houses_df["house_id_a"] != differnt_houses_df["house_id_b"]
    diff_crit = a_has_house_crit & b_has_house_crit & diff_house_id_crit

    a_has_H_b_has_H = differnt_houses_df[diff_crit].copy()
    
    ### sum the house price for A and B
    a_has_H_b_has_H["house_price_a"] = a_has_H_b_has_H["house_price_a"] + a_has_H_b_has_H["house_price_b"]
    a_has_H_b_has_H["house_price_b"] = a_has_H_b_has_H["house_price_a"] + a_has_H_b_has_H["house_price_b"]

    ### refinance the loan for A and B using the highest loan term and the lowest interest rate
    ### generate a new house_id for A and B that combines the house_id_a and house_id_b
    a_has_H_b_has_H["house_id_a"] = a_has_H_b_has_H["house_id_a"].astype(str) +\
                                    a_has_H_b_has_H["house_id_b"].astype(str)
    a_has_H_b_has_H["house_id_b"] = a_has_H_b_has_H["house_id_a"]

    ### refinance the loan for A and B
    base_value_a = a_has_H_b_has_H["loan_a"]/\
                     ((1 + a_has_H_b_has_H["loan_interest_rate_a"])**\
                        a_has_H_b_has_H["loan_term_a"])
    
    base_value_b = a_has_H_b_has_H["loan_b"]/\
                        ((1 + a_has_H_b_has_H["loan_interest_rate_b"])**\
                            a_has_H_b_has_H["loan_term_b"]) 
    
    min_rate = a_has_H_b_has_H[["loan_interest_rate_a", "loan_interest_rate_b"]].min(axis=1)
    max_term = a_has_H_b_has_H[["loan_term_a", "loan_term_b"]].max(axis=1)

    total_value = (base_value_a + base_value_b)* (1 + min_rate)**max_term

    a_has_H_b_has_H["loan_a"] = total_value/2
    a_has_H_b_has_H["loan_b"] = total_value/2
    a_has_H_b_has_H["loan_term_a"] = max_term
    a_has_H_b_has_H["loan_term_b"] = max_term
    a_has_H_b_has_H["loan_interest_rate_a"] = min_rate
    a_has_H_b_has_H["loan_interest_rate_b"] = min_rate

    ### update the current_year_df with the new values
    combined_changes_df = pd.concat([a_has_H_b_nH, a_has_H_b_has_H]).sort_index()
    ### select cols that end with _a into a new dataframe and cols that end with _b into a new dataframe
    dfa = combined_changes_df.copy()
    dfb = combined_changes_df.copy()
    ### drop cols that end with _b in dfa and cols that end with _a in dfb
    dfa = dfa.drop(columns=[col for col in dfa.columns if col.endswith("_b")], errors='ignore')
    dfb = dfb.drop(columns=[col for col in dfb.columns if col.endswith("_a")], errors='ignore')
    ### rename the cols in dfb to remove the _b suffix
    to_rename = {col: col.replace("_b", "") for col in dfb.columns}
    dfb = dfb.rename(columns=to_rename)
    ### rename the cols in dfa to remove the _a suffix
    to_rename = {col: col.replace("_a", "") for col in dfa.columns}
    dfa = dfa.rename(columns=to_rename)
    ### concat the two dataframes and sort by index
    combined_changes_df_part2 = pd.concat([dfa, dfb]).sort_index()
    ### merge the combined_changes_df_part2 with the current_year_df and replace the values with the new values
    current_year_df = current_year_df.merge(combined_changes_df_part2, 
                                            on="unique_name_id", 
                                            how="left", 
                                            suffixes=("", "_new"))
    ### replace the values with the new values when the new values are not null
    for col in combined_changes_df_part2.columns:
        crit = current_year_df[col + "_new"].notna()
        current_year_df.loc[crit, col] = current_year_df.loc[crit, col + "_new"]
    ### drop the cols that end with _new
    current_year_df = current_year_df.drop(columns=[col for col in current_year_df.columns if col.endswith("_new")], errors='ignore')

    ### update the df with the new values
    ### drop the unique_name_id that are in current_year_df
    to_drop = current_year_df["unique_name_id"].unique()
    to_drop_crit = df["unique_name_id"].isin(to_drop) & max_year_crit
    df2 = df[~to_drop_crit].copy()
    ### concat the current_year_df with the df2
    df2 = pd.concat([df2, current_year_df]).sort_index()
    return df2

def buy_or_upgrade_house(df):
    ### get the current year
    if True:
        df2 = df.copy()
        
        buy_or_upg_cols = ["unique_name_id", 'age', 'career','spender_prof',"age_range","marriage_status","existing_children_count",
                            'loan','house_price','house_id', 'balance','loan_term','loan_interest_rate' ]
        prob_merge_cols = ["career", "spender_prof","age_range","marriage_status","existing_children_count"]

        current_year_df = df2[buy_or_upg_cols].copy()
        current_year_df = current_year_df.merge( HOUSE_PROBABILITY_FACTORS[prob_merge_cols+["base_house_likelihood"]], 
                                                on=prob_merge_cols, how="left").fillna(0) ### add the base_house_likelihood column

        married_crit = current_year_df["marriage_status"] == True

        new_cols_df = current_year_df.copy()
        new_cols_df["room_count"] = new_cols_df["marriage_status"].fillna(0).astype(int)+\
                                    new_cols_df["existing_children_count"].fillna(0).astype(int) + 1
        
        new_cols_df["house_price_new"] = new_cols_df["room_count"].apply(get_house_price_from_room_count).fillna(0)

        new_cols_df["house_price_previous"] = new_cols_df["house_price"].fillna(0)
        new_cols_df.loc[married_crit, "house_price_previous"] = new_cols_df.loc[married_crit, "house_price_previous"]*2
        
        buy_house_prob = random.uniform(0, 1)
        might_buy_crit = buy_house_prob < current_year_df["base_house_likelihood"]
        upgrade_check = new_cols_df["house_price_previous"] < new_cols_df["house_price_new"]
        might_buy_crit = new_cols_df["user_house_likelihood"] < new_cols_df["base_house_likelihood"]

        career_crit = new_cols_df["career"].isin(list(INITIAL_INCOME_RANGES.keys())[2:-1])
        combined_crit = might_buy_crit & career_crit & upgrade_check
        print("will buy a house: ", combined_crit.sum())

    if combined_crit.sum() == 0:
        return df2
    base_mortgage_rate = INTEREST_RATE_PER_TYPE["mortgage"]

    ### generate new columns for every person regardless of the criteria then we will only update the ones that meet the criteria
    new_cols_df["loan_interest_rate_new"] = (base_mortgage_rate + random.uniform(-1, 2))/100
    new_cols_df["loan_term_new"] = random.randint(20, 30)
    new_cols_df["down_payment_new"] = random.uniform(0.1, 0.2)
    ### bring the loan to the current base value if loan is not 0
    base_value = new_cols_df["loan"]/((1 + new_cols_df["loan_interest_rate"])**new_cols_df["loan_term"])
    new_cols_df["loan_base"] = base_value.fillna(0)

    amount_due_single = new_cols_df["house_price_new"] - new_cols_df["house_price_previous"] + new_cols_df["loan_base"]
    ### this assumes that the person will pay the down payment and the rest will be the loan
    current_year_df["loan_base_new_single"] = amount_due_single * (1 - new_cols_df["down_payment_new"])
    
    ### if single then the loan_new will replace the loan and the balance_new will be deducted from the balance

    down_payment_val = current_year_df["down_payment_new"]*amount_due_single.fillna(0)
    current_year_df["loan_exp_val"] = down_payment_val
    current_year_df["loan_exp_rate"] = down_payment_val/current_year_df["income"].fillna(1)

    new_cols_df["balance_new_single"] = new_cols_df["balance"] -\
                                            new_cols_df["loan_base_new_single"]*\
                                            new_cols_df["down_payment_new"]
    
    new_cols_df["loan_new_single"] = new_cols_df["loan_base_new"]*\
                                        ((1 + new_cols_df["loan_interest_rate_new"])**\
                                        new_cols_df["loan_term_new"])
    
    ### add a random number to the house_id
    new_cols_df["house_id_new"] = "house_" + np.random.randint(0, 100000, new_cols_df.shape[0]).astype(str)

    ### if married then we merge both dataframes 
    partner_a = new_cols_df.copy()
    partner_b = new_cols_df.copy()

    partner_a_list = partner_a["unique_name_id"][combined_crit].unique()
    parter_a_as_spouse = new_cols_df["spouse_name_id"].isin(partner_a_list)
    partner_b = partner_b[~parter_a_as_spouse].copy()
    partner_b_list = partner_b["unique_name_id"][combined_crit].unique()

    ### subtract the partner_a_list from partner_b_list
    partner_b_list = [x for x in partner_b_list if x not in partner_a_list]
    partner_b = partner_b[partner_b["unique_name_id"].isin(partner_b_list)].copy()
    partner_b = partner_b.drop(columns=["spouse_name_id"], errors='ignore').rename(columns={"unique_name_id": "spouse_name_id"})
    couples_df = partner_a.merge(partner_b, on = "spouse_name_id", how="left", suffixes=("_a", "_b"))

    ### get highest loan term, lowest interest rate min new house price, mean previous house price, sum loan, sum balance
    couples_df["loan_term_new"] = couples_df[["loan_term_new_a", "loan_term_new_b"]].max(axis=1)
    couples_df["loan_interest_rate_new"] = couples_df[["loan_interest_rate_new_a", "loan_interest_rate_new_b"]].min(axis=1)
    couples_df["house_price_new"] = couples_df[["house_price_new_a", "house_price_new_b"]].min(axis=1)
    
    couples_df["previous_house_price"] = couples_df[["previous_house_price_a", "previous_house_price_b"]].mean(axis=1)
    couples_df["down_payment_new"] = couples_df[["down_payment_new_a", "down_payment_new_b"]].min(axis=1)
    couples_df["loan_base"] = couples_df[["loan_base_a", "loan_base_b"]].sum(axis=1)
    couples_df["balance"] = couples_df[["balance_a", "balance_b"]].sum(axis=1)
    amount_due_couples = couples_df["house_price_new"] - couples_df["previous_house_price"] + couples_df["loan_base"]
    down_payment_val_couples = couples_df["down_payment_new"]*amount_due_couples.fillna(0)
    ### loan_exp_val and loan_exp_rate should consider the down payment and each person's income
    income_exp_sharing_rate = couples_df["income_a"]/(couples_df["income_a"] + couples_df["income_b"]) ### this way the loan_exp_rate will be shared according to the income

    ### this only includes the down payment - loan payment will be calculated later and will update the loan_exp_val and loan_exp_rate (pay_loan function)
    couples_df["loan_exp_val_a"] = down_payment_val_couples*income_exp_sharing_rate
    couples_df["loan_exp_val_b"] = down_payment_val_couples*(1 - income_exp_sharing_rate)
    couples_df["loan_exp_rate_a"] = couples_df["loan_exp_val_a"]/couples_df["income_a"]
    couples_df["loan_exp_rate_b"] = couples_df["loan_exp_val_b"]/couples_df["income_b"]

    couples_df["loan_base_new_couples"] = amount_due_couples * (1 - couples_df["down_payment_new"])
    couples_df["balance_new_couples"] = couples_df["balance"] - couples_df["loan_base_new_couples"]*couples_df["down_payment_new"]
    couples_df["balance_a"] = couples_df["balance_new_couples"]*income_exp_sharing_rate
    couples_df["balance_b"] = couples_df["balance_new_couples"]*(1 - income_exp_sharing_rate)
    couples_df["loan_new_couples"] = couples_df["loan_base_new_couples"]*((1 + couples_df["loan_interest_rate_new"])**couples_df["loan_term_new"])
    ### split the loan total between the two partners
    couples_df["loan_new_a"] = couples_df["loan_new_couples"]*income_exp_sharing_rate
    couples_df["loan_new_b"] = couples_df["loan_new_couples"]*(1 - income_exp_sharing_rate)
    couples_df["house_id_new"] = couples_df["house_id_new_a"] ### to ensure that the house_id_new will be the same for both partners

    ### get list of unique_name_id that meet the criteria for buying a house
    singles_list = new_cols_df["unique_name_id"][combined_crit].unique()
    couples_A_list = couples_df["unique_name_id"][combined_crit].unique()
    couples_B_list = couples_df["spouse_name_id"][combined_crit].unique()

    new_cols_couples_df2 = new_cols_df.copy().drop(columns=["house_id_new", "house_price_new", "loan_term_new", "loan_interest_rate_new"], errors='ignore')
    ### update the new_cols_df with the new values - couples A & B by merging the dataframes selecting only the valid columns
    #drop house_id_new, house_price_new, loan_term_new, loan_interest_rate_new (single values)

    new_cols_couples_df2 = new_cols_couples_df2.merge(couples_df[["unique_name_id", "loan_new_a", "loan_new_b","balance_a", "balance_b",
                                                                  "loan_exp_val_a", "loan_exp_val_b", "loan_exp_rate_a", "loan_exp_rate_b",
                                                                  "house_id_new", "house_price_new", "loan_term_new", "loan_interest_rate_new"]],
                                                       on="unique_name_id", how="left" )
    
    to_update_dict = {"single": singles_list, "couples_a": couples_A_list, "couples_b": couples_B_list}
    ### update twith the new values - using loc to avoid SettingWithCopyWarning and overwrite those that will not buy a house
    for key, list_values in to_update_dict.items():
        if key == "single":
            df2_nc = new_cols_df
            multiplier = 1
            loan_col = "loan_new_single"
            balance_col = "balance_new_single"
            loan_exp_col = "loan_exp_val"
            loan_exp_rate_col = "loan_exp_rate"

        else:
            multiplier = 0.5
            df2_nc = new_cols_couples_df2
            if key == "couples_a":
                loan_col = "loan_new_a"
                balance_col = "balance_a"
                loan_exp_col = "loan_exp_val_a"
                loan_exp_rate_col = "loan_exp_rate_a"
            elif key == "couples_b":
                loan_col = "loan_new_b"
                balance_col = "balance_b"
                loan_exp_col = "loan_exp_val_b"
                loan_exp_rate_col = "loan_exp_rate_b"

            else:
                raise ValueError("Invalid Value for Buying a House - Update Loan and Balance Columns")

        critA = df2_nc["unique_name_id"].isin(list_values)
        critB = df2["unique_name_id"].isin(list_values)
        df2.loc[critB, "house_id"] = df2_nc.loc[critA, "house_id_new"]
        df2.loc[critB, "house_price"] = df2_nc.loc[critA, "house_price_new"]*multiplier ### this is the only value that is split equally/ all others are split by income
        df2.loc[critB, "loan"] = df2_nc.loc[critA, loan_col]
        df2.loc[critB, "balance"] = df2_nc.loc[critA, balance_col]
        df2.loc[critB, "loan_term"] = df2_nc.loc[critA, "loan_term_new"]
        df2.loc[critB, "loan_interest_rate"] = df2_nc.loc[critA, "loan_interest_rate_new"]
        df2.loc[critB, "loan_exp_val"] = df2_nc.loc[critA, loan_exp_col]
        df2.loc[critB, "loan_exp_rate"] = df2_nc.loc[critA, loan_exp_rate_col]

    return df2

def update_housing_expenditure(df):
    ### if person has a house then the housing expenditure is the loan payment
    ### if person does not have a house then the housing expenditure will be the existing housing expenditure
    ### get the current year
    df2 = df.copy()
    current_year_df = df2

    ### check if the person has a house using house_id
    has_house_crit = current_year_df["house_id"].notna() | current_year_df["house_id"] != "None" | current_year_df["house_id"] != ""
    ### if has_house_crit 
    if has_house_crit.sum() == 0:
        return df2
    
    ### split the dataframe into 2 - those with houses and those without houses
    has_house_df = current_year_df[has_house_crit].copy()
    no_house_df = current_year_df[~has_house_crit].copy()

    ### new housing_expenditure_val will be loan/loan_term
    ### if current housing_exp_val is null then housing_expenditure will be the new housing_expenditure_val
    ### if current housing_exp_val is not null then housing_expenditure_val will be the current housing_exp_val
    ### else calculate the housing_expenditure_val delta - if new is higher then expenditure will be the new value and rate will increase
    ### if new is lower then expenditure will be the new value and rate will decrease and the difference will be added to savings_exp_value





    ### loan will be the amount due divided by the loan term
    has_house_df["housing_exp_val_new"] = has_house_df["loan"]/has_house_df["loan_term"]

    
    ### divide by 


    # "savings_exp_rate"
    # "savings_exp_value"
    # "housing_exp_rate"
    # "housing_exp_value"


    current_year_df.loc[has_house_crit, "housing_expenditure"] = current_year_df.loc[has_house_crit, "loan"]/current_year_df.loc[has_house_crit, "loan_term"]

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