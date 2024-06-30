#%%
### import modules
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from modules.marriage_functions import get_marriage_pairs, calculate_marriage_cost
from modules.born_functions import children_born
from modules.financial_functions import *
from modules.utils_and_tests import *
from modules.constants import *
import warnings
import matplotlib.pyplot as plt
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
import tqdm
from logging import getLogger
logger = getLogger(__name__)
########################################### Generate Functions ###########################################
def generate_init_df(population, year, age_range):
    """
    Generate initial population dataframe
    """
    # generate initial population
    df = pd.DataFrame()
    min_age = AGE_RANGES[age_range][0]
    max_age = AGE_RANGES[age_range][1]
    df['age'] = np.random.randint(min_age, max_age, population)
    df["year"] = year
    df['age_range'] = age_range

    ### set gender using GENDER_PROBS
    df["gender"] = np.random.choice(list(GENDER_PROBS.keys()),
                                    population,
                                    p=np.array(list(GENDER_PROBS.values())))

    return df

def generate_names_and_initial_data(df,population):
    ### count Males and get index
    gd = df['gender'] == "Male"
    ### generate unique male names using numpy
    df.loc[gd, "first_name"] = np.random.choice(MALE_FIRST_NAMES,gd.sum())
    #print("male names",gd.sum())              
    df.loc[~gd, "first_name"] = np.random.choice(FEMALE_FIRST_NAMES,len(gd) - gd.sum())
    #print("female names",len(gd) - gd.sum())
    df["last_name"] = np.random.choice(LAST_NAMES, population)
    df["event"] = "Created"
    df["full_name"] = df["first_name"] + " " + df["last_name"]

    str_num = np.random.randint(0, 1000000000, population)
    df["temp_id"] = str_num
    df["unique_name_id"] = df["first_name"] + "_" +\
                           df["last_name"] + "_"+\
                           df["temp_id"].astype(str)
    
    df.drop(columns=["temp_id"], inplace=True)

    df['parent_name_id_A'] = np.random.choice(MALE_FIRST_NAMES,population)
    df['parent_name_id_A'] += " " + df["last_name"]
    df['parent_name_id_B'] = np.random.choice(FEMALE_FIRST_NAMES,population)
    df['parent_name_id_B'] += " " + df["last_name"]
    df = generate_initial_constants(df)
    df = create_initial_expenditure_values(df)
    return df

def generate_past_events(df, debug_print=False):
    """
    Generate past events for initial population
    """
    df_past = df.copy()
    ### drop columns that are not needed
    try:
        to_drop = ['first_name', 'last_name', 'full_name']
        df_past.drop(columns=to_drop, inplace=True)
    except:
        pass

    ### calculate year of birth
    df_past["year"] = df_past["year"] - df_past["age"]
    df_past["event"] = "Born"
    df_past["age"] = 0

    ### current year - create event
    max_year = df["year"].max()
    
    ### birth_year
    dfs = []

    for birth_year in df_past["year"].unique():
        dfs_temp = []
        ### count how many age up events to generate
        age_up_count = max_year - birth_year

        for i in range(age_up_count):
            if i == 0:
                df_temp = df_past[df_past["year"] == birth_year].copy()
            else:
                if debug_print:
                    #print(f"Past Events:  Year: {birth_year} Age: {i} Population: {len(df_temp)}")
                    pass
                df_temp = dfs_temp[-1].copy()

            df_temp = generate_complete_year_age_up_pipeline(df_temp, basic_mode=False)

            dfs_temp.append(df_temp)
            dfs.append(df_temp)
    df_past2 = pd.concat(dfs)

    df_past_final = pd.concat([df_past, df_past2])

    return df_past_final
 
def generate_complete_year_age_up_pipeline(df, debug_print=False, basic_mode=False):
    year = df["year"].max()
    mask = df['year'] == year
    #print(f"Generating year {year+1}")
    df_length = {"Total": len(df)}
    if mask.sum() == 0:
        return df
    df2 = df[mask].copy()
    df_length["year_lenght"] = len(df2)

    df2, dfd = remove_dead_people(df2)
    df_length["non_dead_people"] = len(df2)

    df2 = share_distribution(df2, dfd)
    df_length["share_distribution"] = len(df2)

    df2 = check_function_for_duplication(age_up_df, df2)
    df_length["age_up"] = len(df2)

    df2 = check_function_for_duplication(calculate_death_df, df2)
    df_length["death_calc"] = len(df2)

    df2 = check_function_for_duplication(handle_pocket_money, df2)
    df_length["pocket_money"] = len(df2)

    df2 = check_function_for_duplication( handle_fut_career, df2)
    df_length["fut_career"] = len(df2)

    df2 = check_function_for_duplication(student_loan, df2)
    df_length["student_loan"] = len(df2)

    df2 = check_function_for_duplication(update_years_of_study, df2)
    df_length["years_of_study"] = len(df2)

    df2 = check_function_for_duplication(handle_finished_studies, df2)
    df_length["finished_studies"] = len(df2)

    df2 = check_function_for_duplication(handle_part_time, df2)
    df_length["part_time"] = len(df2)

    df2 = check_function_for_duplication(get_a_raise, df2)
    df_length["raise"] = len(df2)

    df2 = check_function_for_duplication(define_partner_type, df2)
    df_length["partner_type"] = len(df2)

    if basic_mode:
        #df2 = check_function_for_duplication(handle_marriage_array, df2)
        df2 = time_function(handle_marriage_array, df2)
        df_length["marriage"] = len(df2)

        df2 = check_function_for_duplication(children_born, df2)
        df_length["children_born"] = len(df2)

    df2 = check_function_for_duplication(update_expenditure_rates, df2)
    df_length["expenditure_rates"] = len(df2)

    df2 = check_function_for_duplication(handle_expenditure_value, df2)
    df_length["expenditure_value"] = len(df2)

    df2 = check_function_for_duplication(update_account_balance_v2, df2)
    df_length["account_balance"] = len(df2)

    df2  = solve_couples_distinct_house(df2)
    df_length["couples_distinct_households"] = len(df2)

    df2 = life_moment_score(df2,dfd)
    df_length["life_moment_score"] = len(df2)
    
    df2 = check_function_for_duplication(pay_loan, df2)
    df_length["pay_loan"] = len(df2)
    #df2 = check_function_for_duplication(share_distribution, df, dfd)




    df2 = pd.concat([df2, dfd])
    df_length["combined"] = len(df2)


    return df2

def generate_complete_city(years, age_range="Young Adult", population=40000, start_year=1950, debug_print=False):
    ### Print the start year
    df = time_function(generate_init_df, population, start_year, age_range)
    df = time_function(generate_names_and_initial_data, df, population)
    ### generate past events
    print("\n ####   Generating past events ####\n")
    df_past = time_function(generate_past_events, df, debug_print)
    df2 = df_past.copy()
    #dfs = []
    for year in tqdm.tqdm(range(years)):
        ### generate new year
        df2up = generate_complete_year_age_up_pipeline(df2, basic_mode=True, debug_print=debug_print)
        df2 = pd.concat([df2, df2up], ignore_index=True)

    dfs_final = pd.concat([df_past, df2])

    ### data quality check - marriage status
    print("Marriage Status Data Quality Check")
    ### Marriage status should be either True or False or None
    is_nan = dfs_final["marriage_status"].isna()
    is_true = dfs_final["marriage_status"] == True
    is_false = dfs_final["marriage_status"] == False
    is_valid = is_nan | is_true | is_false
    ### if not valid print the unique values and replace with None
    if len(dfs_final[~is_valid]) > 0:
        # count unique values
        print(dfs_final[~is_valid]["marriage_status"].value_counts())
        dfs_final.loc[~is_valid, "marriage_status"] = None

    ### data quality check - Gender should be either Male or Female otherwise drop rows
    print("Gender Data Quality Check")
    gender_check = dfs_final["gender"].isin(["Male","Female"])
    if len(dfs_final[~gender_check]) > 0:
        print(gender_check.sum())
        dfs_final = dfs_final[gender_check]
    
    return dfs_final

########################################### Event Functions ###########################################
def age_up_df(df):
    df2 = df.copy()

    df2['age'] = df2['age'] + 1
    df2['year'] = df2['year'] + 1
    ### drop old age_range column
    try:
        df2.drop(columns=['age_range'], inplace=True)
    except:
        pass
    try:
        df2.drop(columns=['age_event'], inplace=True)
    except:
        pass

    df2 = df2.merge(AGE_RANGE_DF, on='age', how='left')
    ### if age is 0 keep event as born else replace with age_event
    df2['event'] = np.where(df2['age'] == 0, "Born", df2['age_event'])

    return df2

def calculate_death_chance_v2(age,gender):
    #print(age)
    ### the model predicts the probability of living and returns the probability of dying
    if gender == "Male":
        gender_val =  1.2
    elif gender == "Female":
        gender_val = 2

    ### pred_poly values ranges from 1 100 - a value of 100 means will live, 0 means will die 
    pred_poly = DEATH_PROB_MODEL_COEF_NEW['age^1']*age +\
                DEATH_PROB_MODEL_COEF_NEW['age^2']*age**2 +\
                DEATH_PROB_MODEL_COEF_NEW['age^3']*age**3 +\
                DEATH_PROB_MODEL_COEF_NEW['age^4']*age**4 +\
                DEATH_PROB_MODEL_COEF_NEW['age^5']*age**5 +\
                DEATH_PROB_MODEL_COEF_NEW['gender^1']*gender_val +\
                DEATH_PROB_MODEL_COEF_NEW['gender^2']*gender_val**2 +\
                DEATH_PROB_MODEL_COEF_NEW['gender^3']*gender_val**3 +\
                DEATH_PROB_MODEL_COEF_NEW['gender^4']*gender_val**4 +\
                DEATH_PROB_MODEL_COEF_NEW['gender^5']*gender_val**5 +\
                DEATH_PROB_MODEL_COEF_NEW['intercept']
    
    if pred_poly > 100:
        death_prob = 0.000001

    elif age > 100:
        death_prob = 0.999999
    else:
        death_prob = 1- pred_poly/100 #

    return death_prob

def calculate_death_chance_crit_ill(age):
    prob = CRIT_ILL_DEATH_PROB_MODEL_COEF['age']*age +\
            CRIT_ILL_DEATH_PROB_MODEL_COEF['age_sq']*age**2 +\
            CRIT_ILL_DEATH_PROB_MODEL_COEF['age_cub']*age**3 +\
            CRIT_ILL_DEATH_PROB_MODEL_COEF['age_qd']*age**4 +\
            CRIT_ILL_DEATH_PROB_MODEL_COEF['intercept']
    # if age <20:
    #     prob = 0
    # elif age >=20 and age < 40:
    #     prob = np.abs(prob)

    # elif age >=40 and age < 55:
    #     prob = np.abs(prob)/3

    # elif age >=55 and age < 60:
    #     prob = np.abs(prob)
    prob = np.abs(prob)

    return prob

def calculate_death_df(df):
    df2 = df.copy()
    ### remove people who has age nan
    #df2 = df2[(~df2['age'].isna()) | (df2['age'].str() != "nan")]
    ### remove dead people
    try:
        df2['age_death_thresh'] = df2.apply(
                lambda x: calculate_death_chance_v2(x['age'], x['gender']), axis=1)
    except:
        print(f"{len(df2)} people in dataframe")
        return df2
    ### generate random number to compare with death threshold
    df2["age_death_prob"] = np.random.rand(len(df2))
    ### use calculate_death_chance_crit_ill
    df2['ci_death_thresh'] = df2.apply(
        lambda x: calculate_death_chance_crit_ill(x['age']), axis=1)
    ### generate random number to compare with death threshold
    df2["ci_death_prob"] = np.random.rand(len(df2))
    df2["servere_accident_prob"] = np.random.rand(len(df2))
    df2["infant_death_prob"] = np.random.rand(len(df2))

    df2['age_death_status'] = np.where(df2['age_death_prob'] < df2['age_death_thresh'], 1, 0)
    df2['ci_death_status'] = np.where(df2['ci_death_prob'] < df2['ci_death_thresh'], 1, 0)
    df2['severe_accident_status'] = np.where(df2['servere_accident_prob'] < SEVERE_ACCIDENT_DEATH_PROB, 1, 0)
    infant_death_check = (df2['infant_death_prob'] < INFANT_DEATH_PROB) & (df2['age'] <= INFANT_DEATH_AGE)
    df2['infant_death_status'] = np.where(infant_death_check, 1, 0)

    df2['death_status'] = np.where(df2['infant_death_status'] == 1, 
                                        "Death - Unexpected Infant Death", 
                                np.where(df2['severe_accident_status'] == 1,
                                            "Death - Severe Accident",
                                np.where(df2['ci_death_status'] == 1,
                                            "Death - Critical Illness",
                                np.where(df2['age_death_status'] == 1,
                                                "Death - Age",
                                                ""))))
    ### replace event with death status
    df2.loc[df2['death_status'] != "", "event"] = df2.loc[df2['death_status'] != "", "death_status"]

    # print("Death Input", len(df), "Death Output", len(df2))
    return df2

def remove_dead_people(df):
    df2 = df.copy()
    try:
        is_dead_mask = df2['event'].str.contains("Death")
        death_count = is_dead_mask.sum()
        if death_count > 0:
            #print("Dead people", is_dead_mask.sum())
            pass
        df2 = df2[~is_dead_mask]
        dfd = df2[is_dead_mask]
    except:
        if len(df2) == 0:
            #print("No people in dataframe")
            dfd = pd.DataFrame()
        dfd = pd.DataFrame()
    return df2, dfd

def handle_pocket_money(df):
    df2 = df.copy()
    age_crit = df2["age"] == POCKET_MONEY_AGE
    if age_crit.sum() == 0:
        return df2
    
    #print(f"Pocket Money: {age_crit.sum()} vs {(~age_crit).sum()}")
    df_rest = df2[~age_crit].copy()
    df2 = df2[age_crit].copy()  

    df2["career"] = "Pocket Money"
    base_income = INITIAL_INCOME_RANGES['Pocket Money'][0]
    std_deviation = INITIAL_INCOME_RANGES['Pocket Money'][1]
    pocket_money = np.abs(np.round(np.random.normal(base_income, std_deviation,len(df2)),2))
    df2["income"] = pocket_money

    ### append dead people and rest of the population
    df2["spender_prof"] = np.random.choice( list(SPENDER_PROFILE_PROBS.keys()), 
                                            len(df2),
                                            p = np.array(list(SPENDER_PROFILE_PROBS.values())))
    #print(f"Pocket Money Before: {len(df2)}")
    df2 = pd.concat([df2, df_rest])
    #print(f"Pocket Money After: {len(df2)}")

    return df2

def handle_part_time(df):
    df2 = df.copy()
    career_crit = df2["career"] == "Pocket Money"
    age_crit = df2["age"] >= PART_TIME_JOB_MIN_AGE
    combined_crit = career_crit & age_crit
    if combined_crit.sum() == 0:
        return df2
    
    df_rest = df2[~combined_crit]
    df2 = df2[combined_crit]

    ### generate probability for part time job given combined_crit.sum() population
    part_time_job_prob = np.random.rand(combined_crit.sum())
    part_time_job_crit = part_time_job_prob > PART_TIME_JOB_PROB
    df2["career"] = np.where(part_time_job_crit, "Part Time", "Pocket Money")
    ### generate income for part time job
    base_income = INITIAL_INCOME_RANGES['Part Time'][0]
    std_deviation = INITIAL_INCOME_RANGES['Part Time'][1]
    part_time_income = np.abs(np.round(np.random.normal(base_income, std_deviation, combined_crit.sum()),2))
    df2["income"] = np.where(part_time_job_crit, part_time_income, df2["income"])
    df2 = pd.concat([df2, df_rest])
    return df2

def handle_fut_career(df):
    ### use define_study_and_fut_career
    df2 = df.copy()

    ### select people who are young adults with no career
    age_crit = df2["age"].astype(int) == AGE_RANGES["Young Adult"][0]

    ### remove people who are already working
    valid_careers = ['Base', 'Medium', 'High', 'Very High']
    future_is_none = ~df2['future_career'].isin(valid_careers)
    combined_crit = age_crit & future_is_none
    valid_pop = combined_crit.sum()
    if valid_pop == 0:
        return df2
    else:
        #print(f"Valid population for future career: {valid_pop}")
        pass
    
    df_rest = df2[~combined_crit].copy()
    df2_fut_career = df2[combined_crit].copy()

    future_career = np.random.choice( list(FUTURE_CAREER_PAY_PROBS.keys()), valid_pop,
                                        p=np.array(list(FUTURE_CAREER_PAY_PROBS.values())))

    df2_fut_career["future_career"] = future_career
    df2_fut_career['years_of_study'] = 0
    ### use  YEARS_OF_STUDY[future_career] as a merge operation where YEarS_OF_STUDY is a dict
    df2_fut_career = df2_fut_career.merge(pd.DataFrame(list(YEARS_OF_STUDY.items()), 
                                 columns=["future_career", "years_to_study"]),
                                 on="future_career", how="left")
    ### drop years_to_study_x and rename years_to_study_y to years_to_study
    df2_fut_career.drop(columns=["years_to_study_x"], inplace=True)
    df2_fut_career.rename(columns={"years_to_study_y":"years_to_study"}, inplace=True)

    if len(df_rest) == 0:
        df2 = df2_fut_career.copy()
    else:
        df2 = pd.concat([df2_fut_career, df_rest])

    return df2

def update_years_of_study(df):
    df2 = df.copy()

    # Split the dataframe into two parts
    criteria = df2["years_to_study"] > 0
    if criteria.sum() == 0:
        return df2
    
    will_update_years = df2[criteria]
    will_not_update_years = df2[~criteria]

    # Update the years_to_study and years_of_study for the relevant part
    will_update_years["years_to_study"] -= 1
    will_update_years["years_of_study"] += 1

    # Merge the two parts back together
    updated_df = pd.concat([will_update_years, will_not_update_years])

    return updated_df

def handle_finished_studies(df, debug_print=False):
    df2 = df.copy()

    # Criteria for finished studies
    years_of_study_crit = df2['years_to_study'] == 0

    # Criteria for having a valid future career and not currently working
    has_car_crit = df2['future_career'].isin(['Base', 'Medium', 'High', 'Very High'])
    not_working = ~df2['career'].isin(['Base', 'Medium', 'High', 'Very High'])

    # Combined criteria for updating
    combined_crit = years_of_study_crit & has_car_crit & not_working

    if combined_crit.sum() == 0:
        return df2

    # Split dataframe into two parts based on the combined criteria
    df_first_income = df2[combined_crit].copy()
    df_rest = df2[~combined_crit].copy()

    # Update careers and set future_career to None where appropriate
    df_first_income['career'] = df_first_income['future_career']
    df_first_income['future_career'] = None

    # Calculate initial income based on INITIAL_INCOME_RANGES
    base_val  = df_first_income["career"].apply(lambda x: INITIAL_INCOME_RANGES[x][0]).values
    std_val = df_first_income["career"].apply(lambda x: INITIAL_INCOME_RANGES[x][1]).values

    random_inc_values = np.random.normal(base_val, std_val, len(df_first_income))
    random_inc_values = np.abs(np.round(random_inc_values, 2))
    df_first_income["income"] = random_inc_values

    # Add "Finished Studies" to the event string
    df_first_income["event"] = df_first_income["event"] + " - Finished Studies"

    # Debug printing if enabled
    if debug_print:
        print(f"Finished studies: {combined_crit.sum()}")

    # Merge the updated dataframes back together
    updated_df = pd.concat([df_first_income, df_rest])

    return updated_df

def define_partner_type(df):
    df2 = df.copy()
    ### age must be greater than marriage age
    age_crit = df2["age"] >= MIN_MARRIAGE_ALLOWED_AGE
    partner_type_crit = (df2["partner_type"].isna()) | (df2["partner_type"].astype(str) == "nan")
    combined_crit = age_crit & partner_type_crit
    if combined_crit.sum() == 0:
        return df2
    df_other = df2[~combined_crit]
    df_partner = df2[combined_crit]

    ### use np.random.choice to select partner type
    df_partner["partner_type"] = np.random.choice(list(SEXUAL_ORIENTATION_RATES.keys()), 
                                        combined_crit.sum(),
                                         p=np.array(list(SEXUAL_ORIENTATION_RATES.values())))
    
    df2 = pd.concat([df_partner, df_other])
    return df2

def handle_marriage_array(df):
    df2 = df.copy()
    age_crit = df2["age"] >= MIN_MARRIAGE_ALLOWED_AGE
    married_crit = df2["marriage_status"] == False
    can_marry_crit = age_crit & married_crit

    if can_marry_crit.sum() == 0:
        return df2
    df_can = df2[can_marry_crit]
    df_cannot_mar = df2[~can_marry_crit]

    ### add 
    df_can["marriage_thresh"] = df_can.apply(lambda x: CAREERS_AND_MARRIAGE_PROBS[x["career"]], axis=1)
    df_can["marriage_prob"] = np.random.rand(can_marry_crit.sum())
    will_marry_status = np.where(df_can["marriage_prob"] < df_can["marriage_thresh"], True, False)
    #print(f"Potential Marriages: {will_marry_status.sum()}")
    will_marry_df = df_can[will_marry_status]
    will_not_marry_df = df_can[~will_marry_status]

    pairs = get_marriage_pairs(will_marry_df)
    
    ### rename unique_id_1 to unique_name_id
    ### merge pairs with will_marry_df
    ### replace 'spouse_name_id' with 'unique_id_2' when spouse_name_id is None
    
    ### rename unique_id_2 to unique_name_id
    ### merge pairs with will_marry_df
    ### replace 'spouse_name_id' with 'unique_id_1' when spouse_name_id is None
    pairsA = pairs.rename(columns={"unique_id_1":"unique_name_id"})
    will_marry_df_A = pairsA.merge(will_marry_df, on="unique_name_id", how="left")
    cond = will_marry_df_A["spouse_name_id"].isna() | (will_marry_df_A["spouse_name_id"] == "None")
    will_marry_df_A["spouse_name_id"] = np.where(cond, will_marry_df_A["unique_id_2"], will_marry_df_A["spouse_name_id"])
    will_marry_df_A["marriage_status"] = np.where(cond, True, will_marry_df_A["marriage_status"])
    will_marry_df_A.drop(columns=["unique_id_2"], inplace=True)

    pairsB = pairs.rename(columns={"unique_id_2":"unique_name_id"})
    will_marry_df_B = pairsB.merge(will_marry_df, on="unique_name_id", how="left")
    cond = will_marry_df_B["spouse_name_id"].isna() | (will_marry_df_B["spouse_name_id"] == "None")
    will_marry_df_B["spouse_name_id"] = np.where(cond, will_marry_df_B["unique_id_1"], will_marry_df_B["spouse_name_id"])
    will_marry_df_B["marriage_status"] = np.where(cond, True, will_marry_df_B["marriage_status"])
    will_marry_df_B.drop(columns=["unique_id_1"], inplace=True)

    ### check those in will_marry_df that are not in pairs
    unique_id_with_pairs = pd.concat([pairsA["unique_name_id"], pairsB["unique_name_id"]])

    will_marry_df = pd.concat([will_marry_df_A, will_marry_df_B]).drop_duplicates(subset=["unique_name_id"])

    will_marry_df = calculate_marriage_cost(will_marry_df)
            
    not_paired_mask = ~will_marry_df["unique_name_id"].isin(unique_id_with_pairs)
    not_paired_df = will_marry_df[not_paired_mask]
    #print(f"Will Marry: {len(will_marry_df)}")
    #print(f"Not Paired: {len(not_paired_df)}")

    df2 = pd.concat([will_marry_df, will_not_marry_df, not_paired_df, df_cannot_mar]).\
            drop_duplicates(subset=["unique_name_id"])

    return df2



