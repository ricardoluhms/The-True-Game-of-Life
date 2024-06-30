#%%
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
from  modules.gml_constants import ( BABY_TWINS_MODE, BIRTH_PROB_CURVES_CST,
                                     GENDER_PROBS, MALE_FIRST_NAMES, FEMALE_FIRST_NAMES,
                                     generate_initial_constants)
                                     
### ignore warnings 
import warnings
warnings.filterwarnings("ignore")

def children_born(df):

    ### current mode will consider only heterosexual couples duo the complexity of the code for other types

    ### cond person is married
    ### cond person and spouse are old enough
    ### cond spouse and person are alive

    female_cri = df["gender"] == "Female"
    married_cri = df["marriage_status"] == True
    age_cri = df["age"] >= 16
    has_spouse_cri = df["spouse_name_id"].notnull()
    is_candidate = married_cri & age_cri & has_spouse_cri & female_cri
    df_candidates = df[is_candidate].copy()
    df_non_candidates = df[~is_candidate].copy()
    #print("Candidates: ", is_candidate.sum(), "Non Candidates: ", (~is_candidate).sum())


    #print((~is_candidate).sum(), is_candidate.sum())
    if is_candidate.sum() == 0:
        return df
    
    ### use apply and lambda and birth_prob_curves
    age_exist_child_prob = df_candidates.apply(lambda x: birth_prob_curves(x["age"], 
                                                                 x["existing_children_count"]), axis=1)

    ### create a random number between 0 and 1
    children_prob = np.random.random(size=len(df_candidates))
    
    ### total prob starts high and decreases with age and existing children, a low children_prob is better because it will be easier to have a child 
    #### if adults are young and have no children, and total_prob is high
    #### if adults are old and have children, and total_prob is low 
    will_have_child = children_prob <= age_exist_child_prob

    #print("Desc", df_candidates["total_prob"].describe(), crit.sum())
    ### non negative total_prob or children_prob <= total_prob

    df_with_new_children = df_candidates[will_have_child].copy()
    df_with_no_new_children = df_candidates[~will_have_child].copy()

    temp_baby_count = np.random.choice( list(BABY_TWINS_MODE.keys()),
                                       size=len(df_with_new_children),
                                        p=np.array(list(BABY_TWINS_MODE.values())))
    ### if baby_count 
    df_with_new_children["existing_children_count"] += temp_baby_count

    ### get the person and the spouse from the dataframe
    df_babies = df_with_new_children.copy()[["unique_name_id", "spouse_name_id"]]
    df_babies["to_create_count"] = temp_baby_count

    ### rename the name id to parent_name_id_A and parent_name_id_B
    ### get last name of the person and the spouse by splitting their ids where     
    #: df["unique_name_id"] = df_babies["first_name"] + "_" +  df["last_name"] + "_"+\ df["temp_id"].astype(str)
    # last_name_mother = df["unique_name_id"].str.split("_").str[1]
    #last_name_father = df["spouse_name_id"].str.split("_").str[1]

    df_babies["parent_name_id_A"] = df_babies["unique_name_id"]
    df_babies["parent_name_id_B"] = df_babies["spouse_name_id"]

    df_babies["last_name"] = df_babies["unique_name_id"].str.split("_").str[1]
    df_babies["last_name"] += " "+df_babies["spouse_name_id"].str.split("_").str[1]

    ### drop the unique_name_id and spouse_name_id
    df_babies.drop(columns=["unique_name_id", "spouse_name_id"], inplace=True)

    ### if to_create_count is 1 then add the baby to the person and the spouse
    df_babies = df_babies.explode("to_create_count")

    ### drop the to_create_count 
    df_babies.drop(columns=["to_create_count"], inplace=True)

    current_year = df["year"].max()

    df_babies = generate_names_and_initial_data_babies(df_babies, current_year)
    print("New Babies: ", df_babies.shape[0])

    df2 = pd.concat([df_non_candidates, df_with_no_new_children, df_with_new_children, df_babies], ignore_index=True)

    return df2                       

def generate_names_and_initial_data_babies(df, current_year):

    df['age'] = 0
    df["year"] = current_year
    df['age_range'] = 'Baby'

    ### set gender using GENDER_PROBS
    df["gender"] = np.random.choice(list(GENDER_PROBS.keys()),
                                    len(df),
                                    p=np.array(list(GENDER_PROBS.values())))

    ### count Males and get index
    gd = df['gender'] == "Male"
    ### generate unique male names using numpy
    df.loc[gd, "first_name"] = np.random.choice(MALE_FIRST_NAMES,gd.sum())
    #print("male names",gd.sum())              
    df.loc[~gd, "first_name"] = np.random.choice(FEMALE_FIRST_NAMES,len(gd) - gd.sum())
    #print("female names",len(gd) - gd.sum())

    df["event"] = "Born"
    df["full_name"] = df["first_name"] + " " + df["last_name"]

    str_num = np.random.randint(0, 1000000000, len(df))
    df["temp_id"] = str_num
    df["unique_name_id"] = df["first_name"] + "_" +\
                           df["last_name"] + "_"+\
                           df["temp_id"].astype(str)
    
    df.drop(columns=["temp_id"], inplace=True)

    df = generate_initial_constants(df)
    return df
#%%
def birth_prob_curves(age,existing_children_count):
    ### curves constants
    c_cst = BIRTH_PROB_CURVES_CST
    ### A1 * EXP ( (AGE -A2)/A3) = AGE PROB SUBTRACTION
    ### B1 * LN(EXISTING CHILDREN COUNT+B2) - B3 = EXIST CHILDREN PROB
    ### A3 = A1 * C0
    ### B1 = A1*C1
    ### B2 = A1 * C2
    ### B3 = B2 / C3

    age_prob_subtraction = c_cst["Age Exp Constant -> A1"]*\
                            np.exp((age - c_cst["Age Sub Constant -> A2"])/\
                            c_cst["Age Div Constant -> A3"])

    exist_children_prob = c_cst["Ext. Child Mult -> B1"]*\
                          np.log(existing_children_count + c_cst["Ext. Child CT -> B2"]) -\
                          c_cst["Correction Factor -> B3"]

    prob = 1 - age_prob_subtraction - exist_children_prob
    if prob < 0:
        prob = 0.000000001

    return prob

#%% generate a table with the combinations of age and existing children count
def generate_birth_prob_table():
    age = np.arange(17, 75)
    children = np.arange(0, 10)
    df = pd.DataFrame()
    for i in age:
        for j in children:
            temp = pd.DataFrame({"age": i, "existing_children_count": j}, index=[0])
            df = pd.concat([df, temp], ignore_index=True)
    df["total_prob"] = df.apply(lambda x: birth_prob_curves(x["age"], x["existing_children_count"]), axis=1)
    return df

#%%
if False:
    birth_table = generate_birth_prob_table()
    pivot = birth_table.pivot("age", "existing_children_count", "total_prob")

    plt.figure(figsize=(10, 10))
    sns.heatmap(pivot, cmap="coolwarm", annot=True)
    plt.show()
# %%
