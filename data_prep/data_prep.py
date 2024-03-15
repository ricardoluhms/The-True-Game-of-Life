#%%
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
### read data from test_files
import pandas as pd

folder = os.path.dirname(__file__)
root_folder = os.path.abspath(os.path.join(folder, os.pardir))
file = os.path.join(root_folder, 
                    'test_files', 
                    'data', 
                    'test_city_500_init_pop_100_years_1950_start_year_2024_03_15_13_30.csv')
data = pd.read_csv(file,low_memory=False) 
#%%
### check death type in "event" column
is_death = data['event'].str.contains('death')
data['event'][is_death].value_counts()
### death is not being recorded in the event column

### for each unique_name_id get the highest age and its respective year

#%%
### create a dataframe to store the highest age and its respective year
### copy the data to a new dataframe
max_age_df = data.copy()
keep_columns = ['unique_name_id','age','year']
### sort by unique_name_id and age, where age is the highest
max_age_df = max_age_df[keep_columns].\
                sort_values( by=['unique_name_id','age'], 
                             ascending=[True,False])
### drop duplicates keeping the first entry
max_age_df = max_age_df.drop_duplicates(subset='unique_name_id', keep='first')

### create a dataframe that retrieve the age the they were born
### copy the data to a new dataframe
min_age_df = data.copy()

### sort by unique_name_id and age, where age is the lowest
min_age_df = min_age_df[keep_columns].\
                sort_values( by=['unique_name_id','age'], 
                             ascending=[True,True])
### drop duplicates keeping the first entry
min_age_df = min_age_df.drop_duplicates(subset='unique_name_id', keep='first')

### merge the two dataframes
age_df = pd.merge(max_age_df, min_age_df, on='unique_name_id', suffixes=('_max', '_min'))
# %%
#plot the age distribution by year
import seaborn as sns
import matplotlib.pyplot as plt
#%%

age_df['age_max'].hist(bins=100)
plt.show()

# %%
