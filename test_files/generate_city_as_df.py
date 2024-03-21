#%%
### import modules
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#%%
import pandas as pd
import numpy as np
from modules.city import City
from modules.person import Person_Life
from modules.gml_constants import *
import warnings
import matplotlib.pyplot as plt
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

# file_path = "C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/batch/test_city_40000_init_pop_100_years_1950_start_year_2024_03_15_batch_merged.csv"
# data = pd.read_csv(file_path,low_memory=False)

# data2 = data[data['year'] == data["year"].max()].copy()

# %%
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

def remove_dead_people(df):
    df2 = df.copy()
    try:
        is_dead_mask = df2['event'].str.contains("Death")
        death_count = is_dead_mask.sum()
        if death_count > 0:
            print("Dead people", is_dead_mask.sum())
        df2 = df2[~is_dead_mask]
        dfd = df2[is_dead_mask]
    except:
        if len(df2) == 0:
            print("No people in dataframe")
            dfd = pd.DataFrame()
        dfd = pd.DataFrame()
    return df2, dfd

def age_up_df(df):
    df2 = df.copy()

    df2['age'] = df2['age'] + 1
    df2['year'] = df2['year'] + 1
    ### drop old age_range column
    try:
        df2.drop(columns=['age_range','age_event'], inplace=True)
    except:
        pass

    df2 = df2.merge(AGE_RANGE_DF, on='age', how='left')
    ### if age is 0 keep event as born else replace with age_event
    df2['event'] = np.where(df2['age'] == 0, "Born", df2['age_event'])

    return df2

def generate_past_events(df):
    """
    Generate past events for initial population
    """
    df_past = df.copy()
    ### drop columns that are not needed
    to_drop = ['first_name', 'last_name', 'full_name']
    df_past.drop(columns=to_drop, inplace=True)

    ### calculate year of birth
    df_past["year"] = df_past["year"] - df_past["age"]
    df_past["event"] = "Born"
    df_past["age"] = 0

    ### current year - create event
    max_year = df["year"].max()
    
    ### birth_year
    dfs = []
    #print(df_past["year"].unique())
    for birth_year in df_past["year"].unique():
        dfs_temp = []
        ### count how many age up events to generate
        age_up_count = max_year - birth_year
        #print(age_up_count)
        for i in range(age_up_count):
            if i == 0:
                df_temp = df_past[df_past["year"] == birth_year].copy()
            else:
                df_temp = dfs_temp[-1].copy()
            df_temp = complete_year_age_up_pipeline(df_temp)
            dfs_temp.append(df_temp)
            dfs.append(df_temp)
    df_past2 = pd.concat(dfs)
    df_past_final = pd.concat([df_past, df_past2])
    return df_past_final

def calculate_death_df(df):
    df2 = df.copy()
    ### remove dead people

    df2['age_death_thresh'] = df2.apply(
            lambda x: Person_Life.calculate_death_chance_v2(x['age'], x['gender']), axis=1)
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
    
    ### count Males and get index
    gd = df['gender'] == "Male"
    ### generate unique male names using numpy
    df.loc[gd, "first_name"] = np.random.choice(MALE_FIRST_NAMES,gd.sum())
    print("male names",gd.sum())              
    df.loc[~gd, "first_name"] = np.random.choice(FEMALE_FIRST_NAMES,len(gd) - gd.sum())
    print("female names",len(gd) - gd.sum())
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
    df['future_career'] = None
    df['income'] = 0
    df['balance'] = 0
    df['spender_prof'] = None

    return df

def generate_fut_career(df):
    ### use Person_Life and define_study_and_fut_career
    df2 = df.copy()

    ### remove people that are not old enough to work
    age_crit = df2["age"].astype(int) < AGE_RANGES["Young Adult"][0]

    ### remove people who are already working
    working_crit = df2["career"].isin(CAREERS_AND_MARRIAGE_PROBS.keys())

    combined_crit = ~age_crit & ~working_crit
    if combined_crit.sum() == 0:
        return df2

    df2 = df2[combined_crit]
    df_rest = df2[~combined_crit]

    alive_pop = len(df2)
    future_career = np.random.choice( list(FUTURE_CAREER_PAY_PROBS.keys()), alive_pop,
                                        p=np.array(list(FUTURE_CAREER_PAY_PROBS.values())))
    df2["future_career"] = future_career
    df2["career"] = None
    df2['years_of_study'] = 0
    ### use  YEARS_OF_STUDY[future_career] as a merge operation where YEarS_OF_STUDY is a dict
    df2 = df2.merge(pd.DataFrame(list(YEARS_OF_STUDY.items()), 
                                 columns=["future_career", "years_of_study"]),
                                 on="future_career", how="left")
    ### append dead people and rest of the population
    df2 = pd.concat([df2, df_rest])
    return df2

def update_years_of_study(df):
    df2 = df.copy()
    ### get people who are studying
    try:
        study_crit = df2["years_of_study"] > 0
        df2.loc[study_crit, "years_of_study"] -= 1
        df2.loc[~study_crit, "years_of_study"] += 1
    except:
        print("No eligible people in dataframe")
    return df2

def handle_finished_studies(df):
    df2 = df.copy()
    ### check if future_career is None or nan
    nan_or_none = (df2['future_career'] == None) | (df2['future_career'].astype(str) == "nan")
    ### years of study is 0
    years_of_study_crit = df2['years_of_study'] == 0
    ### check if career is Pocket Money or Part Time
    pocket_or_part = df2['career'].isin(["Pocket Money", "Part Time"])
    combined_crit = nan_or_none & pocket_or_part & years_of_study_crit
    if combined_crit.sum() == 0:
        return df2
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

def complete_year_age_up_pipeline(df):

    df2 = df[df['year'] == df["year"].max()].copy()
    ### remove dead people
    df2, dfd = remove_dead_people(df2)

    df2 = age_up_df(df2)
    df2 = calculate_death_df(df2)
    df2 = handle_pocket_money(df2)
    #df2 = handle_spender_profile(df2)
    ### remove newly dead people
    #df2, dfd2 = remove_dead_people(df2)
    df2 = generate_fut_career(df2)
    df2 = update_years_of_study(df2)
    df2 = handle_finished_studies(df2)
    df2 = update_account_balance(df2)

    ### append dead people
    df2 = pd.concat([df2, dfd])

    return df2

def complete_city(years, age_range="Young Adult", population=40000, start_year=1950):
    df = time_function(generate_init_df, population, start_year, age_range)
    df_past = time_function(generate_past_events, df)
    df2 = df_past.copy()
    dfs = []
    for _ in range(years):
        df2 = time_function(complete_year_age_up_pipeline, df2)
        dfs.append(df2)

    dfs_p1 = pd.concat(dfs)
    dfs_final = pd.concat([df_past, dfs_p1])

    return dfs_final

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
#%% test complete_city function
df3 = time_function(complete_city, 100, "Young Adult", 40000, 1950)
#%% check if folder exists
if not os.path.exists("C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/new_pipeline"):
    os.makedirs("C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/new_pipeline")
    
df3.to_csv("C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/new_pipeline/complete_city_test.csv", index=False)

#%%
population_histogram(df3)

death_count_by_age(df3)
# %%
### handle marriage

def generate_marriage(df):
    df2 = df.copy()
    ### remove dead people
    df2, dfd = remove_dead_people(df2)

    ### remove people who are already married or ["Baby", "Child", "Teenager"]
    age_crit = df2["age_range"].isin(["Baby", "Child", "Teenager"])
    married_crit = df2["marriage_status"] == True
    df2 = df2[~age_crit & ~married_crit]



    ### create marriage dataframe
#%%
import pandas as pd
import numpy as np
from modules.gml_constants import *
def calculate_death_chance_2(age,gender):
    if gender == "Male":
        gender_val =  0
    elif gender == "Female":
        gender_val = 1
    else:
        gender_val = gender

    pred_lin = 1 - DEATH_PROB_MODEL_COEF['lin_reg']['age']*age*0.75 +\
            DEATH_PROB_MODEL_COEF['lin_reg']['gender']*gender_val +\
            DEATH_PROB_MODEL_COEF['lin_reg']['intercept']+0.2/100

    pred_log2 = DEATH_PROB_MODEL_COEF['lin_reg_log']['age']*age +\
                DEATH_PROB_MODEL_COEF['lin_reg_log']['gender']*gender_val +\
                DEATH_PROB_MODEL_COEF['lin_reg_log']['lin_pred']*pred_lin +\
                DEATH_PROB_MODEL_COEF['lin_reg']['intercept']

    pred_log2_final = 1 - np.power(2,pred_log2)


    if age > 55:
        output = 1-pred_log2_final
    else:
        output = 1-pred_lin

    return 1-pred_lin, 1-pred_log2_final, output

### create a table with age and gender combinations
age_df = pd.DataFrame(np.arange(0,101), columns=["age"])
age_df_a = age_df.copy()
age_df_a["gender"] = 'Male'
age_df_b = age_df.copy()
age_df_b["gender"] = 'Female'
age_df_c = pd.concat([age_df_a, age_df_b])
age_df_c["pack"] = age_df_c.apply(
    lambda x: calculate_death_chance_2(x["age"],x['gender']), axis=1)

age_df_c['deatch_chance_lin_reg'] = age_df_c["pack"].astype(str).str.split(",", expand=True)[0].str.replace("(","")
age_df_c['deatch_chance_lin_reg_log'] = age_df_c["pack"].astype(str).str.split(",", expand=True)[1]
age_df_c['deatch_chance_final'] = age_df_c["pack"].astype(str).str.split(",", expand=True)[2].str.replace(")","")
age_df_c
age_df_c.to_csv("C:/Users/ricar/Documents/GitHub/TGoL/test_files/data/new_pipeline/death_chance.csv", index=False)

    # %%
