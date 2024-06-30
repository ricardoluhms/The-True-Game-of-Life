#%%
### import modules
import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from modules.constants import *
import warnings
import matplotlib.pyplot as plt
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
### Generic and Test functions

########################################### Generic and Test Functions ###########################################
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

def check_population_histogram(df):
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

def check_death_count_by_age(df):
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

def check_career_and_study(df):
    cols = [ "years_to_study", "career", "future_career"]
    print(f"Population {len(df)}")
    check = df[cols].fillna("None").reset_index().groupby(cols).count().reset_index()
    print(f"{check}")
    print("\n","-"*50,"\n")

### this function will read use test a function and check the years_to_study, career, and future_career
def check_career_and_study_func_test(func, df, *args):
    cols = [ "years_to_study", "future_career"] #"age"
    year = df["year"].max()
    gb_count_before = df[cols].reset_index().groupby(cols).count().reset_index()
    df2 = func(df, *args)
    gb_count_after = df2[cols].reset_index().groupby(cols).count().reset_index()

    cols2 = [ "years_to_study", "career"]
    gb_count_before2 = df[cols2].reset_index().groupby(cols2).count().reset_index()
    gb_count_after2 = df2[cols2].reset_index().groupby(cols2).count().reset_index()

    ### dont print if len of count is 0
    if len(gb_count_before) == 0:
        return df2

    print(f"Year {year}")
    print(f"Futur Career Before:\n {gb_count_before}\n"\
          f" Future Career After:\n {gb_count_after}\n")
    print(f"Career Before:\n {gb_count_before2}\n"\
          f" Career After:\n {gb_count_after2}\n")
    return df2
