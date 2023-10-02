#%%
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
class City():
    ### create a city with a name and a population of young adults 
    def __init__(self, name:str, population:int, current_year:int = 1950):
        self.event = "Created"
        self.city_name = name
        self.population = population
        self.current_year = current_year
        self.young_adults = []
        self.history = []
        self.people = self.generate_young_adults(population)

    def age_up(self):
        self.current_year += 1
        ### 
        for i in range(len(self.people)):
            self.people[i].age_up()

    def generate_young_adults(self, population:int = None):
        # make a even distribution of gender
        people_list = [] 
        if population is None:
            population = 1
        for _ in range(self.population):
            current_person = Person_Life(age_range='Young Adult', current_year=self.current_year)

            ### a random max age to a teenager
            max_age = np.random.randint(AGE_RANGES['Teenager'][0],AGE_RANGES['Teenager'][1])

            current_person.teenager_life(max_age)
            people_list.append(current_person)

        return people_list

    def retrieve_history_from_people(self):
        for person in self.people:
            self.history.extend(person.retrieve_history())

class Starter_Data_Person():

    def __init__(self, gender:str =None, first_name = None, last_name = None, 
                      current_year = None, age_range: str = None,
                      career: str = None, future_career: str = None, income: int = None,
                      loan: int = None, loan_term: int = None, balance: int = None,
                      married: bool = False, children: int = 0, spender_prof: str = None,
                      years_of_study: int = None,
                      years_to_study: int = None):
        
        """
        Initialize a new person with various attributes.
        
        Parameters:
        - gender: The gender of the person. Can be 'Male' or 'Female'.
        - first_name, last_name: The name of the person.
        - current_year: The current year for context.
        - age_range: The age category the person belongs to. 
                (age_range options: 'Baby', 'Child', 'Teenager', 'Young Adult', 'Adult', 'Elder' \n)
        - career, future_career: The current and future careers of the person.
        - income: The person's income.
        - loan, loan_term, balance: Financial attributes.
        - married: Marital status.
        - children: Number of children.
        - spender_prof: Spending profile.
        - years_of_study, years_to_study: Education attributes.
        """

        if gender is None:
            gender = np.random.choice( list(GENDER_PROBS.keys()),
                                       p=np.array(list(GENDER_PROBS.values())))
        self.gender = gender
        self.first_name = first_name;  self.last_name = last_name
        self.generate_full_name()
        self.unique_name_id = self.generate_unique_name_id()
        if current_year is None:
            current_year = date.today().year
        self.year = current_year
        self.age_range, self.age = self.initial_age(age_range)       
        self.career = career
        self.future_career = future_career
        self.years_of_study = years_of_study
        self.years_to_study = years_to_study
        self.income = income
        self.loan = loan
        self.loan_term = loan_term
        self.interest_rate = None
        self.balance = balance
        self.married = married
        self.children = children
        self.spender_prof = spender_prof
        self.event = "Created"
        self.history_df = pd.DataFrame(self.get_values(), index=[0])

    def get_values(self):
        constants = {name: value for name, value in vars(self).items() if not callable(value)}
        return constants
    
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
    
    @staticmethod
    def update_age_range(age):#
        for age_range, age_range_list in AGE_RANGES.items():
            if age_range_list[0] <= age <= age_range_list[1]:
                return age_range

    def initial_age(self, age_range=None):#
        if age_range is None:
            age = np.random.randint(AGE_RANGES["Baby"][0], AGE_RANGES["Elder"][1])
            age_range = self.update_age_range(age)
        else:
            age = np.random.randint(AGE_RANGES[age_range][0], AGE_RANGES[age_range][1])
            age_range = age_range
        return age_range, age

    def max_age_check(self, age_range:str, max_age= None):#
        create_max_age = self.history_df['event'] == "Created"
        age_range_check = self.history_df['age_range'] == age_range
        condition = create_max_age & age_range_check
        if condition.sum() >0:
            max_age_current = max_age
            max_age = self.history_df[create_max_age & age_range_check]['age'].values[0]
            #print("max age check", age_range, max_age, max_age_current)
        elif max_age is None or max_age > AGE_RANGES[age_range][1]:
            max_age = AGE_RANGES[age_range][1]
        else:
            max_age = max_age
        return max_age

    def update_history(self,  event:str, new_history=None):
        if event is None:
            event = self.event

        if type(new_history) == pd.Series and new_history is not None:
            new_history['event'] = event
            new_history_df = pd.DataFrame(new_history).T
        else:
            constants = self.get_values()
            constants.pop('history_df', 'Key not found')
            constants['event'] = event
            new_history_df = pd.DataFrame(constants, index=[0])
        self.history_df = pd.concat([self.history_df, new_history_df], ignore_index=True)

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
        self.one_age_range_life("Young Adult")

        ### life events
        ### will go to college/university
        ### will get a loan
        ### will get a job
        ### may get married
        ### may have children
        ### may get a house
        ### may get a car

        pass

    def young_adult_one_year(self, temp_history = None):

        self.temporary_income = None
        new_income_check = False
        student_career = ["Part Time",  "Pocket Money"]

        if temp_history['age'] == AGE_RANGES['Young Adult'][0]:
            event = "Became Young Adult"

            future_career = np.random.choice( list(FUTURE_CAREER_PAY_PROBS.keys()), 
                                            p=np.array(list(FUTURE_CAREER_PAY_PROBS.values())))
            temp_history['future_career'] = future_career
            temp_history['years_of_study'] = 0
            temp_history['years_to_study'] = YEARS_OF_STUDY[future_career]

        else:
            if temp_history['career'] == "Part Time":
                event = "Young Adult - Part Time - Aged Up"
            elif temp_history['career'] == "Pocket Money":
                event = "Young Adult - Pocket Money - Aged Up"

            temp_history['years_of_study'] += 1
            temp_history['years_to_study'] -= 1

        if np.random.random() >= PART_TIME_JOB_PROB and temp_history['career'] == "Pocket Money":
            temp_history['career'] = 'Part Time'
            temp_history['income'] = np.random.choice( INITIAL_INCOME_RANGES['Part Time'][0],
                                                    INITIAL_INCOME_RANGES['Part Time'][1])
            event = "Young Adult - Part Time - Aged Up"
        
        if temp_history['years_to_study'] == 0 and temp_history['career'] in student_career:
            event = "Young Adult - Finished Studies"
            temp_history['career'] = temp_history['future_career']
            temp_history['future_career'] = None
            temp_history['years_of_study'] = YEARS_OF_STUDY[future_career]
            temp_history['years_to_study'] = 0

            new_income = np.random.choice( INITIAL_INCOME_RANGES[temp_history['career']][0],
                                                        INITIAL_INCOME_RANGES[temp_history['career']][1])
            previous_income = temp_history['income']
            month = 1/np.random.randint(1,13)
            temp_history['income'] = new_income*month + previous_income*(1-month)
            new_income_check = True
        elif temp_history['years_to_study'] == 0 and temp_history['career'] not in student_career:
            if new_income_check:
                temp_history['income'] = new_income
                new_income_check = False

        pack = self.student_loan( future_career, 
                                temp_history['balance'], 
                                temp_history['loan'], 
                                temp_history['loan_term'],
                                temp_history['interest_rate'])
        temp_history['loan'], temp_history['loan_term'], temp_history['interest_rate'], temp_history['balance']  = pack
        temp_history['balance'] += temp_history['income'] -\
                                temp_history['income']*SPENDER_PROFILE[temp_history['spender_prof']]

        return temp_history, event

    def teenager_life(self, max_age=None):
        self.child_life(max_age= AGE_RANGES["Child"][1])
        self.one_age_range_life("Teenager", max_age)

    def teenager_life_one_year(self, temp_history = None):
        if temp_history['age'] == AGE_RANGES["Teenager"][0]:
            event = "Become Teenager"

        # Check if it's the start of the teenager age range or "Aged Up"
        elif temp_history['age'] >= PART_TIME_JOB_MIN_AGE:
            if temp_history['career'] == "Pocket Money" and np.random.random() >= PART_TIME_JOB_PROB:
                event = "Teenager - Part Time Job"
                temp_history['career'] = "Part Time"
                base_income = INITIAL_INCOME_RANGES['Part Time'][0]
                std_deviation = INITIAL_INCOME_RANGES['Part Time'][1]
                temp_history['income'] = np.round(np.random.normal(base_income, std_deviation),2)
        elif temp_history['age']>= PART_TIME_JOB_MIN_AGE and temp_history['career'] == "Part Time":
            event = "Teenager - Part Time - Aged Up"
        else:
            event = "Teenager - Aged Up"

        temp_history['balance'] += temp_history['income'] -\
                        temp_history['income'] * SPENDER_PROFILE[temp_history['spender_prof']]

        return temp_history, event

    def child_life(self,max_age = None):
        self.baby_life(max_age= AGE_RANGES["Baby"][1])
        self.one_age_range_life("Child", max_age)

    def child_life_one_year(self, temp_history = None):

        if temp_history['age'] == AGE_RANGES["Child"][0]:
            event = "Become Child"
        else:
            event = "Children - Aged Up"

        if temp_history['age'] == 5:
            event = "Children - First Pocket Money"
            temp_history['career'] = "Pocket Money"
            ### random income is a distribuition based 
            # on INITIAL_INCOME_RANGES['Pocket Money'][0] -+ 
            # a distribution of INITIAL_INCOME_RANGES['Pocket Money'][0]
            base_income = INITIAL_INCOME_RANGES['Pocket Money'][0]
            std_deviation = INITIAL_INCOME_RANGES['Pocket Money'][1]

            temp_history['income'] = np.abs(np.round(np.random.normal(base_income, 
                                                                      std_deviation),2))
   
            temp_history['spender_prof'] = np.random.choice(list(SPENDER_PROFILE_PROBS.keys()),
                                                            p=np.array(list(SPENDER_PROFILE_PROBS.values())))

        if temp_history['career'] == "Pocket Money":
            #print(temp_history)
            if temp_history['balance'] is None:
                temp_history['balance'] = 0
            temp_history['balance'] += temp_history['income'] -\
                                        np.round( temp_history['income'] *\
                                                  SPENDER_PROFILE[temp_history['spender_prof']],2)
        return temp_history, event
    
    def baby_life(self,max_age = None):### to test
        self.born()
        self.one_age_range_life("Baby", max_age)

    def baby_life_one_year(self,temp_history = None):
        return temp_history, "Baby - Aged Up"

    def one_age_range_life(self, age_range:str, max_age = None):

        max_age = self.max_age_check(age_range, max_age)
        for _ in range(AGE_RANGES[age_range][0],max_age+1):
            self.age_up()

    def born(self):
        temp_history = self.history_df.iloc[0].copy() ### get the first history of the person when it was created but not necessarily their are a baby
        temp_history['year'] = temp_history['year'] - temp_history['age'] 
        temp_history['age'] = 0
        self.update_history(new_history = temp_history, event="Born")

    def temp_age_up(self, temp_history = None):
        if temp_history is None:
            temp_history = self.history_df.iloc[-1].copy()
        
        temp_history['year'] += 1
        temp_history['age'] += 1
        temp_history['age_range'] = self.update_age_range(temp_history['age'])
        return temp_history

    def age_up(self):
        ### check current age range and age one year for that age range
        temp_history = self.history_df.iloc[-1].copy()
        print(temp_history)
        age_range = temp_history['age_range']
        
        print(age_range, temp_history['age'], " age up function start")
        temp_history = self.temp_age_up(temp_history)
        age_range = temp_history['age_range']

        
        if age_range == "Baby":
            temp_history,event = self.baby_life_one_year(temp_history)
        elif age_range == "Child":
            temp_history,event = self.child_life_one_year(temp_history)
        elif age_range == "Teenager":
            temp_history,event = self.teenager_life_one_year(temp_history)
        elif age_range == "Young Adult":
            temp_history,event = self.young_adult_one_year(temp_history)
        elif age_range == "Adult":
            pass
            #temp_history,event = self.adult_one_year(temp_history)
        elif age_range == "Elder":
            pass
            #temp_history,event =  self.elder_one_year(temp_history)
        print(age_range, self.history_df.iloc[-1]['age'], " age up function end", event)
        self.update_history(new_history = temp_history, event=event)
### if person temp_history['age'] is > baby age range, generate the first event a
# %%
