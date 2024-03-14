#%%
### set system path
import os
import sys
import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

### remove Future Warning from pandas
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
from modules.city import City # , 
from modules.person import Person_Life, Person_Functions # 
import pandas as pd
import tqdm

# Create a city
#%%GENERATING CITY AND PEOPLE

city = City("Test City",population=7, current_year=1950, mode='testing')

###Generate specific young adults

###Generating people with pocket money and part time careers
pocket = Person_Life('Male', 'Pocket', 'Money', None, None, career="Pocket Money", income=100, spender_profile='Average')
part = Person_Life('Female', 'Part', 'Time', None, None, career='Part Time', income=100, spender_profile='Average')

###Generating people with loan 0 and loan None
loan_free1 = Person_Life('Male', 'No', 'Loan', None, None, career="Medium", loan=0, income=100, spender_profile='Average')
loan_free2 = Person_Life('Female', 'None', 'Loan', None, None, career="Medium", loan=None, income=100, spender_profile='Average')

###Person with not enough to pay loan
poor = Person_Life('Male', 'Poor','Smith', career='Base', loan=1000, loan_term=5, balance=100, income=100, spender_profile='Average')
###Perosn with enough to make payment
middle = Person_Life('Male', 'Average', 'Smith', career='Medium', loan=1000, loan_term=5, balance=1000, income=100, spender_profile='Average')
###Person with enough to fully pay off loan
rich = Person_Life('Male', 'Rich', 'Smith', career='High', loan=200, loan_term=1, balance=5000, income=100, spender_profile='Average')


###Creating a list of people so that we can loop over it to add them all
people_list = [pocket, part, loan_free1, loan_free2, poor, middle, rich]
people_names = []

#%%VALIDATING THE PEOPLE

#for person in people_list:
    #print("SpenderProfile:" + person.first_name)
    #print("L_name:" + person.last_name)
    #print("Career:" + str(person.career))
    #print("Loan:" + str(person.loan))
    #print("Loan_term:" + str(person.loan_term))
    #print("Balance:" + str(person.balance))



#%%###ADD THEM TO THE CITY







###Adds everyone to the city and keeps track of their unique name id so we can reference them below
for person in people_list:
    temp_history = person.history_df.iloc[-1].copy()
    unique_name_id = temp_history['unique_name_id']
    ###For finding out what their id is so we can test below
    people_names.append(unique_name_id)
    city.people_obj_dict[unique_name_id] = person

    temp_full_history = person.history_df

    city.history = pd.concat([city.history, temp_full_history], ignore_index=True)



    

#%% 'PASS' TESTS

###Test1 Pocket money and Part time (Should pass the pay loan)

    ###Check through debugging that it indeed passes the loan function

#%%

###Test2 not c4 (loan is 0 or None)

    ###Check through debuggin that this does indeed pass the loan function


#%%LOAN TESTS
    
###Age up the city to activiate the loan payment
city.age_up()


#%%Test if they don't have money to pay the loan (and interest increases)
    

#This gives us the unique name id for the person that we need for the test
person_id = people_names[4]

#Person_obj will be that specific person in the city dictionary we will call it by name (key)
person = city.people_obj_dict[person_id]
person_last_history = person.history_df.iloc[-1].copy()

###Checking to see if person's balance is less than what he should pay
temp_loan_payement = person.loan / person.loan_term

if temp_loan_payement > person.balance:
    print("This person does not have enough to pay his loan")

    ###Test changing spender profile, event update, and loan update to both the df and the object

print(person_last_history["event"] == "Loan Payment Failed - Spender Profile Decreased")
print(person_last_history['loan'])

###This should tell us if interest was added
print(person.loan)

print(person.spender_prof)








#%%Test if the loan is fully paid off
 
###Age up the city to activiate the loan payment
#city.age_up()

#Grabbing the specific person the test applies to
person_id = people_names[6]

person = city.people_obj_dict[person_id]
person_last_history = person.history_df.iloc[-1].copy()

print(person.first_name)
print(person.loan == 0)
print(person.interest_rate == 0)
print(person_last_history["event"] == "Loan Payment Complete")


print(person_last_history['loan_term'])
print(person_last_history['loan'])
print(person_last_history['balance'])

#%%Test if loan is not fully paid off


#Grabbing the specific person the test applies to
person_id = people_names[5]

person = city.people_obj_dict[person_id]
person_last_history = person.history_df.iloc[-1].copy()


print(person_last_history["event"] == "Loan Payment OK")
print(person.loan)


print(person_last_history['loan_term'])
print(person_last_history['loan'])
print(person_last_history['balance'])


# %%
