#%%
import pandas as pd
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from person import Person_Life
from city import City

###Create a city
city = City("Boludos City",population=2, current_year=1950, mode='testing')





#%%
### Mariage Tests ###

"""
Tests the marriage function by adding 2 specific people into the city

Parameters:
    age1 - integer age of the first person
    age2 - integer age of the second peron
    gender1 - string gender of the first person 
    gender2 - string gender of the second person
    married1 - boolean if person1 is married
    married2 - boolean if person2 is married

Returns:
    a list containing both people objects 
"""
def test_marriage(age1, age2, gender1, gender2, married1, married2):
    ###Sets the age of each person
    person1_age = age1
    person2_age = age2

    ###Create the people we want
    person = Person_Life(gender1,None,None,current_year=2023, age_range="Baby", married=married1)
    person2 = Person_Life(gender2,None,None,current_year=2023, age_range="Baby", married=married2)

    for _ in range(person1_age):
        person.age_up()

    for _ in range(person2_age):
        person2.age_up()


    ###Adds the first person to the city dataframe
    temp_history = person.history_df.iloc[-1].copy()
    unique_name_id = temp_history['unique_name_id']
    city.people_obj_dict[unique_name_id] = person

    temp_full_history = person.history_df

    city.history = pd.concat([city.history, temp_full_history], ignore_index=True)
    
    ###Adds the second person to the city dataframe
    temp_history = person2.history_df.iloc[-1].copy()
    unique_name_id = temp_history['unique_name_id']
    city.people_obj_dict[unique_name_id] = person2

    temp_full_history = person2.history_df

    city.history = pd.concat([city.history, temp_full_history], ignore_index=True)
    

    ### Test Marriage Function
    city.handle_marriage(person)

    ###COMMENT THIS OUT WHEN TESTING "TWO ELIGIBLE PEOPLE" or "ONLY ONE PERSON IN CITY" BECAUSE FOR THAT TEST WE ONLY NEED TO MARRY ONCE
    city.handle_marriage(person2)

    ### Return the people so we can check thier marriage status
    return [person, person2]


#%%

### Test someone not of age
#people = test_marriage(10, 12, 'Male', 'Female', False, False)

### Checks to see if the most recent history matches up with what it should be
#print(people[0].history_df.iloc[-1]['married'] == False)
#print(people[0].history_df.iloc[-1]['just_married'] == False)
#print(people[0].history_df.iloc[-1]['spouse_name_id'] == None)

#print(people[1].history_df.iloc[-1]['married'] == False)
#print(people[1].history_df.iloc[-1]['just_married'] == False)
#print(people[1].history_df.iloc[-1]['spouse_name_id'] == None)

#%%
### Test someone who is already married
#people = test_marriage(18, 20, 'Male', 'Female', True, False)

### Person 0 is already married so this shouldn't change
#print(people[0].history_df.iloc[-1]['married'] == True)
#print(people[0].history_df.iloc[-1]['just_married'] == False)
#print(people[0].history_df.iloc[-1]['spouse_name_id'] == None)

### Person 1 should be married since because there is no candidate we make one (I'm not testing just married because it could be true or false)
#print(people[1].history_df.iloc[-1]['married'] == True)
###Makes sure that person 1 is not married to person 0
#print(people[1].history_df.iloc[-1]['spouse_name_id'] != people[0].history_df.iloc[-1]['unique_name_id'])

#%%
### Test two people that are more than 5 years apart 
#people = test_marriage(16, 24, 'Male', 'Female', False, False)

### Person 0 should be married but not to the second person but both should be married because we make a new candidate
#print(people[0].history_df.iloc[-1]['married'] == True)
#print(people[0].history_df.iloc[-1]['spouse_name_id'] != people[1].history_df.iloc[-1]['unique_name_id'])

### Person 1 should be married but not to the first person
#print(people[1].history_df.iloc[-1]['married'] == True)
#print(people[1].history_df.iloc[-1]['spouse_name_id'] != people[0].history_df.iloc[-1]['unique_name_id'])


#%% 
###Test Two eligible people
#people = test_marriage(16, 16, 'Male', 'Female', False, False)

### Person 0 should be married to the other person
#print(people[0].history_df.iloc[-1]['married'] == True)
#print(people[0].history_df.iloc[-1]['spouse_name_id'] == people[1].history_df.iloc[-1]['unique_name_id'])

### Person 1 should be married to the other person
#print(people[1].history_df.iloc[-1]['married'] == True)
#print(people[1].history_df.iloc[-1]['spouse_name_id'] == people[0].history_df.iloc[-1]['unique_name_id'])


#%%
###Test when there is only one person in the city
#people = test_marriage(16, 16, 'Male', 'Female', False, False)

### Only need to test one person he should be married but not to himself
#print(people.history_df.iloc[-1]['married'] == True)
#print(people.history_df.iloc[-1]['spouse_name_id'] != people.history_df.iloc[-1]['unique_name_id'])


###Test same sex marriage
###This does work as I came across a couple instances during my other tests


# %%
