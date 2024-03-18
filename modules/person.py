import numpy as np
import pandas as pd

from  modules.gml_constants import (MALE_FIRST_NAMES, FEMALE_FIRST_NAMES, LAST_NAMES, 
                            GENDER_PROBS,SPENDER_PROFILE_PROBS,
                            AGE_RANGES, PART_TIME_JOB_PROB,                           
                            YEARS_OF_STUDY, TUITION, SPENDER_PROFILE,
                            INITIAL_INCOME_RANGES,
                            FUTURE_CAREER_PAY_PROBS,STUDENT_LOAN_INTEREST_RATES,
                            RAISE_DICT, DEATH_PROB_MODEL_COEF,CRIT_ILL_DEATH_PROB_MODEL_COEF)
                            # CAR_FINANCING_OPTION_PROBS,CAR_MAX_DEBT_RATIO,
                            # CAR_DOWNPAYMENT_CONSTANT,CAR_SELF_FINANCING_CONSTANT)
### ignore future warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
 
### add logging to the project
from logging import getLogger

import random
from datetime import date
### import timestamp
from time import time
### create a timestamp value
#timestamp = date.today().strftime("%Y-%m-%d")

logger = getLogger(__name__)

class Person_Functions():

    def __init__(self, gender:str =None, first_name = None, last_name = None, 
                      current_year = None, age_range: str = None, age: int = None,
                      career: str = None, future_career: str = None, income: int = None,
                      loan: int = None, loan_term: int = None, balance: int = None,
                      married: bool = False, just_married = False, children: int = 0, spender_prof: str = None,
                      death: bool = False,
                      parent_name_id_A: str = None, parent_name_id_B: str = None, children_name_id:list = [],

                      spouse_name_id: str = None,
                      years_of_study: int = None,
                      years_to_study: int = None,
                      has_a_car: bool = False,
                      history_df = None):
        
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
        ### timestamp with seconds
        self.time_stamp = round(time(),3)#.strftime("%Y-%m-%d %H:%M:%S")
        self.spouse_name_id = spouse_name_id
        self.has_a_car = has_a_car
        self.parent_name_id_A = parent_name_id_A
        self.parent_name_id_B = parent_name_id_B
        self.children_name_id = children_name_id
        self.death = death


        # Initialize the history DataFrame
        key_and_values = self.get_values()
        if history_df is not None:
            self.history_df = history_df
        else:
            self.history_df = pd.DataFrame(key_and_values.values(), index=key_and_values.keys()).T

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

    def max_age_check(self, age_range:str, max_age= None):
            """Check and return the maximum age for a given age range.

            Args:
                age_range (str): The age range to check.
                max_age (int, optional): The maximum age to compare. Defaults to None.

            Returns:
                int: The maximum age for the given age range.
            """
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

    def update_history(self,  event:str, new_history=None, death = False):
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
        new_history_df["death"] = death
        new_history_df["time_stamp"] = round(time(),3)#.strftime("%Y-%m-%d %H:%M:%S")
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
        if loan_term is None or loan_term == 0:
            loan_term = YEARS_OF_STUDY[future_career]+8

        # Subtract tuition from balance
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
        if temp_history['years_of_study'] == None:
            temp_history['years_of_study'] = 0
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
        if temp_history['future_career'] == None and temp_history['career'] in ["Pocket Money", "Part Time"]:
            temp_history['future_career'] = np.random.choice( list(FUTURE_CAREER_PAY_PROBS.keys()), 
                                         p=np.array(list(FUTURE_CAREER_PAY_PROBS.values())))
        elif temp_history['future_career'] == None and temp_history['career'] not in ["Pocket Money", "Part Time"]:
            return "Young Adult - Aged Up", temp_history

        event = "Young Adult - Finished Studies"
        temp_history['career'] = temp_history['future_career']
        temp_history['future_career'] = None
        temp_history['years_of_study'] = YEARS_OF_STUDY[temp_history['career']]
        temp_history['years_to_study'] = 0
        new_income = abs(np.random.choice(INITIAL_INCOME_RANGES[temp_history['career']]))
        temp_history['income'] = new_income
        return event, temp_history

    @staticmethod
    def update_income_to_balance(temp_history):
        if type(temp_history['balance']) is str:
            pass
        if temp_history['balance'] is None:
            temp_history['balance'] = 0
        income = temp_history['income']
        spender_prof = temp_history['spender_prof']
        temp_history['balance'] += income - income * SPENDER_PROFILE[spender_prof]
        return temp_history

    @staticmethod
    def handle_pocket_money(temp_history):
        temp_history['career'] = "Pocket Money"
        base_income = INITIAL_INCOME_RANGES['Pocket Money'][0]
        std_deviation = INITIAL_INCOME_RANGES['Pocket Money'][1]

        pocket_money = np.abs(np.round(np.random.normal(base_income, std_deviation), 2))
        temp_history['income'] = pocket_money

        return temp_history
    
    @staticmethod
    def set_spender_profile():
        spender_profile = np.random.choice( list(SPENDER_PROFILE_PROBS.keys()), 
                                         p=np.array(list(SPENDER_PROFILE_PROBS.values())))
        return spender_profile

    @staticmethod
    def get_a_raise(current_salary, career_path):

        ### raise chance
        raise_prob = RAISE_DICT[career_path]["chance"]
        raise_event = np.random.uniform(0,1)

        if raise_event <= raise_prob:

            hike_range = RAISE_DICT[career_path]["hike_range"]
            random_rate = np.random.uniform(hike_range[0], hike_range[1])
            new_salary = round(current_salary + current_salary*random_rate,2)
            event = "Got a Raise"
        else:
            ### raise amount
            new_salary = round(current_salary,2)
            
            event = "No Raise"

        return new_salary, event

    @staticmethod 
    def calculate_death_chance(age,gender):
        if gender == "Male":
            gender_val =  0
        elif gender == "Female":
            gender_val = 1
        else:
            gender_val = gender

        pred_lin = DEATH_PROB_MODEL_COEF['lin_reg']['age']*age*0.75 +\
                DEATH_PROB_MODEL_COEF['lin_reg']['gender']*gender_val +\
                DEATH_PROB_MODEL_COEF['lin_reg']['intercept']

        pred_log2 = DEATH_PROB_MODEL_COEF['lin_reg_log']['age']*age +\
                    DEATH_PROB_MODEL_COEF['lin_reg_log']['gender']*gender_val +\
                    DEATH_PROB_MODEL_COEF['lin_reg_log']['lin_pred']*pred_lin +\
                    DEATH_PROB_MODEL_COEF['lin_reg']['intercept']
        
        pred_log2_final = np.power(2,pred_log2)

        if pred_lin > 1:
            output_a = 1
        else:
            output_a = pred_lin

        if pred_log2_final > 1:
            output_b = 1
        else:
            output_b = pred_log2_final

        if age > 55:
            return 1 - output_b - 0.2

        else:
            return 1 - output_a - 0.08

    @staticmethod
    def calculate_death_chance_crit_ill(age):
        prob = CRIT_ILL_DEATH_PROB_MODEL_COEF['age']*age +\
                CRIT_ILL_DEATH_PROB_MODEL_COEF['age_sq']*age**2 +\
                CRIT_ILL_DEATH_PROB_MODEL_COEF['age_cub']*age**3 +\
                CRIT_ILL_DEATH_PROB_MODEL_COEF['age_qd']*age**4 +\
                CRIT_ILL_DEATH_PROB_MODEL_COEF['intercept']
        if age <20:
            prob = 0
        elif age >=20 and age < 40:
            prob = np.abs(prob)/5

        elif age >=40 and age < 55:
            prob = np.abs(prob)/3

        elif age >=55 and age < 60:
            prob = np.abs(prob)

        return prob

    def update_values(self, temp_history):
        """Update the person's attributes with new values."""
        for col in temp_history.index:
            ### check if the column is in the object
            if col in self.__dict__.keys():
                setattr(self, col, temp_history[col])

    # @staticmethod
    # def get_a_car(temp_history, finance_option):
    #     age = temp_history['age']
    #     balance = temp_history['balance']
    #     income = temp_history['income']
    #     credit_profile = temp_history['spender_prof']
    #     loan = int(temp_history['loan'])
    #     downpayment_capability = balance - CAR_DOWNPAYMENT_CONSTANT 

    # # This function is just calculating the likelyhood of a person getting a car loan or not
    # #  We still need to modify it to update the current loan term and interest rate
    # # if we can get credit score, we can calculate it in financial institution. 
    # # once the person is married and has children,especilally if they are in the age range of 30 - 45 the logic needs to be modified

    #     def choose_finance_option():
    #         if finance_option is None:
    #             return np.random.choice(
    #                 list(CAR_FINANCING_OPTION_PROBS.keys()),
    #                 p=np.array(list(CAR_FINANCING_OPTION_PROBS.values()))
    #             )
    #         return finance_option

    #     def self_financing_eligibility():
    #         if balance >= CAR_SELF_FINANCING_CONSTANT[1] and income >= CAR_SELF_FINANCING_CONSTANT[2]:
    #             return "Bought a Car (Self-Financed)"
    #         if balance <= CAR_SELF_FINANCING_CONSTANT[0]:  # Modified balance condition
    #             return "Cannot Buy a Car (Insufficient Balance)"
    #         return "Cannot Buy a Car (Insufficient Income)"

    #     def car_loan_eligibility():
    #         if income == 0:
    #             debt_to_income_ratio = float('inf')
    #         else:
    #             debt_to_income_ratio = loan / income
 
    #         for _, bucket_dict in CAR_MAX_DEBT_RATIO.items():
    #             age_range = bucket_dict['Age Range']
    #             if age_range[0] <= age <= age_range[1]:
    #                 max_debt_ratio = bucket_dict['Max Debt to Income Ratio'][credit_profile]
    #                 break
    #         else:
    #             return "Car Loan Application Rejected (Age out of range, more than 75)"

    #         if debt_to_income_ratio <= max_debt_ratio and downpayment_capability >= 1000:   
    #             return "Bought a Car (Car Loan)"
    #         return "Car Loan Application Rejected"

    #     if age >= 18:
    #         finance_option = choose_finance_option()

    #         if finance_option == "Self-Financing":
    #             event = self_financing_eligibility()
    #         elif finance_option == "Car Loan":
    #             event = car_loan_eligibility()
    #     else:
    #         event = "Not Eligible to Buy a Car (Age Restriction)"

    #     return event
      

class Person_Life(Person_Functions):
    def __init__(self, gender:str = None, first_name:str = None, last_name:str = None, 
                 current_year:int = None, age_range: str = None, age: int = None, 
                 career: str = None, future_career: str = None, income: float = None,
                loan: float = None, loan_term: int = None, balance: float = None,
                married: bool = False, parent_name_id_A: str = None, parent_name_id_B: str = None,
                spouse_name_id: str = None, years_of_study: int = None, years_to_study: int = None,
                has_a_car: bool = False, death: bool = False, children_name_id:list = []):
        
        ### call the parent class to initialize the person attributes
        super().__init__( gender = gender, first_name = first_name, last_name = last_name,
                        current_year = current_year, age_range = age_range, age = age, 
                        career = career, future_career = future_career, income = income,
                        loan = loan, loan_term = loan_term, balance = balance,married = married, 
                        parent_name_id_A = parent_name_id_A, parent_name_id_B = parent_name_id_B,
                        spouse_name_id = spouse_name_id, years_of_study = years_of_study, 
                        years_to_study = years_to_study,
                        has_a_car = has_a_car, death = death, children_name_id = children_name_id)

    ### there will be two main scenarios:
    # - the person is a recent born from a couple and just ages up
    # - the person was randomly generated and has a random age and we would need to know previous events from the past and then age up
    ### every time a person ages up, we need to update the history and check if the age range has changed
    ### if a person is created straight ahead as an elder then we need to create adult, teenager, child, baby classes and update their history
    ### if a person is created straight ahead as an working adult then we need to create child and teenager,child, baby classes and update their history
    ### if a person is created straight ahead as an teenager then we need to create child and baby classes and update their history
    ### if a person is created straight ahead as an child then we need to create baby classes and update their history
    ### if a person is created straight ahead as an baby then we need to create baby classes and update their history

    def death_check(self, age, gender):
        ### add cause of death
        ### add probability of death based on age

        #This will probably be triggered by other functions maybe we have a percent chance on ageup() to trigger death based on factors like age, health 
        # and a complete random chance of like car accident or something

        death = False
        age_death = self.calculate_death_chance(age,gender)
        ci_death = self.calculate_death_chance_crit_ill(age)
        random_prob_unexpect = np.random.random()
        random_prob_severe_acc = np.random.random()
        random_prob_ci = np.random.random()
        random_prob_curvature = np.random.random()
        if age <= 1 and random_prob_unexpect <= 0.0045:
            event = "Death - Unexpected Infant Death"
            death = True
            logger.info(f"### Death - Unexpected Infant Death: prob_th:{0.0045} >= prob:{round(random_prob_unexpect,4)} - age{age}")

        elif random_prob_severe_acc <= 0.0001:
            event = "Death - Severe Accident"
            death = True
            logger.info(f"### Death - Severe Accident: prob_th:{0.0001} >= prob:{round(random_prob_severe_acc,4)} - age{age}")
        

        elif random_prob_ci <= ci_death:
            event = "Death - Critical Illness"
            death = True
            logger.info(f"### Death - Critical Illness: prob_th:{round(ci_death,2)} >= prob:{round(random_prob_ci,2)} - age{age}")
        
        elif random_prob_curvature <= age_death:
            event = "Death - Age Curvature"
            death = True
            logger.info(f"### Old Age Death Event: prob_th:{round(age_death,2)} >= prob:{round(random_prob_curvature,2)} - age{age}")
        
        else:
            event = ""
        
        return event, death

    def generate_past_events(self):
        ### check self.history_df.iloc[0] to get the last history of the person
        temp_history = self.history_df.iloc[0].copy()
        reference_year = temp_history['year']
        ### generate the past events of the person
        current_age = temp_history['age']
        for loop_age in range(0, current_age+1):
            if loop_age == 0:
                temp_history['year'] = reference_year - current_age
                temp_history['age'] = 0
                temp_history['age_range'] = "Baby"
                self.update_history(new_history = temp_history, event="Born")
            else:
                temp_history['year'] = (reference_year - current_age + loop_age)
                temp_history['age'] = loop_age
                temp_history['age_range'] = self.update_age_range(loop_age)
                death = self.age_up_one_year_any_life_stage(temp_history)

                if death:
                    break

    def age_up_one_year_any_life_stage(self, temp_history):
        event = "This is a test event - this should be overwritten by the function"
        death = temp_history["death"]
        if death:
            logger.info(f"### Death Event: {temp_history['event']}")
            return None

        temp_history['year'] += 1
        temp_history['age'] += 1
        age_range = temp_history['age_range'] = self.update_age_range(temp_history['age'])

        ### Stage 2: Check the age range and call the corresponding life_one_year function
        ## Stage 2.1: If age range is baby, then age up the baby
        if age_range == "Baby":
            ### Stage 2.2: If age range is baby, then update the event
            event = "Baby - Aged Up"

        ### Stage 2.2: If age range is child, then age up the child
        elif age_range == "Child":
            ### Stage 2.3: If child is age is the first year as a child, then update the event
            if temp_history['age'] == AGE_RANGES["Child"][0]:
                event = "Become Child"


            ### Stage 2.3: If child is age is 5 it is time to give them pocket money and set their spender profile
            elif temp_history['age'] == 5:
                event = "Children - First Pocket Money"
                temp_history['spender_prof'] = self.set_spender_profile()
                temp_history = self.handle_pocket_money(temp_history)
            ### Stage 2.4: If child is age is not the first year as a child, nor the year to give pocket money, then update the event
            else:
                event = "Children - Aged Up"

            ### Stage 2.5: If child is on pocket money, then update the balance
            if temp_history['career'] == "Pocket Money":
                if temp_history['balance'] is None and temp_history['income'] is None:
                    temp_history['balance'] = 0
                else:
                    temp_history = self.update_income_to_balance(temp_history)
        
        ### Stage 3: If age range is teenager, then age up the teenager
        elif age_range == "Teenager":

            ### Stage 3.1: If teenager is age is the first year as a teenager, then update the event
            if temp_history['age'] == AGE_RANGES["Teenager"][0]:
                event = "Become Teenager"

            ### Stage 3.2: If teenager is age is not the first year as a teenager, then update the event
            else:
                event, temp_history = self.handle_part_time_job(temp_history, mode="Teenager")
            ### Stage 3.3: If teenager is on pocket money or part time job, then update the balance 
            temp_history = self.update_income_to_balance(temp_history)
        
        ### Stage 4: If age range is young adult, then age up the young adult
        elif age_range == "Young Adult":
            ### Stage 4.1: If young adult is age is the first year as a young adult, then update the event

                
            if temp_history['age'] == AGE_RANGES['Young Adult'][0]:
                ### If first year as a young adult, then define study and future career, check if they will get a loan and get a part time job
                temp_history = self.define_study_and_fut_career(temp_history)
                event, temp_history = self.handle_part_time_job(temp_history, mode = "Young Adult")
                temp_history = self.handle_get_student_loan(temp_history)
                event = event.replace("Young Adult", "Become Young Adult")
      
            ### Stage 4.2: If young adult is age is not the first year as a young adult, then update the event
            else:
                ### Stage 4.2.1: Check if Completed Studies (if years to study is 0 then the person has completed studies)
                if temp_history['years_to_study'] == 0:
                    #### set future career to career and get first income from non part time job
                    event, temp_history = self.handle_finished_studies(temp_history)

                ### did not complete studies yet
                ### Stage 4.2.2: If the person did not complete studies yet, then update the years of study, get a part time job and check if they will get a loan
                elif temp_history['years_to_study'] == None:
                    pass
                else:
                    temp_history = self.update_years_of_study(temp_history)
                    event, temp_history = self.handle_part_time_job(temp_history, mode = "Teenager")
                    temp_history = self.handle_get_student_loan(temp_history)
            #event  =self.get_a_car(temp_history,car_prob)
            if temp_history['balance'] == None:
                pass
            else:
                temp_history = self.update_income_to_balance(temp_history)
            if temp_history['event'] == "Created":
                event = ""
        
        ### Stage 5: If age range is adult, then age up the adult
        elif age_range == "Adult":
            if temp_history['years_to_study'] == 0 and temp_history['career'] == "Part Time":
                event, temp_history = self.handle_finished_studies(temp_history)

            temp_history = self.update_income_to_balance(temp_history)
            event = "Adult - Aged Up"
            
        elif age_range == "Elder":
            temp_history = self.update_income_to_balance(temp_history)
            event = "Elder - Aged Up"

        if age_range in ["Young Adult", "Adult", "Elder"]:
            ### check if event variable exists
            if event is None:
                event = "Aged Up"
            if temp_history['income'] is None:
                pass
            else:
                temp_history['income'], raise_event = self.get_a_raise(temp_history['income'], temp_history['career'])
                event = event + " - " + raise_event

        ### Stage X: Check if the person will die
        death_event, death = self.death_check(temp_history['age'], temp_history["gender"])

        if death:
            event = death_event
            logger.info(f"### Death Event: {event}")                               
  
        self.update_history(new_history = temp_history, event=event, death=death)
        self.update_values(temp_history)
        return death
    
def create_person_from_dataframe(person_df):
    """Create a person from a DataFrame."""

    ### extract the person attributes from the dataframe
    history_df = person_df.copy()
    ### get max year
    max_year = history_df['year'].max()
    ### filter the dataframe to get the attributes of the person in the max year
    person_attributes = history_df[history_df['year'] == max_year].iloc[0]

    person = Person_Life(gender = person_attributes["gender"],
                        first_name = person_attributes["first_name"],
                        last_name = person_attributes["last_name"],
                        current_year = max_year,
                        age_range = person_attributes["age_range"],
                        age = person_attributes["age"],
                        career = person_attributes["career"],
                        future_career = person_attributes["future_career"],
                        income = person_attributes["income"],
                        loan = person_attributes["loan"],
                        loan_term = person_attributes["loan_term"],
                        balance = person_attributes["balance"],
                        married = person_attributes["married"],
                        parent_name_id_A = person_attributes["parent_name_id_A"],
                        parent_name_id_B = person_attributes["parent_name_id_B"],
                        spouse_name_id = person_attributes["spouse_name_id"],
                        years_of_study = person_attributes["years_of_study"],
                        years_to_study = person_attributes["years_to_study"],
                        has_a_car = person_attributes["has_a_car"],
                        death = person_attributes["death"],
                        children_name_id = person_attributes["children_name_id"],
                        history_df = history_df)
    return person
        
    