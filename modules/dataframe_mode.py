#%%
### import modules
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from modules.marriage import get_marriage_pairs
from modules.born import children_born
from modules.financial_fc import *
from modules.utils import *
from modules.city import City
from modules.person import Person_Life
from modules.gml_constants import *
import warnings
import matplotlib.pyplot as plt
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
import tqdm

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
    ### add marriage status
    df["marriage_status"] = False
    df["career"] = "No Career"
    df['years_of_study'] = None
    df['years_to_study'] = None
    df['future_career'] = None
    df['income'] = 0
    df['balance'] = 0
    df["has_insurance_flag"] = 0
    df['spender_prof'] = None
    df['partner_type'] = None
    df['spouse_name_id'] = None
    df["marriage_thresh"] = 0
    df["marriage_prob"] = 0
    df["existing_children_count"] = 0
    df['parent_name_id_A'] = np.random.choice(MALE_FIRST_NAMES,population)
    df['parent_name_id_A'] += " " + df["last_name"]
    df['parent_name_id_B'] = np.random.choice(FEMALE_FIRST_NAMES,population)
    df['parent_name_id_B'] += " " + df["last_name"]
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
    df2 = check_function_for_duplication(age_up_df, df2)
    df_length["age_up"] = len(df2)
    df2 = check_function_for_duplication(calculate_death_df, df2)
    df_length["death_calc"] = len(df2)
    df2 = check_function_for_duplication(handle_pocket_money, df2)
    df_length["pocket_money"] = len(df2)
    df2 = check_function_for_duplication( handle_fut_career, df2)
    df_length["fut_career"] = len(df2)
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
    #df2 = check_function_for_duplication(update_account_balance, df2)
    df_length["account_balance"] = len(df2)
    df2 = pd.concat([df2, dfd])
    df_length["combined"] = len(df2)
    if basic_mode and debug_print:
        #print(f"Year: {df2['year'].max()} Lengths:\n {df_length}")

        ### print histogram number of children per parent

        # cols = ["parent_name_id_A","existing_children_count"]

        # xx = df2[cols].reset_index().groupby(cols).count().reset_index()
        # ### print histogram number of children per parent
        # xx.hist(column="existing_children_count", bins=10)
        # plt.show()
        pass

    return df2

def generate_complete_city(years, age_range="Young Adult", population=40000, start_year=1950, debug_print=False):
    ### Print the start year
    df = time_function(generate_init_df, population, start_year, age_range)
    df = time_function(generate_names_and_initial_data, df, population)
    ### generate past events
    print("\n ####   Generating past events ####\n")
    df_past = time_function(generate_past_events, df, debug_print)
    df2 = df_past.copy()
    dfs = []
    for year in tqdm.tqdm(range(years)):
        ### generate new year
        df2 = generate_complete_year_age_up_pipeline(df2, basic_mode=True, debug_print=debug_print)
        dfs.append(df2)

    dfs_p1 = pd.concat(dfs)
    dfs_final = pd.concat([df_past, dfs_p1])

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

def calculate_death_df(df):
    df2 = df.copy()
    ### remove people who has age nan
    #df2 = df2[(~df2['age'].isna()) | (df2['age'].str() != "nan")]
    ### remove dead people
    try:
        df2['age_death_thresh'] = df2.apply(
                lambda x: Person_Life.calculate_death_chance_v2(x['age'], x['gender']), axis=1)
    except:
        print(f"{len(df2)} people in dataframe")
        return df2
    ### generate random number to compare with death threshold
    df2["age_death_prob"] = np.random.rand(len(df2))
    ### use calculate_death_chance_crit_ill
    df2['ci_death_thresh'] = df2.apply(
        lambda x: Person_Life.calculate_death_chance_crit_ill(x['age']), axis=1)
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
    ### use Person_Life and define_study_and_fut_career
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
            
    not_paired_mask = ~will_marry_df["unique_name_id"].isin(unique_id_with_pairs)
    not_paired_df = will_marry_df[not_paired_mask]
    #print(f"Will Marry: {len(will_marry_df)}")
    #print(f"Not Paired: {len(not_paired_df)}")

    df2 = pd.concat([will_marry_df, will_not_marry_df, not_paired_df, df_cannot_mar]).\
            drop_duplicates(subset=["unique_name_id"])

    return df2



