#%%
### import modules
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from modules.city import City
from modules.person import Person_Life
from modules.gml_constants import *
import warnings
import matplotlib.pyplot as plt
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
import tqdm

### Generic and Test functions
### create a function that measures the time it takes to run the function
import time
def time_function(func, *args):
    start = time.time()
    result = func(*args)
    end = time.time()
    ### round to 5 decimal places
    delta = round(end-start, 5)
    print(f"Function {func.__name__} took {delta} seconds to run")
    return result

def check_merge_duplication_columns_error_message(df):
    
    df2 = df.copy()
    ### if columns ends with _x or _y, then remove them
    cols = []
    for col in df2.columns: 
        if col.endswith("_x") or col.endswith("_y"):
            cols.append(col)
    if len(cols) == 0:
        return ""
    else:
        print("Checking merge duplication columns")
        print(df2.head())
        return f"Columns to remove: {cols}"

def solve_merge_duplication_columns(df,cols):
    ### assume that the columns are in the format column_x and column_y
    ### _x seems to be the original column and _y seems to be the new column
    ### drop the _x column and rename the _y column to the original column
    df2 = df.copy()
    for col in cols:
        if col.endswith("_x"):
            original_col = col.replace("_x", "")
            print(f"Original column: {original_col}")
            df[original_col] = df2[original_col + "_y"]
            df2.drop(columns=[original_col+"_x", original_col+"_y"], inplace=True)
    return df2

def check_function_for_duplication(func, *args):
    df = func(*args)
    #df2 = check_merge_duplication_columns(df)
    error = check_merge_duplication_columns_error_message(df)
    ### print function name
    if error != "":
        print(func.__name__, error)
        cols = error.split(": ")[1].replace("[","").replace("]","").replace("'","").split(", ")
        df = solve_merge_duplication_columns(df, cols)

    return df

### use assert to raise an error if the condition is not met
def check_unique_id(df):
    print("Checking unique_name_id")
    unique_count = len(df["unique_name_id"].unique())
    total_count = len(df)
    unique_text = f"Unique count: {unique_count}"
    total_text = f"Total count: {total_count}"
    assert len(df["unique_name_id"].unique()) == len(df), f"{unique_text}, {total_text}"

def check_max_year(df,population=40000):
    print("Checking max year")
    max_year = df["year"].max()
    print(f"Max year: {max_year}")
    assert len(df[df["year"] == max_year]) == population, f"Max year: {max_year}"

### Generate Functions
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
    df["career"] = None
    df['years_of_study'] = None
    df['years_to_study'] = None
    df['future_career'] = None
    df['income'] = 0
    df['balance'] = 0
    df['spender_prof'] = None
    df['partner_type'] = None
    return df

def generate_past_events(df):
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
                df_temp = dfs_temp[-1].copy()

            df_temp = generate_complete_year_age_up_pipeline(df_temp)

            dfs_temp.append(df_temp)
            dfs.append(df_temp)
    df_past2 = pd.concat(dfs)

    df_past_final = pd.concat([df_past, df_past2])

    return df_past_final

def generate_complete_year_age_up_pipeline(df):
    
    mask = df['year'] == df["year"].max()
    if mask.sum() == 0:
        #print("No people in that year")
        return df
    #print(len(df), mask.sum())

    df2 = df[mask].copy()
    ### remove dead people
    
    df2, dfd = remove_dead_people(df2)

    df2 = check_function_for_duplication(age_up_df, df2)
    ### check if age is a number and not nan
    #print(df2['age'].isna().sum())
    df2 = check_function_for_duplication(calculate_death_df, df2)
    df2 = check_function_for_duplication(handle_pocket_money, df2)
    #df2 = handle_spender_profile(df2)
    ### remove newly dead people
    #df2, dfd2 = remove_dead_people(df2)
    df2 = check_function_for_duplication(handle_fut_career, df2)
    df2 = check_function_for_duplication(update_years_of_study, df2)
    df2 = check_function_for_duplication(handle_finished_studies, df2)
    df2 = check_function_for_duplication(handle_part_time, df2)
    df2 = check_function_for_duplication(define_partner_type, df2)
    df2 = check_function_for_duplication(handle_marriage_new, df2)

    df2 = check_function_for_duplication(update_account_balance, df2)

    df2 = pd.concat([df2, dfd])

    return df2

def generate_complete_city(years, age_range="Young Adult", population=40000, start_year=1950):
    df = time_function(generate_init_df, population, start_year, age_range)
    df = time_function(generate_names_and_initial_data, df, population)
    df_past = time_function(generate_past_events, df)
    df2 = df_past.copy()
    dfs = []
    for _ in tqdm.tqdm(range(years)):
        df2 = generate_complete_year_age_up_pipeline(df2) 
        dfs.append(df2)

    dfs_p1 = pd.concat(dfs)
    dfs_final = pd.concat([df_past, dfs_p1])

    return dfs_final

### Event Functions

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
    df2 = df2[age_crit]
    df_rest = df2[~age_crit]

    df2["career"] = "Pocket Money"
    base_income = INITIAL_INCOME_RANGES['Pocket Money'][0]
    std_deviation = INITIAL_INCOME_RANGES['Pocket Money'][1]
    pocket_money = np.abs(np.round(np.random.normal(base_income, std_deviation,len(df2)),2))
    df2["income"] = pocket_money

    ### append dead people and rest of the population
    df2["spender_prof"] = np.random.choice( list(SPENDER_PROFILE_PROBS.keys()), 
                                            len(df2),
                                            p = np.array(list(SPENDER_PROFILE_PROBS.values())))
    df2 = pd.concat([df2, df_rest])

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
    #working_crit = df2["career"].isin(CAREERS_AND_MARRIAGE_PROBS.keys())
    working_crit = df2["career"].isin(valid_careers)
    combined_crit = age_crit & ~working_crit
    valid_pop = combined_crit.sum()


    rest_pop = (~combined_crit).sum()
    if valid_pop == 0:
        return df2
    else:
        #print(f"Valid population for future career: {valid_pop}")
        pass
    
    df2 = df2[combined_crit]
    df_rest = df2[~combined_crit]

    future_career = np.random.choice( list(FUTURE_CAREER_PAY_PROBS.keys()), valid_pop,
                                        p=np.array(list(FUTURE_CAREER_PAY_PROBS.values())))
    df2["future_career"] = future_career
    df2["career"] = None
    df2['years_of_study'] = 0
    ### use  YEARS_OF_STUDY[future_career] as a merge operation where YEarS_OF_STUDY is a dict
    df2 = df2.merge(pd.DataFrame(list(YEARS_OF_STUDY.items()), 
                                 columns=["future_career", "years_to_study"]),
                                 on="future_career", how="left")
    ### drop years_to_study_x and rename years_to_study_y to years_to_study
    df2.drop(columns=["years_to_study_x"], inplace=True)
    df2.rename(columns={"years_to_study_y":"years_to_study"}, inplace=True)

    ### append dead people and rest of the population
    if rest_pop > 0:
        df2 = pd.concat([df2, df_rest])

    return df2

def update_years_of_study(df):
    df2 = df.copy()
    

    ### check if years_to_study exists else print error message
    if "years_to_study" not in df2.columns:
        print("years_to_study not in columns")
        return df2

    study_crit = df2["years_to_study"] > 0
    if study_crit.sum() == 0:
        return df2
    else: 
        df2.loc[study_crit, "years_to_study"] -= 1
        df2.loc[study_crit, "years_of_study"] += 1

    return df2

def handle_finished_studies(df):
    df2 = df.copy()
    ### check if future_career is None or nan
    nan_or_none = ~(df2['future_career'] == None) | (df2['future_career'].astype(str) == "nan")
    ### years of study is 0
    years_of_study_crit = df2['years_to_study'] == 0
    ### check if career is Pocket Money or Part Time
    pocket_or_part = df2['career'].isin(["Pocket Money", "Part Time"])
    combined_crit = nan_or_none & pocket_or_part & years_of_study_crit
    if combined_crit.sum() == 0:
        return df2
    else:
        print(f"Finished studies: {combined_crit.sum()}")
        pass
    df2.loc[combined_crit, 'career'] = df2.loc[combined_crit, 'future_career']
    df2.loc[~combined_crit, 'future_career'] = None
    df_first_income = df2[combined_crit]
    df_rest = df2[~combined_crit]
    ### generate new income - use apply and lambda
    df_first_income["income"] = df_first_income.apply(
        lambda x: abs(np.random.normal(FUTURE_CAREER_PAY_PROBS[x["career"]][0],
                                        FUTURE_CAREER_PAY_PROBS[x["career"]][1])))
    
    ### Add Finished Studies to event string
    df_first_income["event"] = df_first_income["event"] + " - Finished Studies"
    ### append dataframes
    
    df2 = pd.concat([df_first_income, df_rest])
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

def define_partner_type(df):
    df2 = df.copy()
    ### age must be greater than marriage age
    age_crit = df2["age"] >= MIN_MARRIAGE_ALLOWED_AGE
    partner_type_crit = (df2["partner_type"] == None) | (df2["partner_type"].astype(str) == "nan")
    combined_crit = age_crit & partner_type_crit
    if combined_crit.sum() == 0:
        return df2
    df_other = df2[~combined_crit]
    ### use np.random.choice to select partner type
    df2["partner_type"] = np.random.choice(SEXUAL_ORIENTATION_RATES.keys(), 
                                            combined_crit.sum(),
                                            p=np.array(list(SEXUAL_ORIENTATION_RATES.values())))
    df2 = pd.concat([df2, df_other])
    return df2

def generate_spouses():
    pass

def handle_marriage(self, person):
    # retrieve the last history of the person and:
    person_last_history = person.history_df.iloc[-1].copy()
    if person_last_history['age_range'] not in ["Baby", "Child", "Teenager"]:
        
        if person_last_history['career'] is None:
            return None
        ### check current employment status to retrieve the marriage probability
        career_crit_chance = CAREERS_AND_MARRIAGE_PROBS[person_last_history['career']] ### test for all careers later - to be developed
        
        ### check if the person is old enough to get married and is not married
        age_cri = person_last_history["age"] >= MIN_MARRIAGE_ALLOWED_AGE
        married_cri = person_last_history["married"] == False
        prob_cri = np.random.random() < career_crit_chance

        ### FOR TESTING MARRIAGE
        prob_cri = True

        ### Based on the career of the person, check if the person will get married
        can_marry_cri = age_cri and married_cri and prob_cri

        if can_marry_cri:
            # 1st - get the gender of the person to be married & check what will be gender of the spouse
            person_gender =  person_last_history['gender']
            if person_gender == "Male":
                spouse_gender = 'Female' if np.random.random() < (1 - SAME_GENDER_MARRIAGE_RATIO) else 'Male'
            else:
                spouse_gender = 'Male' if np.random.random() < (1 - SAME_GENDER_MARRIAGE_RATIO) else 'Female'
            # 2nd - check if exist spouse candidate in the city:`
            person_age = person_last_history['age']
            person_most_recent_year = person_last_history['year']
            all_population = self.history.copy()
            # - is not married and; 
            # - is not the person itself in the city and;
            # - is within +- 5 years of the person age and;
            # - has the gender defined for the spouse and;
            # - has the age to get married
            # - must be the information on the same year as the person
            is_married = all_population['married'] == False
            is_not_person = all_population['unique_name_id'] != person_last_history['unique_name_id']
            is_age_range = (all_population['age'] >= person_age - 5) & (all_population['age'] <= person_age + 5)
            is_gender = all_population['gender'] == spouse_gender
            is_age_to_get_married = all_population['age'] >= MIN_MARRIAGE_ALLOWED_AGE
            is_same_year = all_population['year'] == person_most_recent_year
            marriage_criteria = is_married & is_not_person & is_age_range & is_gender & is_age_to_get_married & is_same_year

            does_not_have_the_same_parentsA = all_population['parent_name_id_A'] != person_last_history['parent_name_id_A']
            does_not_have_the_same_parentsB = all_population['parent_name_id_B'] != person_last_history['parent_name_id_B']
            marriage_criteria = marriage_criteria & does_not_have_the_same_parentsA & does_not_have_the_same_parentsB

            eligible_people_crit_within_city = marriage_criteria.sum() > 0

            if eligible_people_crit_within_city:
                # retrieve the spouse candidate from the city
                spouse_id = all_population[marriage_criteria].sample(1).iloc[0].copy()['unique_name_id'] ### select on from the list

                spouse = self.people_obj_dict[spouse_id]
                spouse_last_history = spouse.history_df.iloc[-1].copy()
                #Retrieve the person history
                person_last_history = person.history_df.iloc[-1].copy()

                ### quick error check to see if the last history is the same year as the person - else solve the issue
                if spouse_last_history['year'] != person_last_history['year']:
                    logger.debug(f"Solve the issue \n\
                                    - Last history of the spouse candidate -\
                                    is not the same year as the person which means there is a problem with the current logic -\n\
                                    {spouse_last_history['year']} -\n\
                                    {person_last_history['year']} -\n\
                                    {person_last_history['unique_name_id']}")
                    pass

                ###Update the spouse and person values so they are married

                # - change the married status to True
                spouse_last_history['married'] = True
                # - change the just_married status to True
                spouse_last_history['just_married'] = True
                # - change the spouse_name_id to the person unique_name_id
                spouse_last_history['spouse_name_id'] = person_last_history['unique_name_id']
                # the person last history:

                # - change the spouse_name_id to the spouse unique_name_id
                last_index = person.history_df.index[-1]
                person.history_df.loc[last_index, 'spouse_name_id'] = spouse_last_history['unique_name_id']


                # update the history of the person and the spouse candidate
                
                person_last_history['married'] = True
                person_last_history['just_married'] = True
                person_last_history['spouse_name_id'] = spouse_last_history['unique_name_id']

                ###Update the actual dataframes
                person.history_df.iloc[-1] = person_last_history
                spouse.history_df.iloc[-1] = spouse_last_history

                # update the object status
                person.married = True
                person.just_married = True
                self.people_obj_dict[spouse.unique_name_id] = spouse
                
                #person.update_history(new_history=person_last_history) 
                #### FUTURE ISSUES TO SOLVE:
                # - IF THE PERSON CURRENT YEAR WAS NOT UPDATED YET SO THE PERSON WILL NOT BE A CANIDATE FOR MARRIAGE
                # - UPDATE HISTORY ISSUE - A SPOUSE CANDIDATE HAS THE CURRENT HISTORY APPENDED TO THE PERSON HISTORY AND CITY HISTORY BUT THEY SHOULD BE UPDATED IN BOTH

            else:
                # if there is no spouse candidate, then create a new person and get married
                # get a random age between the minimum age to get married and the maximum age to get married 
                # get the age range based on the age
                # create a new person with the age range and the current year

                if person_age - 5 < MIN_MARRIAGE_ALLOWED_AGE:
                    spouse_min_age = MIN_MARRIAGE_ALLOWED_AGE
                else:
                    spouse_min_age = person_age - 5
                
                ### Stage 1 - select the age of the spouse
                spouse_age = np.random.randint(spouse_min_age, person_age + 5)

                ### Stage 2 - get age range based on the age
                spouse_age_range = Person_Life.update_age_range(spouse_age) ### TO BE DEVELOPED - SKIP AGE RANGE TO REPLACE WITH THE AGE WHEN CREATING A NEW PERSON

                ### Stage 3 - create a new person with the age range and the current year
                spouse = Person_Life(gender= spouse_gender, age_range= spouse_age_range, current_year= person_most_recent_year, married = True)

                ### Stage 4 - generate the past events of the new spouse
                spouse.generate_past_events()

                ### Stage 5 - update the history of the spouse
                ### married to true will be applied to all the history of the person so it need to be removed from the history later
                spouse_all_history = spouse.history_df.copy()
                criteria_arange = spouse_all_history["age_range"] == spouse_age_range
                criteria_age = spouse_all_history["age"] == spouse_age
                criteria_year = spouse_all_history["year"] == person_most_recent_year

                marriage_status_crit = criteria_arange & criteria_age & criteria_year


                spouse_all_history.loc[~marriage_status_crit,"married"] = False
                spouse_all_history.loc[marriage_status_crit,"just_married"] = True
                spouse_all_history.loc[marriage_status_crit,"married"] = True
                spouse_all_history.loc[marriage_status_crit,"spouse_name_id"] = person_last_history['unique_name_id']
                spouse.history_df = spouse_all_history


                ###Grabs the histories we need
                spouse_last_history = spouse.history_df.iloc[-1].copy()
                person_last_history = person.history_df.iloc[-1].copy()

                ###Updates everything for the person getting married to the spouse
                person_last_history['married'] = True
                person_last_history["just_married"] = True
                person_last_history["spouse_name_id"] = spouse.unique_name_id
                person.history_df.iloc[-1] = person_last_history

                ###Updates the values of the acutal object
                person.married = True
                person.just_married = True
                self.people_obj_dict[spouse.unique_name_id] = spouse
                ### append the spouse to the city history
                self.history = pd.concat([self.history, spouse.history_df])

            ### TO BE DEVELOPED ###
            # # check if the person has enough money to get married    
            # _, marriage_expense = self.calculate_marriage_cost() ### to be developed
            # total_balance = person_last_history['balance'] + spouse_last_history['balance']
            # ### if the person does not have enough money, then check both person and spouse candidate can get a loan
            # if total_balance < marriage_expense:
            #     get_loan_status = self.get_loan(desired_loan_amount=marriage_expense-total_balance)
            #     if  get_loan_status is None:
            #         print('You cannot afford the marriage expense. You have reached the maximum loan amount.')
            return spouse
        else:
            return None
    else:
        return None

# %%
### handle marriage

def check_candidate_spouse(eligible_df, will_marry_id):
    ### get partner type, gender, age, year, unique_name_id
    candidate = eligible_df[eligible_df["unique_name_id"] == will_marry_id].copy()
    partner_type = candidate["partner_type"].iloc[0]
    gender = candidate['gender'].iloc[0]
    age = candidate['age'].iloc[0]
    year = candidate['year'].iloc[0]
    parent_name_id_A = candidate['parent_name_id_A'].iloc[0]
    parent_name_id_B = candidate['parent_name_id_B'].iloc[0]

    ### criteria for spouse
    age_crit = (eligible_df["age"] >= age - 5) & (eligible_df["age"] <= age + 5)
    year_crit = eligible_df["year"] == year
    parent_critA = eligible_df["parent_name_id_A"] != parent_name_id_A
    parent_critB = eligible_df["parent_name_id_B"] != parent_name_id_B
    orient_crit = eligible_df["partner_type"] == partner_type

    ### specific criteria for spouse
    if partner_type == "Heterosexual" :
        if gender == "Male":
            spouse_gender = 'Female'
            spouse_gender_crit = eligible_df["gender"] == spouse_gender
        else:
            spouse_gender = 'Male'
            spouse_gender_crit = eligible_df["gender"] == "Male"
        
    elif partner_type == "Gay/Lesbian":
        spouse_gender = gender
        spouse_gender_crit = eligible_df["gender"] == gender

    else:
        spouse_gender = gender
        spouse_gender_crit = (eligible_df["gender"] == gender) | (eligible_df["gender"] != gender)

    spouse_crit = orient_crit & spouse_gender_crit & age_crit & year_crit & parent_critA & parent_critB

    if spouse_crit.sum() > 0:
        id_spouse = eligible_df[spouse_crit].sample(1)["unique_name_id"].iloc[0]
        specs = None
    else:
        id_spouse = None
        specs = {"will_marry_id":will_marry_id,
                 "partner_type":partner_type,
                 "gender":spouse_gender,
                 "age":np.random.randint(age - 5, age + 5),
                 'year':year} 
    return id_spouse, specs

def create_spouse_from_specs(to_create_spouse_specs):
    ### to_create_spouse_specs is a list of dictionaries
    #### where specs = {"will_marry_id":will_marry_id,
    #  "partner_type":partner_type,
    #  "gender":spouse_gender,
    #  "age":np.random.randint(age - 5, age + 5),
    #  'year':year}
    ### transform the list of dictionaries into a dataframe
    df = pd.DataFrame(to_create_spouse_specs)
    
def handle_marriage_new(df):
    df2 = df.copy()
    ### remove people who are already married or are not old enough ["Baby", "Child", "Teenager"]
    age_crit = df2["age"] >= MIN_MARRIAGE_ALLOWED_AGE
    married_crit = df2["marriage_status"] == False
    can_marry_crit = age_crit & married_crit
    if can_marry_crit.sum() == 0:
        return df2

    df2 = df2[can_marry_crit]
    df_rest = df2[~can_marry_crit]
    ### create marriage dataframe

    df2["marriage_thresh"] = df2.apply(lambda x: CAREERS_AND_MARRIAGE_PROBS[x["career"]], 
                                     axis=1)
    df2["marriage_prob"] = np.random.rand(can_marry_crit.sum())
    will_marry_status = np.where(df2["marriage_prob"] < df2["marriage_thresh"], True, False)
    will_marry_df = df2[will_marry_status]
    to_create_spouse_specs = []
    for will_marry_id in will_marry_df["unique_name_id"]:
        id_spouse, specs = check_candidate_spouse(df2, will_marry_id)
        if id_spouse is not None:
            df2.loc[df2["unique_name_id"] == will_marry_id, "marriage_status"] = True
            df2.loc[df2["unique_name_id"] == will_marry_id, "spouse_name_id"] = id_spouse
            df2.loc[df2["unique_name_id"] == id_spouse, "marriage_status"] = True
            df2.loc[df2["unique_name_id"] == id_spouse, "spouse_name_id"] = will_marry_id
        else:
            to_create_spouse.append(specs)
            print(f"No spouse candidate for {specs['will_marry_id']}")


### Plotting Functions

def population_histogram(df):
    df2 = df.copy()
    ### plot polulation count by year
    df3 = df2.groupby("year").size().reset_index(name="count")
    plt.xticks(np.arange(df3["year"].min(), df3["year"].max(), 10))
    min_V = df3["count"].min()
    str_min = str(min_V)
    min_v = int(str_min[0] + "0" * (len(str_min) - 1))

    plt.yticks(np.arange(min_v, df3["count"].max(), 1000))
    plt.xlabel("Year")
    plt.ylabel("Population Count")
    plt.title("Population Count by Year")
    plt.plot(df3["year"], df3["count"])
    plt.show()

def death_count_by_age(df):
    df2 = df.copy()
    df2["death_count"] = np.where(df2["event"].str.contains("Death"), 1, 0)
    ### drop where death count is 0
    df2 = df2[df2["death_count"] > 0]
    df3 = df2.groupby(["age"]).agg({"death_count": "sum"}).reset_index()
    df3["age"] = df3["age"].astype(int)
    plt.figure(figsize=(20,10))
    ### set age as continuous variable and do not show all ages
    ### do not show years as labels
    plt.xticks(np.arange(df3["age"].astype(int).min(), 
                         df3["age"].astype(int).max())+1, 5)
    plt.yticks(np.arange(df3["death_count"].min(), df3["death_count"].max()+1, 50))
    plt.xlabel("Age")
    plt.ylabel("Death Count")
    plt.title("Death Count by Age")
    plt.plot(df3["age"], df3["death_count"])
    plt.show()