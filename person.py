import numpy as np
import pandas as pd

from  gml_constants import (MALE_FIRST_NAMES, FEMALE_FIRST_NAMES, LAST_NAMES, 
                            GENDER_PROBS,SPENDER_PROFILE_PROBS,
                            AGE_RANGES, PART_TIME_JOB_PROB,                           
                            YEARS_OF_STUDY, TUITION, SPENDER_PROFILE,
                            INITIAL_INCOME_RANGES,
                            FUTURE_CAREER_PAY_PROBS,STUDENT_LOAN_INTEREST_RATES,
                            CAR_FINANCING_OPTION_PROBS,CAR_MAX_DEBT_RATIO,
                            CAR_DOWNPAYMENT_CONSTANT,CAR_SELF_FINANCING_CONSTANT,
                            RAISE_CONSTANTS)

import random
from datetime import date

class Person_Functions():

    def __init__(self, gender:str =None, first_name = None, last_name = None, 
                      current_year = None, age_range: str = None, age: int = None,
                      career: str = None, future_career: str = None, income: int = None,
                      loan: int = None, loan_term: int = None, balance: int = None,
                      married: bool = False, just_married = False, children: int = 0, spender_prof: str = None,
                      parent_name_id_A: str = None, parent_name_id_B: str = None, children_name_id:list = [],

                      spouse_name_id: str = None,
                      years_of_study: int = None,
                      years_to_study: int = None,
                      has_a_car: bool = False, cause_of_death : str = None):
        
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
        - just_married: Marital event.
        - children: Number of children.
        - spender_prof: Spending profile.
        - years_of_study, years_to_study: Education attributes.

        """
        # Determine gender if not provided
        if gender is None:
            gender = np.random.choice( list(GENDER_PROBS.keys()),
                                       p=np.array(list(GENDER_PROBS.values())))
        self.gender = gender
        
        # Set names and generate a full name
        self.first_name = first_name
        self.last_name = last_name
        self.generate_full_name()

        # Generate a unique ID for the person
        self.unique_name_id = self.generate_unique_name_id()

        # Set the current year if not provided
        if current_year is None:
            current_year = date.today().year
        self.year = current_year

        # Determine the age range and specific age if not provided
        self.age_range, self.age = self.initial_age(age_range, age)
        # Set career attributes and life events     
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
        self.just_married = just_married
        self.children = children
        self.spender_prof = spender_prof
        self.event = "Created"
        self.spouse_name_id = spouse_name_id
        self.has_a_car = has_a_car
        self.parent_name_id_A = parent_name_id_A
        self.parent_name_id_B = parent_name_id_B
        self.children_name_id = children_name_id
        self.cause_of_death = cause_of_death


       

        # Initialize the history DataFrame
        self.history_df = pd.DataFrame([self.get_values()], index = [0])

    def get_values(self):
        """Return the current attributes of the person as a dictionary."""
        constants = {name: value for name, value in vars(self).items() if not callable(value)}
        return constants
    
    def generate_first_name(self):#
        """Generate a first name based on the person's gender."""
        if self.gender == "Female":
            name = random.choice(FEMALE_FIRST_NAMES)
        else:
            name = random.choice(MALE_FIRST_NAMES)
        return name

    def generate_full_name (self):#
        """Generate a full name for the person."""
        if self.last_name is None:
            self.last_name = random.choice(LAST_NAMES)
        if self.first_name is None:
            self.first_name = self.generate_first_name()
        self.full_name = self.first_name + " " + self.last_name

    def generate_unique_name_id(self):#
        """Generate a unique ID based on the person's name."""
        ### contains the first name, last name, and a random number between 0 and 1000 without spaces
        return self.first_name +"_"+ self.last_name +"_"+ str(random.randint(0, 10000))
    
    @staticmethod
    def update_age_range(age):#
        """Determine the age range based on a specific age."""
        for age_range, age_range_list in AGE_RANGES.items():
            if age_range_list[0] <= age <= age_range_list[1]:
                return age_range
    
    def initial_age(self, age_range=None, age = None):#
        """Determine the initial age and age range if not provided."""
        if age is not None:
            age_range = self.update_age_range(age)
        else:
            if age_range is None:
                age = np.random.randint(AGE_RANGES["Baby"][0], AGE_RANGES["Elder"][1])
                age_range = self.update_age_range(age)
            else:
                age = np.random.randint(AGE_RANGES[age_range][0], AGE_RANGES[age_range][1])
                age_range = age_range

        return age_range, age

    def max_age_check(self, age_range:str, max_age= None):#
        """Check and return the maximum age for a given age range."""
        create_max_age = self.history_df['event'] == "Created"
        age_range_check = self.history_df['age_range'] == age_range
        condition = create_max_age & age_range_check
        if condition.sum() >0:
            max_age = self.history_df[create_max_age & age_range_check]['age'].values[0]
        elif max_age is None or max_age > AGE_RANGES[age_range][1]:
            max_age = AGE_RANGES[age_range][1]
        else:
            max_age = max_age
        return max_age

    def update_history(self,  event:str, new_history=None):
        """Update the person's history with a new event."""
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
            
        new_history_df["unique_name_year_event_id"] = new_history_df["unique_name_id"] + "_" +\
                                          new_history_df["year"].astype(str) + "_" +\
                                          new_history_df["event"]
          
        self.history_df = pd.concat([self.history_df, new_history_df], ignore_index=True)

    @staticmethod
    def handle_part_time_job(temp_history, mode="Teenager"):
        if temp_history['career'] == "Pocket Money" and np.random.random() >= PART_TIME_JOB_PROB:
            temp_history['career'] = "Part Time"
            base_income = INITIAL_INCOME_RANGES['Part Time'][0]
            std_deviation = INITIAL_INCOME_RANGES['Part Time'][1]
            temp_history['income'] = np.round(np.random.normal(base_income, std_deviation), 2)
            return f"{mode} - Part Time Job", temp_history
        else:
            return f"{mode} - Aged Up", temp_history

    @staticmethod
    def student_loan(future_career, balance, loan, loan_term, interest_rate=None):### review this function
        """Calculate and update loan details based on tuition fees."""
        ### Tuition due
        tuition_due = TUITION[future_career]
        
        if interest_rate is None:
            interest_rate = random.uniform(STUDENT_LOAN_INTEREST_RATES[0], 
                                                STUDENT_LOAN_INTEREST_RATES[1])
        if loan_term is None:
            loan_term = YEARS_OF_STUDY[future_career]+8

        # Subtract tuition from balance
        print(tuition_due,balance)
        balance -= tuition_due

        if balance > 0:
            ### Student has enough money to pay for the tuition
            loan = 0
            loan_term = 0
        else:
            ### Student does not have enough money to pay for the tuition
            new_loan = abs(balance) * (1 + interest_rate)**(loan_term)
            ### check if loan exist and is not None
            if loan != 0 and loan is not None:
                loan += new_loan
            else:
                ### Student does not have loan and will need to get a loan on the remaining balance
                loan = new_loan
            balance = 0
            
        return loan, loan_term, interest_rate, balance

    def handle_get_student_loan(self, temp_history):
        pack = self.student_loan( temp_history['future_career'], temp_history['balance'],   
                                  temp_history['loan'], temp_history['loan_term'], temp_history['interest_rate'])
                                
        temp_history['loan'], temp_history['loan_term'], temp_history['interest_rate'], temp_history['balance'] = pack

        return temp_history
    
    @staticmethod
    def update_years_of_study(temp_history):
        temp_history['years_of_study'] += 1
        temp_history['years_to_study'] -= 1
        return temp_history

    @staticmethod
    def define_study_and_fut_career(temp_history):
        future_career = np.random.choice( list(FUTURE_CAREER_PAY_PROBS.keys()), 
                                         p=np.array(list(FUTURE_CAREER_PAY_PROBS.values())))
        temp_history['future_career'] = future_career
        temp_history['years_of_study'] = 0
        temp_history['years_to_study'] = YEARS_OF_STUDY[future_career]
        return temp_history

    @staticmethod
    def handle_finished_studies(temp_history):
      
        ###TEMP SOLUTION, IF TEMP_HISOTRY HAS NO FUTURE CAREER DEFINE ONE OTHERWISE WE GET AN ERROR###
        if temp_history['future_career'] == None:
            temp_history['future_career'] = np.random.choice( list(FUTURE_CAREER_PAY_PROBS.keys()), 
                                         p=np.array(list(FUTURE_CAREER_PAY_PROBS.values())))

        event = "Young Adult - Finished Studies"
        temp_history['career'] = temp_history['future_career']
        temp_history['future_career'] = None
        temp_history['years_of_study'] = YEARS_OF_STUDY[temp_history['career']]
        temp_history['years_to_study'] = 0
        new_income = abs(np.random.choice(INITIAL_INCOME_RANGES[temp_history['career']]))
        #month = 1/np.random.randint(1, 13)
        #temp_history['income'] = new_income*month + temp_history['income']*(1-month)
        return event, temp_history

    @staticmethod
    def update_income_to_balance(temp_history):
        print(type(temp_history['balance']), temp_history['age_range'], temp_history['age'])
        if type(temp_history['balance']) is str:
            print(temp_history['balance'])
        if temp_history['balance'] is None:
            temp_history['balance'] = 0
        income = temp_history['income']
        spender_prof = temp_history['spender_prof']
        temp_history['balance'] += income - income * SPENDER_PROFILE[spender_prof]
        return temp_history

    @staticmethod
    def handle_pocket_money(temp_history):
        print("Testing Pocket Money")
        print("Current Career", temp_history['career'])
        temp_history['career'] = "Pocket Money"
        print("Current Career After", temp_history['career'])
        base_income = INITIAL_INCOME_RANGES['Pocket Money'][0]
        std_deviation = INITIAL_INCOME_RANGES['Pocket Money'][1]
        temp_history['income'] = np.round(np.random.normal(base_income, std_deviation), 2)
        print( INITIAL_INCOME_RANGES['Pocket Money'][0],
                INITIAL_INCOME_RANGES['Pocket Money'][1],
                np.round(np.random.normal(base_income, std_deviation), 2))
        return temp_history
    
    @staticmethod
    def set_spender_profile():
        spender_profile = np.random.choice( list(SPENDER_PROFILE_PROBS.keys()), 
                                         p=np.array(list(SPENDER_PROFILE_PROBS.values())))
        return spender_profile


    @staticmethod
    def get_a_car(temp_history, finance_option):
        age = temp_history['age']
        balance = temp_history['balance']
        income = temp_history['income']
        credit_profile = temp_history['spender_prof']
        loan = int(temp_history['loan'])
        downpayment_capability = balance - CAR_DOWNPAYMENT_CONSTANT 

    # This function is just calculating the likelyhood of a person getting a car loan or not
    #  We still need to modify it to update the current loan term and interest rate
    # if we can get credit score, we can calculate it in financial institution. 
    # once the person is married and has children,especilally if they are in the age range of 30 - 45 the logic needs to be modified

        def choose_finance_option():
            if finance_option is None:
                return np.random.choice(
                    list(CAR_FINANCING_OPTION_PROBS.keys()),
                    p=np.array(list(CAR_FINANCING_OPTION_PROBS.values()))
                )
            return finance_option

        def self_financing_eligibility():
            if balance >= CAR_SELF_FINANCING_CONSTANT[1] and income >= CAR_SELF_FINANCING_CONSTANT[2]:
                return "Bought a Car (Self-Financed)"
            if balance <= CAR_SELF_FINANCING_CONSTANT[0]:  # Modified balance condition
                return "Cannot Buy a Car (Insufficient Balance)"
            return "Cannot Buy a Car (Insufficient Income)"

        def car_loan_eligibility():
            if income == 0:
                debt_to_income_ratio = float('inf')
            else:
                debt_to_income_ratio = loan / income
 
            for _, bucket_dict in CAR_MAX_DEBT_RATIO.items():
                age_range = bucket_dict['Age Range']
                if age_range[0] <= age <= age_range[1]:
                    max_debt_ratio = bucket_dict['Max Debt Ratio'][credit_profile]
                    break
            else:
                return "Car Loan Application Rejected (Age out of range, more than 75)"

            if debt_to_income_ratio <= max_debt_ratio and downpayment_capability >= 1000:   
                return "Bought a Car (Car Loan)"
            return "Car Loan Application Rejected"

        if age >= 18:
            finance_option = choose_finance_option()

            if finance_option == "Self-Financing":
                event = self_financing_eligibility()
            elif finance_option == "Car Loan":
                event = car_loan_eligibility()
        else:
            event = "Not Eligible to Buy a Car (Age Restriction)"

        return event
      

class Person_Life(Person_Functions):
    def __init__(self, gender:str =None, first_name:str = None, last_name:str = None, 
                 current_year:int = None, age_range: str = None, married: bool = False, ):

        super().__init__(gender, first_name, last_name, current_year, age_range, career=None, income=None, 
                         loan=None, loan_term=None, balance=None, married=married)
    @staticmethod    
    def get_a_car(temp_history,finance_option):
        # replace the constants with a variable coming from gml_constants
        if temp_history['age'] >= 18:
            
            if finance_option is None:
                finance_option = np.random.choice(list(CAR_FINANCING_OPTION_PROBS.keys()), 
                                         p=np.array(list(CAR_FINANCING_OPTION_PROBS.values())))
            
            if finance_option == "Self-Financing":
                if temp_history['balance'] >= 2000 and temp_history['income'] >= 70000:  
                    event="Bought a Car (Self-Financed)"
                else:
                    event="Cannot Buy a Car (Insufficient Balance)"
            
            elif finance_option == "Car Loan":

                debt_to_income_ratio = temp_history['loan'] / (temp_history['income'])  # Assuming monthly income

                if debt_to_income_ratio <= 0.5:  # Adjust the threshold as needed
                    event="Bought a Car (Car Loan)"
                else:
                    event="Car Loan Application Rejected"
        else:
            event="Not Eligible to Buy a Car (Age Restriction)"
        
        return event

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


    ###What do we have to do in this death function?

    #Add a column to the city history that keeps track of if that person is alive or not

    #Add a column to the person history that keeps track of cause of death (sort of like an event)

    #Add a column to the person history that keeps track of if that person is alive or not


    #Update the death value for both the city and the person


    def death(self, cause):
        ### add cause of death
        ### add probability of death based on age

            #This will probably be triggered by other functions maybe we have a percent chance on ageup() to trigger death based on factors like age, health 
            # and a complete random chance of like car accident or something

        ### ???

        
        if cause == "Critical Illness":

            self.history_df['cause_of_death'] = "Critcal Illness"
            
        elif cause == "Old Age":

            self.history_df['cause_of_death'] = "Old Age"

        elif cause == "Severe Accident":

            self.history_df['cause_of_death'] = "Severe Accident"
        else:
            pass
            



        





    

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

    def young_adult(self, max_age):
        self.teenager_life(max_age)
        self.one_age_range_life("Young Adult")

        ### life events
        ### will go to college/university (OK)
        ### will get a loan (OK)
        ### will get a job (OK)
        ### may get married (OK)
        ### may have children (In progress)
        ### may get a house
        pass


    def young_adult_one_year(self, temp_history = None,car_prob = None):

        #### First year Check
        if temp_history['age'] == AGE_RANGES['Young Adult'][0]:
            ### First year as a young adult
            temp_history = self.define_study_and_fut_career(temp_history)
            event, temp_history = self.handle_part_time_job(temp_history, mode = "Young Adult")
            temp_history = self.handle_get_student_loan(temp_history)
            event = event.replace("Young Adult", "Become Young Adult")
            
        ### Not first year as a young adult
        else:
           ### Check if Completed Studies
           if temp_history['years_to_study'] == 0:
               #### set future career to career and get first income from non part time job

               event, temp_history = self.handle_finished_studies(temp_history)

               ### pay student loan
               #temp_history = self.handle_pay_student_loan(temp_history) ### to be developed

           ### did not complete studies yet
           else:
                temp_history = self.update_years_of_study(temp_history)
                event, temp_history = self.handle_part_time_job(temp_history, mode = "Teenager")
                temp_history = self.handle_get_student_loan(temp_history)
        event  =self.get_a_car(temp_history,car_prob)
        temp_history = self.update_income_to_balance(temp_history)

        return temp_history, event

    def teenager_life(self, max_age=None):
        self.child_life(max_age= AGE_RANGES["Child"][1])
        self.one_age_range_life("Teenager", max_age)

    def teenager_life_one_year(self, temp_history = None):
        if temp_history['age'] == AGE_RANGES["Teenager"][0]:
            event = "Become Teenager"

        else:
            event, temp_history = self.handle_part_time_job(temp_history, mode="Teenager")

        temp_history = self.update_income_to_balance(temp_history)

        return temp_history, event

    def child_life(self,max_age = None):
        self.baby_life(max_age= AGE_RANGES["Baby"][1])
        self.one_age_range_life("Child", max_age)

    def child_life_one_year(self, temp_history = None):

        if temp_history['age'] == AGE_RANGES["Child"][0]:
            event = "Become Child"

        elif temp_history['age'] == 5:
            event = "Children - First Pocket Money"
            temp_history['spender_prof'] = self.set_spender_profile()
            temp_history = self.handle_pocket_money(temp_history)
        else:
            event = "Children - Aged Up"

        if temp_history['career'] == "Pocket Money":
            if temp_history['balance'] is None and temp_history['income'] is None:
                temp_history['balance'] = 0
            else:
                temp_history = self.update_income_to_balance(temp_history)
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
        ### Also update the objects values not just their history
        self.age += 1
        self.age_range = self.update_age_range(temp_history['age'])

        return temp_history

    def age_up(self):
        ### check current age range and age one year for that age range
        temp_history = self.history_df.iloc[-1].copy()
        age_range = temp_history['age_range']
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
        #print(age_range, self.history_df.iloc[-1]['age'], " age up function end", event)
        self.update_history(new_history = temp_history, event=event)

    def age_group_up(self, age_range, max_age = None):
        max_age = self.max_age_check(age_range, max_age)
        if age_range == "Baby":
            self.baby_life(max_age = max_age)
        elif age_range == "Child":
            self.child_life(max_age = max_age)
        elif age_range == "Teenager":
            self.teenager_life(max_age = max_age)
        elif age_range == "Young Adult":
            self.young_adult(max_age = max_age)
        elif age_range == "Adult":
            pass
            #self.adult(max_age = max_age)
        elif age_range == "Elder":
            pass
            #self.elder(max_age = max_age)



    def got_promotion_salary_hike(temp_history):

        age = temp_history['age']
        career_path = temp_history['future_career']
        job_type = temp_history['INITIAL_INCOME_RANGES']

        if job_type != "Part Time" and job_type != "Pocket Money":
            for age_range in RAISE_CONSTANTS.keys():
                if age_range[0] <= age <= age_range[1]:
                    
                    for career in RAISE_CONSTANTS[age_range].keys():
                        if career == career_path:
                            chance = RAISE_CONSTANTS[age_range][career]['chance']
                            hike = RAISE_CONSTANTS[age_range][career]['hike']
                            if np.random.random() <= chance:
                                temp_history['income'] = temp_history['income'] * (1+hike)
                                event = f"Got a Promotion and Salary Hike of ({hike*100}%)"
                                return temp_history , event
                            else:
                                event = "No Promotion"
                                return temp_history , event
                        else:
                            pass
        else:
            event = "Not Eligible for Promotion or Salary Hike due to Job Type"
            return temp_history , event
  


