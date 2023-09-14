import numpy as np
import pandas as pd
from collections import defaultdict

from  gml_constants import (MALE_FIRST_NAMES, FEMALE_FIRST_NAMES, LAST_NAMES, 
                            GENDER_PROBS,SPENDER_PROFILE_PROBS,
                            AGE_RANGES,AGE_RANGE_PROB_DICT,
                            UGRAD_START_AGE, MAX_UGRAD_START_AGE,
                            PART_TIME_JOB_MIN_AGE,  PART_TIME_JOB_PROB,                           
                            YEARS_OF_STUDY, TUITION, SPENDER_PROFILE,
                            INITIAL_CAREER_PROBS_BY_AGE, INITIAL_INCOME_RANGES,
                            FUTURE_CAREER_PAY_PROBS,STUDENT_LOAN_INTEREST_RATES,
                            CAREERS_AND_MARRIAGE_PROBS)
import random
from datetime import date




#%%

class Starter_Data_Person():

    def __init__(self, gender:str =None, first_name = None, last_name = None, 
                      current_year = None, age_range: str = None,
                      career: str = None, future_career: str = None, income: int = None,
                      loan: int = None, loan_term: int = None, balance: int = None,
                      married: bool = False, children: int = 0, spender_prof: str = None,
                      year_of_study: int = None,
                      year_to_study: int = None):
        """ age_range options: 'Baby', 'Child', 'Teenager', 'Young Adult', 'Adult', 'Elder' \n
            gender options: 'Male' or 'Female' """
        if gender is None:
            gender = np.random.choice(GENDER_PROBS.keys(),p=GENDER_PROBS.values())
        self.gender = gender
        self.first_name = first_name;  self.last_name = last_name
        self.generate_full_name()
        self.unique_name_id = self.generate_unique_name_id()
        if current_year is None:
            current_year = date.today().year
        self.current_year = current_year
        self.age_range, self.age = self.initial_age(age_range)       
        self.career = career
        self.future_career = future_career
        self.year_of_study = year_of_study
        self.year_to_study = year_to_study
        self.income = income
        self.loan = loan
        self.loan_term = loan_term
        self.interest_rate = None
        self.balance = balance
        self.married = married
        self.children = children
        self.spender_prof = spender_prof
        self.event = "Created"
        self.history = []
        self.update_history(self.event)


    def generate_first_name(self):#
        if self.gender == "Female":
            name = random.choice(FEMALE_FIRST_NAMES)
        else:
            name = random.choice(MALE_FIRST_NAMES)
        return name

    def generate_full_name (self):#
        if self.last_name is None:
            self.last_name = random.choice(LAST_NAMES)
        if self.first_name is None:
            self.first_name = self.generate_first_name()
        self.full_name = self.first_name + " " + self.last_name

    def generate_unique_name_id(self):#
        ### contains the first name, last name, and a random number between 0 and 1000 without spaces
        return self.first_name +"_"+ self.last_name +"_"+ str(random.randint(0, 10000))
    
    def update_age_range(self):#
        for age_range, age_range_list in AGE_RANGES.items():
            if age_range_list[0] <= self.age <= age_range_list[1]:
                return age_range

    def initial_age(self, age_range=None):#
        if age_range is None:
            age = np.random.randint(AGE_RANGES["Baby"][0], AGE_RANGES["Elder"][1])
            age_range = self.update_age_range()
        else:
            age = np.random.randint(AGE_RANGES[age_range][0], AGE_RANGES[age_range][1])
            age_range = age_range
        return age_range, age

    def update_history(self, event:str):
        self.history.append({"Gender":self.gender,
                             'First Name': self.first_name,
                             'Last Name': self.last_name,
                             'Full Name': self.full_name,
                             'Unique Name ID': self.unique_name_id,
                             'Age': self.age,
                             'Age Range': self.age_range,
                             'Career': self.career,
                             'Future Career': self.future_career,
                             'Income': self.income,
                             'Spender Profile': self.spender_prof,
                             'Loan': self.loan,
                             'Loan Term': self.loan_term,
                             'Balance': self.balance,
                             'Married': self.married,
                             'Children': self.children,
                             'Year': self.current_year,
                             "Year of Study":self.year_of_study,
                             "Year to Study":self.year_to_study,
                             'db_event': event})
    
    def update_history_from_dict(self, history_dict:dict):
        self.history.append(history_dict)

    def student_loan(self, future_career, balance, loan, loan_term, interest_rate=None):### review this function
        
        ### Tuition due
        tuition_due = TUITION[future_career]
        
        if interest_rate is None:
            interest_rate = random.uniform(STUDENT_LOAN_INTEREST_RATES[0], 
                                                STUDENT_LOAN_INTEREST_RATES[1])

        # Subtract tuition from balance
        balance -= tuition_due

        if balance > 0:
            ### Student has enough money to pay for the tuition
            loan = 0
            loan_term = 0
        else:
            ### Student does not have enough money to pay for the tuition
            new_loan = abs(balance) * (1 + interest_rate)**(loan_term)
            if loan != 0:
                loan += new_loan
            else:
                ### Student does not have loan and will need to get a loan on the remaining balance
                loan = new_loan
            balance = 0
            
        return loan, loan_term, interest_rate, balance

    def retrieve_last_history(self):
        return self.history[-1]
    
    def retrieve_history(self):
        return self.history

    def marriage_chance(self):

        career_crit_chance = CAREERS_AND_MARRIAGE_PROBS[self.career][0]
    
        if self.age >= 16 and self.married == False:
        
            if np.random.random() < career_crit_chance:
                self.marriage()
                _, marriage_expense = self.calculate_marriage_cost()
                total_balance = self.balance + self.spouse.balance
                if total_balance < marriage_expense:
                    get_loan_status = self.get_loan(desired_loan_amount=marriage_expense-total_balance)
                    if  get_loan_status is None:
                        print('You cannot afford the marriage expense. You have reached the maximum loan amount.')
    
    def marriage(self):

        if self.gender == "Male":
            spouse_gender = 'Female' if np.random.random() < 0.75 else 'Male'
        else:
            spouse_gender = 'Male' if np.random.random() < 0.75 else 'Female'
        spouse = Starter_Data_Person(spouse_gender,age_range=self.age_range)
        spouse.married = True
        self.spouse = spouse
        self.married = True
        self.update_history()

### Generate a class Person that keeps track of multiple Classes such as Baby, Child, Teenager, Young Adult, Adult, Elder
### if the baby ages up to a child, then the baby class is deleted and a child class is created using the baby class attributes
### if the child ages up to a teenager, then the child class is deleted and a teenager class is created using the child class attributes
### if the teenager ages up to a young adult, then the teenager class is deleted and a young adult class is created using the teenager class attributes
### if the young adult ages up to an adult, then the young adult class is deleted and an adult class is created using the young adult class attributes
### if the adult ages up to an elder, then the adult class is deleted and an elder class is created using the adult class attributes

class Person_Life(Starter_Data_Person):
    def __init__(self, gender:str =None, first_name:str = None, last_name:str = None, current_year:int = None, age_range: str = None):
        super().__init__(gender, first_name, last_name, current_year, age_range)
    
    ### there will be two main scenarios:
    # - the person is a recent born from a couple and just ages up
    # - the person was randomly generated and has a random age and we would need to know previous events from the past and then age up

    ### every time a person ages up, we need to update the history and check if the class changes 
    ### if the class changes, we need to delete the previous class and create a new class inheriting from the previous class last history

    ### if a person is created straight ahead as an elder then we need to create adult, teenager, child, baby classes and update their history
    ### if a person is created straight ahead as an working adult then we need to create child and teenager,child, baby classes and update their history
    ### if a person is created straight ahead as an teenager then we need to create child and baby classes and update their history
    ### if a person is created straight ahead as an child then we need to create baby classes and update their history
    ### if a person is created straight ahead as an baby then we need to create baby classes and update their history

    def get_created_history(self):
        return self.history[0]

    def generate_past_history(self):
        past_year = self.current_year - 1
        past_age = self.age - 1
        past_age_range = self.update_age_range()
        ### check age_range



    def elder(self):

        ### life events

        ### adult to elder


        ### baby to child
        ### child to teenager
        ### teenager to young adult
        ### young adult to adult
        ### adult to elder
        pass

    def adult(self):
        ### life events
        ### baby to child
        ### child to teenager
        ### teenager to young adult
        ### young adult to adult
        pass

    def young_adult(self):
        self.teenager_life()
        temp_history = self.history[-1]
        self.temporary_income = None
        new_income_check = False
        for age in range(AGE_RANGES['Young Adult'][0],AGE_RANGES['Young Adult'][1]+1):
            
            ### First Year of Study 
            if age == AGE_RANGES['Young Adult'][0]:
                temp_history['Event'] = "Become Young Adult"

                ### set future career and update current career
                future_career = np.random.choice( FUTURE_CAREER_PAY_PROBS.keys(), 
                                                  p=FUTURE_CAREER_PAY_PROBS.values())
                temp_history['Future Career'] = future_career
                temp_history['Years of Study'] = 0
                temp_history['Years to Study'] = YEARS_OF_STUDY[future_career]
                if temp_history['Career'] == "Part Time Job":
                    temp_history['Career'] = "Student with Part Time Job"
                elif temp_history['Career'] == "Pocket Money":
                    temp_history['Career'] = "Student with Pocket Money"
            else:
                temp_history['Event'] = "Aged Up"
                temp_history['Years of Study'] += 1
                temp_history['Years to Study'] -= 1

            ### Part Time Job - Check if the person will get a part time job
            if np.random.random() >= PART_TIME_JOB_PROB and temp_history['Career'] == "Student with Pocket Money":
                temp_history['Career'] = "Student with Part Time Job"
                temp_history['Income'] = np.random.choice( INITIAL_INCOME_RANGES['Part Time Job'][0],
                                                             INITIAL_INCOME_RANGES['Part Time Job'][1])
    
            ## check if the person has finished studying
            student_career = ["Student with Part Time Job",  "Student with Pocket Money"]

            ### chance of getting a job - initiallly will be 100% rewrite this later
            if temp_history['Years to Study'] == 0 and temp_history['Career'] in student_career:

                temp_history['Career'] = temp_history['Future Career']
                temp_history['Future Career'] = None
                temp_history['Years of Study'] = YEARS_OF_STUDY[future_career]
                temp_history['Years to Study'] = 0

                new_income = np.random.choice( INITIAL_INCOME_RANGES[temp_history['Career']][0],
                                                            INITIAL_INCOME_RANGES[temp_history['Career']][1])
                previous_income = temp_history['Income']
                ### random month to start working
                month = 1/np.random.randint(1,13)

                temp_history['Income'] = new_income*month + previous_income*(1-month)
                new_income_check = True
            ## updates second year of work
            elif temp_history['Years to Study'] == 0 and temp_history['Career'] not in student_career:
                if new_income_check:
                    temp_history['Income'] = new_income
                    new_income_check = False

            ### Student - Check if the person will need a loan
            pack = self.student_loan( future_career, 
                                      temp_history['Balance'], 
                                      temp_history['Loan'], 
                                      temp_history['Loan Term'],
                                      temp_history['Interest Rate'])
            
            ### return reviewed loan, loan term, interest rate, and balance
            temp_history['Loan'], temp_history['Loan Term'], temp_history['Interest Rate'], temp_history['Balance']  = pack
            
            temp_history['Balance'] += temp_history['Income'] -\
                            temp_history['Income']*SPENDER_PROFILE[temp_history['Spender Profile']]

            temp_history["Year"] += 1
            temp_history["Age"] = age
            temp_history["Age Range"] = self.update_age_range()

            ### check if the person will get married



            

            


        ### life events
        ### will go to college/university
        ### will get a loan
        ### will get a job
        ### may get married
        ### may have children
        ### may get a house
        ### may get a car

        pass

    def teenager_life(self):
        self.child_life()
        temp_history = self.history[-1]
    
        ### life events
        #### can get a part time job with a probability when 16 years old
        for age in range(AGE_RANGES["Teenager"][0],AGE_RANGES["Teenager"][1]+1):
            if age == AGE_RANGES["Teenager"][0]:
                temp_history['Event'] = "Become Teenager"
                temp_history['Career'] = "Pocket Money"
            else:
                temp_history['Event'] = "Aged Up"


            if age >= PART_TIME_JOB_MIN_AGE:
                if temp_history['Career'] == "Pocket Money" and np.random.random() >= PART_TIME_JOB_PROB:
                    temp_history['Career'] = "Part Time Job"
                temp_history['Income'] = np.random.choice( INITIAL_INCOME_RANGES['Part Time Job'][0],
                                                             INITIAL_INCOME_RANGES['Part Time Job'][1])
                
            temp_history['Balance'] += temp_history['Income'] -\
                            temp_history['Income']*SPENDER_PROFILE[temp_history['Spender Profile']] 
            temp_history["Year"] += 1
            temp_history["Age"] = age
            temp_history["Age Range"] = self.update_age_range()
            self.update_history_from_dict(temp_history)
        pass

    def child_life(self):
        self.baby_life()
        temp_history = self.history[-1]

        ### life events
        #### gain pocket money
        for age in range(AGE_RANGES["Child"][0],AGE_RANGES["Child"][1]+1):
            if age == AGE_RANGES["Child"][0]:
                temp_history['Event'] = "Become Child"
            else:
                temp_history['Event'] = "Aged Up"

            temp_history["Year"] += 1
            temp_history["Age"] = age
            temp_history["Age Range"] = self.update_age_range()

            if age == 5:
                temp_history['Career'] = "Pocket Money"
                temp_history['Income'] = np.random.choice( INITIAL_INCOME_RANGES['Pocket Money'][0],
                                                           INITIAL_INCOME_RANGES['Pocket Money'][1])
                
                temp_history['Spender Profile'] = np.random.choice( SPENDER_PROFILE_PROBS.keys(),
                                                                    p = SPENDER_PROFILE_PROBS.values())
                
            if temp_history['Career'] == "Pocket Money":
                temp_history['Balance'] += temp_history['Income'] -\
                                           temp_history['Income']*SPENDER_PROFILE[temp_history['Spender Profile']]

            self.update_history_from_dict(temp_history)

    def baby_life(self):### to test
        temp_history = self.history[0]
        year_born = temp_history["Year"] - temp_history["Age"]
        temp_history['Event'] = "Born"
        for age in range(AGE_RANGES["Baby"][0],AGE_RANGES["Baby"][1]+1):
            if age == AGE_RANGES["Baby"][0]:
                temp_history["Year"] = year_born
            else:
                temp_history["Year"] += 1
                temp_history['Event'] = "Aged Up"


            temp_history["Age"] = age
            temp_history["Age Range"] = self.update_age_range()   
            self.update_history_from_dict(temp_history)




