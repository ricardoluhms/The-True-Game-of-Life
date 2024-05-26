#%%
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
#%%
### Create a generic function to create the matrix dataframes

def create_age_matrix( df: pd.DataFrame, plot=True) -> pd.DataFrame:
    ages = df['age'].values
    age_matrix = np.abs(ages[:, np.newaxis] - ages)
    ### add row values to index and column values to columns
    ### age matrix true if age difference is less than 5 - binary to 0 and 1
    age_matrix2 = age_matrix < 5
    ### remove the diagonal

    age_matrix2 = age_matrix2.astype(int)
    age_matrix2 = age_matrix2 - np.eye(age_matrix2.shape[0])
    if plot:
        print("Age Matrix")
        age_matrix_df = pd.DataFrame(age_matrix2, index=df['age'], columns=df['age'])
        sns.heatmap(age_matrix_df, annot=True, cmap='coolwarm')
        plt.show()
    return age_matrix2

def create_parent_matrix( df: pd.DataFrame, plot=True) -> pd.DataFrame:
    parent_name_id_A = df['parent_name_id_A'].values
    parent_name_id_B = df['parent_name_id_B'].values
    parent_matrix_A = parent_name_id_A[:, np.newaxis] != parent_name_id_A
    parent_matrix_B = parent_name_id_B[:, np.newaxis] != parent_name_id_B

    parent_matrix_A = parent_matrix_A.astype(int) #- np.eye(parent_matrix_A.shape[0])
    parent_matrix_B = parent_matrix_B.astype(int) #- np.eye(parent_matrix_B.shape[0])

    parent_matrix_AB = parent_matrix_A * parent_matrix_B
    parent_matrix_AB = parent_matrix_AB.astype(int)

    if plot:
        print("Parent Matrix")
        parent_matrix_AB_df = pd.DataFrame(parent_matrix_AB, 
                                        index=df['parent_name_id_A']+ " & " + df['parent_name_id_B'],
                                        columns=df['parent_name_id_A']+ " & " + df['parent_name_id_B'])
        sns.heatmap(parent_matrix_AB_df, annot=True, cmap='coolwarm')
        plt.show()
    return parent_matrix_AB

def create_het_matrix( df: pd.DataFrame, plot=True) -> pd.DataFrame:
    ### Partner matrix Heterosexual
    partner_type = df['partner_type'].values
    partner_matrix = partner_type[:, np.newaxis] == partner_type
    partner_matrix = partner_matrix.astype(int) - np.eye(partner_matrix.shape[0])

    ## transform to dataframe
    partner_matrix_df = pd.DataFrame(partner_matrix, 
                                    index=df['partner_type'], 
                                    columns=df['partner_type'])

    ### Gender matrix
    gender_type = df['gender'].values
    gender_matrix = gender_type[:, np.newaxis] != gender_type
    ### remove the diagonal
    gender_matrix = gender_matrix.astype(int)


    ### Heterosexual filter
    partner_matrix2 = partner_matrix.copy()
    ### if index or column is not heterosexual, set to 0
    partner_matrix2[partner_matrix_df.index != 'Heterosexual'] = 0
    partner_matrix2[:, partner_matrix_df.columns != 'Heterosexual'] = 0

    ### hetero matrix
    hetero_matrix = partner_matrix2 * gender_matrix

    if plot:
        print("Heterosexual Matrix")
        hetero_matrix_df = pd.DataFrame(hetero_matrix,
                                        index=will_marry_df['partner_type'] + " & " + will_marry_df['gender'],
                                        columns=will_marry_df['partner_type'] + " & " + will_marry_df['gender'])
        sns.heatmap(hetero_matrix_df, annot=True, cmap='coolwarm')
        plt.show()
    return hetero_matrix

def create_les_gay_matrix( df: pd.DataFrame, plot=True) -> pd.DataFrame:
    ### Gender matrix
    gender_type = df['gender'].values
    gender_matrix2 = gender_type[:, np.newaxis] == gender_type
    gender_matrix2 = gender_matrix2.astype(int) - np.eye(gender_matrix2.shape[0])

    ### Partner
    partner_type = df['partner_type'].values
    partner_matrix = partner_type[:, np.newaxis] == partner_type
    partner_matrix_df = pd.DataFrame(partner_matrix,
                                    index = df['partner_type'],
                                    columns = df['partner_type'])

    partner_matrix2 = partner_matrix.copy()
    partner_matrix2[partner_matrix_df.index != 'Gay/Lesbian'] = 0
    partner_matrix2[:, partner_matrix_df.columns !="Gay/Lesbian"] = 0

    g_and_l_matrix = partner_matrix2 * gender_matrix2

    if plot:
        print("Gay and Lesbian Matrix")
        g_and_l_matrix_df = pd.DataFrame(g_and_l_matrix,
                                        index = df['partner_type'] + " & " +\
                                               df["gender"],
                                        columns = df['partner_type'] + " & " +\
                                                 df["gender"])
        sns.heatmap(g_and_l_matrix_df, annot=True, cmap='coolwarm')

        plt.show()
    
    return g_and_l_matrix

def create_bi_matrix( df: pd.DataFrame, plot=True) -> pd.DataFrame:
    ### Partner
    partner_type = df['partner_type'].values
    partner_matrix = partner_type[:, np.newaxis] == partner_type
    partner_matrix_df = pd.DataFrame(partner_matrix,
                                    index = df['partner_type'],
                                    columns = df['partner_type'])

    partner_matrix2 = partner_matrix.copy() - np.eye(partner_matrix.shape[0])
    partner_matrix2[partner_matrix_df.index != 'Bisexual'] = 0
    partner_matrix2[:, partner_matrix_df.columns !="Bisexual"] = 0
    bis_matrix = partner_matrix2 

    if plot:
        print("Bisexual Matrix")
        bis_matrix_df = pd.DataFrame(bis_matrix,
                                        index = df['partner_type'],
                                        columns = df['partner_type'])
        
        sns.heatmap(bis_matrix_df, annot=True, cmap='coolwarm')

        plt.show()

    return bis_matrix

def to_marry_list( age_array: np.array, 
                  parent_array: np.array, 
                  het_array: np.array,
                  gay_lessbian_array: np.array,
                  bi_array: np.array) -> np.array:
    
    to_marry = []
    ### create id matrix

    ### combine age, parent, het
    to_marry_het = (age_array * parent_array) * het_array

    to_marry_het_lower_triang = np.tril(to_marry_het, k=-1)

    ### get the indices and columns where the value is 1
    indices = np.where(to_marry_het_lower_triang == 1)

    indices_het = np.array(indices).T

    ### this will generate the unique_id to marry
    ### each row is a unique_id pair to marry

    ### combine age, parent, gay_lessbian
    to_marry_gay_lessbian = (age_array * parent_array) * gay_lessbian_array

    to_marry_gl_lower_triang = np.tril(to_marry_gay_lessbian, k=-1)

    ### get the indices and columns where the value is 1
    indices = np.where(to_marry_gl_lower_triang == 1)

    indices_gl = np.array(indices).T

    ### combine age, parent, bisexual
    to_marry_bi = (age_array * parent_array) * bi_array

    to_marry_bi_lower_triang = np.tril(to_marry_bi, k=-1)

    ### get the indices and columns where the value is 1
    indices = np.where(to_marry_bi_lower_triang == 1)

    indices_bi = np.array(indices).T

    to_marry = np.concatenate([indices_het, indices_gl, indices_bi], axis=0)

    return to_marry

def non_dups_marriage_pairs(to_marry: np.array) -> pd.DataFrame:
    to_marry_df = pd.DataFrame(to_marry, columns=['unique_id_1', 'unique_id_2'])

    ### flatten the array
    to_marry2 = to_marry.flatten()
    ### to pandas dataframe

    to_marry_dups= pd.DataFrame(to_marry2, columns=["unique_name_id"]).reset_index()
    to_marry_dups.columns = ['counts', "unique_name_id"]
    ### drop duplicates

    dups = to_marry_dups.groupby("unique_name_id").count().reset_index().\
                        sort_values('counts', ascending=False)

    dups = dups[dups['counts'] > 1]["unique_name_id"].values

    dups_mask = to_marry_df['unique_id_1'].isin(dups) | to_marry_df['unique_id_2'].isin(dups)

    to_marry_df_non_dups = to_marry_df[~dups_mask]

    to_marry_df_dups = to_marry_df[dups_mask]

    ### sort the values randomly
    to_marry_df_dupsA = to_marry_df_dups.sample(frac=1).reset_index(drop=True)
    to_marry_df_dupsB = to_marry_df_dupsA.copy()

    ### swap the values
    to_marry_df_dupsB['unique_id_1'] = to_marry_df_dupsA['unique_id_2']
    to_marry_df_dupsB['unique_id_2'] = to_marry_df_dupsA['unique_id_1']

    ### combine the dataframes 
    to_marry_df_cand = pd.concat([to_marry_df_dupsA, to_marry_df_dupsB,to_marry_df_non_dups], ignore_index=True)
    to_marry_df_select = to_marry_df_cand.drop_duplicates("unique_id_1")

    return to_marry_df_select

def get_marriage_pairs(df: pd.DataFrame) -> pd.DataFrame:
    age_array = create_age_matrix(df, plot=False)
    parent_array = create_parent_matrix(df, plot=False)
    het_array = create_het_matrix(df, plot=False)
    gay_les_array = create_les_gay_matrix(df, plot=False)
    bi_array = create_bi_matrix(df, plot=False)

    to_marry = to_marry_list(age_array, parent_array, het_array,
                             gay_les_array, bi_array)
    
    to_marry_df_non_dups = non_dups_marriage_pairs(to_marry)

    dfindex = df["unique_name_id"].reset_index(drop=True).reset_index()
    to_marry_df_non_dups = to_marry_df_non_dups.\
                            merge(dfindex, left_on='unique_id_1', right_on='index', how='left').\
                            drop(columns=['index', 'unique_id_1']).\
                            rename(columns={'unique_name_id': 'unique_id_1'})
    to_marry_df_non_dups = to_marry_df_non_dups.\
                            merge(dfindex, left_on='unique_id_2', right_on='index', how='left').\
                            drop(columns=['index', 'unique_id_2']).\
                            rename(columns={'unique_name_id': 'unique_id_2'})
    
    return to_marry_df_non_dups

# %%
testing = False
if testing:
    person_1 = pd.DataFrame({
        "unique_name_id": [1],
        "age": [15],
        "gender":["Male"],
        "partner_type": ["Heterosexual"],
        "parent_name_id_A": ["John Doe"],
        "parent_name_id_B": ["Jane Doe"],
        'will_marry': [False]
    })
    heterosexual = pd.DataFrame({
        "unique_name_id": [2, 3, 4],
        "age": [21, 22, 50],
        "gender":["Male","Female","Male"],
        "partner_type": ["Heterosexual","Heterosexual","Heterosexual"],
        "parent_name_id_A": ["Peter Doe", "Zero Doe", "Many Doe"],
        "parent_name_id_B": ["Lana Doe", "Lisa Doe", "Linda Doe"],
        'will_marry': [True, True, True]
    })
    gay_lessbian = pd.DataFrame({
        "unique_name_id": [5, 6, 7, 8, 9],
        "age":[24, 25, 30, 31, 51],
        "gender":["Female","Female","Male","Male","Male"],
        "partner_type": ["Gay/Lesbian","Gay/Lesbian","Gay/Lesbian","Gay/Lesbian","Gay/Lesbian"],
        "parent_name_id_A": ["Peter Doe", "Zero Doe", "Many Doe", "Peter Doe", "Zero Doe"],
        "parent_name_id_B": ["Lana Doe", "Lisa Doe", "Linda Doe", "Lana Doe", "Lisa Doe"],
        'will_marry': [True, True, True, True, True]
    })
    bisexual = pd.DataFrame({
        "unique_name_id": [10, 11, 12, 13, 14],
        "age":[36, 37, 41, 42, 55],
        "gender":["Female","Male","Male","Male","Male"],
        "partner_type": ["Bisexual","Bisexual","Bisexual","Bisexual","Bisexual"],
        "parent_name_id_A": ["Peter Doe", "Zero Doe", "Many Doe", "Doug Doe", "Dino Doe"],
        "parent_name_id_B": ["Lana Doe", "Lisa Doe", "Linda Doe", "Linn Doe", "Lass Doe"],
        'will_marry': [True, True, True, True, True]
    })

    ## combine all dataframes
    will_marry_df = pd.concat([person_1, heterosexual, gay_lessbian, bisexual], ignore_index=True)

    age_array = create_age_matrix(will_marry_df)
    parent_array = create_parent_matrix(will_marry_df)
    het_array = create_het_matrix(will_marry_df)
    gay_lessbian_array = create_les_gay_matrix(will_marry_df)
    bi_array = create_bi_matrix(will_marry_df)## to marry lists
    
    to_marry = to_marry_list(age_array, parent_array, het_array,
                            gay_lessbian_array, bi_array)
    
    to_marry_df_non_dups = non_dups_marriage_pairs(to_marry)

    to_marry_df_non_dups = get_marriage_pairs(will_marry_df)
