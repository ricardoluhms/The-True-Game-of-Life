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
                            CAREERS_AND_MARRIAGE_PROBS,MIN_MARRIAGE_ALLOWED_AGE, SAME_GENDER_MARRIAGE_RATIO,CAR_FINANCING_OPTION_PROBS)

#from  gml_constants import *
import random
from datetime import date

#%%
class City():
  
    ### create a city with a name and a population of young adults 
    def __init__(self, name:str, population:int, current_year:int = 1950, finance_institution = None):
        """ City class is used to create a city with a name and a population of young adults.
            inputs:
            - name: the name of the city (as a string)
            - population: the population of the city (as an integer)
            - current_year: the current year of the city (as an integer)
            outputs:
            - None
        """
        self.event = "Created"
        self.city_name = name
        self.population = population
        self.current_year = current_year
        self.young_adults = []
        self.history = pd.DataFrame()
        self.financial_institution = finance_institution
        self.people_obj_dict = self.generate_young_adults(population)
        ### explain what City class does and the inputs, outputs and attributes


    def age_up(self):
        self.current_year += 1
        ### 
        for person_id in self.people_obj_dict.keys():
            person_obj = self.people_obj_dict[person_id]
            person_obj.age_up()
            
            ### updating city history with each person history avoiding duplicates
            current_history = person_obj.history_df
            self.history = pd.concat([self.history, current_history], ignore_index=True)
            self.history.drop_duplicates(subset=['unique_name_year_event_id'], keep='last', inplace=True)
            ### overwriting the person in people_obj_dict with the updated person
            self.people_obj_dict[person_id] = person_obj
            ### check current history, if there is a marriage, check person id is in the city history
            ### Placeholder for marriage function
            self.handle_marriage(person_obj)
            ### Placeholder for child born function

    
    def generate_young_adults(self, population:int = None):
        # make a even distribution of gender
        people_list = {}
        if population is None:
            population = 1
        for _ in range(self.population):
            current_person = Person_Life(age_range='Young Adult', current_year=self.current_year)

            ### a random max age to a teenager
            max_age = np.random.randint(AGE_RANGES['Teenager'][0],AGE_RANGES['Teenager'][1])

            current_person.teenager_life(max_age)
            ### retrieve the last history of the person and the unique_name_id
            temp_history = current_person.history_df.iloc[-1].copy()
            unique_name_id = temp_history['unique_name_id']
            people_list[unique_name_id] = current_person
        
        return people_list


    def retrieve_history_from_people(self): ### will be deprecated in the future
        for person in self.people:
            self.history.extend(person.retrieve_history())


    def calculate_marriage_cost(self, fixed_guests: int = None): ### being developed
        # Average cost per person - Move value to constants in the future - to be developed
        avg_cost_per_person = 34000 / 100  # assuming average 100 guests
        
        if fixed_guests is not None:
            guests = fixed_guests
        else:
            # Randomize number of guests, more concentrated on 50 to 100
            guests = np.random.normal(loc=75, scale=20).astype(int)
            guests = np.clip(guests, 25, 300)
            
        # Calculate cost based on random additional percentage up to 40%
        additional_percentage = np.random.uniform(0, 0.4)
        cost_per_person = avg_cost_per_person * (1 + additional_percentage)
        total_cost = guests * cost_per_person
        
        return guests, total_cost


    def handle_marriage(self, person):
        # retrieve the last history of the person and:
        person_last_history = person.history_df.iloc[-1].copy()

        ### check current employment status to retrieve the marriage probability
        career_crit_chance = CAREERS_AND_MARRIAGE_PROBS[person_last_history['career']] ### test for all careers later - to be developed
        
        ### check if the person is old enough to get married and is not married
        age_cri = person_last_history["age"] >= MIN_MARRIAGE_ALLOWED_AGE
        married_cri = person_last_history["married"] == False
        prob_cri = np.random.random() < career_crit_chance

        ### FOR TESTING MARRIAGE
        prob_cri = True

        ### Based on the career of the person, check if the person will get married
        if age_cri and married_cri and prob_cri:
            # 1st - get the gender of the person to be married & check what will be gender of the spouse
            person_gender =  person_last_history['gender']
            if person_gender == "Male":
                spouse_gender = 'Female' if np.random.random() < (1 - SAME_GENDER_MARRIAGE_RATIO) else 'Male'
            else:
                spouse_gender = 'Male' if np.random.random() < (1 - SAME_GENDER_MARRIAGE_RATIO) else 'Female'
            # 2nd - check if exist spouse candidate in the city:`
            person_age = person_last_history['age']
            person_most_recent_year = person_last_history['year']
            all_population = self.history.copy()
            # - is not married and; 
            # - is not the person itself in the city and;
            # - is within +- 5 years of the person age and;
            # - has the gender defined for the spouse and;
            # - has the age to get married
            # - must be the information on the same year as the person
            is_married = all_population['married'] == False
            is_not_person = all_population['unique_name_id'] != person_last_history['unique_name_id']
            is_age_range = (all_population['age'] >= person_age - 5) & (all_population['age'] <= person_age + 5)
            is_gender = all_population['gender'] == spouse_gender
            is_age_to_get_married = all_population['age'] >= MIN_MARRIAGE_ALLOWED_AGE
            is_same_year = all_population['year'] == person_most_recent_year
            marriage_criteria = is_married & is_not_person & is_age_range & is_gender & is_age_to_get_married & is_same_year

            if marriage_criteria.sum() > 0:
                # retrieve the spouse candidate from the city
                spouse_id = all_population[marriage_criteria].sample(1).iloc[0].copy()['unique_name_id'] ### select on from the list
                spouse = self.people_obj_dict[spouse_id]
                spouse_last_history = spouse.history_df.iloc[-1].copy()
                ### quick error check to see if the last history is the same year as the person - else solve the issue
                if spouse_last_history['year'] != person_last_history['year']:
                    ### solve the issue
                    print('Solve the issue - Last history of the spouse candidate is not the same year as the person which means there is a problem with the current logic')
                    pass
                # - change the married status to True
                spouse_last_history['married'] = True
                # - change the just_married status to True
                spouse_last_history['just_married'] = True
                # - change the spouse_name_id to the person unique_name_id
                spouse_last_history['spouse_name_id'] = person_last_history['unique_name_id']
                # the person last history:
                # - change the spouse_name_id to the spouse unique_name_id
                person.history_df.iloc[-1, 'spouse_name_id'] = spouse_last_history['unique_name_id']
                # update the history of the person and the spouse candidate
                #person.update_history(new_history=person_last_history) 
                #### FUTURE ISSUES TO SOLVE:
                # - IF THE PERSON CURRENT YEAR WAS NOT UPDATED YET SO THE PERSON WILL NOT BE A CANIDATE FOR MARRIAGE
                # - UPDATE HISTORY ISSUE - A SPOUSE CANDIDATE HAS THE CURRENT HISTORY APPENDED TO THE PERSON HISTORY AND CITY HISTORY BUT THEY SHOULD BE UPDATED IN BOTH

            else:
                # if there is no spouse candidate, then create a new person and get married
                # get a random age between the minimum age to get married and the maximum age to get married 
                # get the age range based on the age
                # create a new person with the age range and the current year
                
                if person_age - 5 < MIN_MARRIAGE_ALLOWED_AGE:
                    spouse_min_age = MIN_MARRIAGE_ALLOWED_AGE
                else:
                    spouse_min_age = person_age - 5
                
                spouse_age = np.random.randint(spouse_min_age, person_age + 5)
                ### get the age range based on the age
                spouse_age_range = Person_Life.update_age_range(spouse_age) ### TO BE DEVELOPED - SKIP AGE RANGE TO REPLACE WITH THE AGE WHEN CREATING A NEW PERSON
                spouse = Person_Life(gender= spouse_gender, age_range= spouse_age_range, current_year= person_most_recent_year, married = True)
                spouse.age_group_up(age_range=spouse_age_range, max_age=spouse_age) ### TO BE DEVELOPED - when creating a new person and age up for marriage set married to True
                ### married to true will be applied to all the history of the person so it need to be removed from the history later
                spouse_all_history = spouse.history_df.copy()
                criteria_arange = spouse_all_history["age_range"] == spouse_age_range
                criteria_age = spouse_all_history["age"] == spouse_age
                criteria_year = spouse_all_history["year"] == person_most_recent_year
                spouse_all_history.iloc[~(criteria_arange & criteria_age & criteria_year),"married"] = False
                spouse_all_history.iloc[(criteria_arange & criteria_age & criteria_year),"just_married"] = True
                spouse_all_history.iloc[(criteria_arange & criteria_age & criteria_year),"spouse_name_id"] = person_last_history['unique_name_id']
                spouse.history_df = spouse_all_history

                self.people_obj_dict[spouse.unique_name_id] = spouse

            ### TO BE DEVELOPED ###
            # # check if the person has enough money to get married    
            # _, marriage_expense = self.calculate_marriage_cost() ### to be developed
            # total_balance = person_last_history['balance'] + spouse_last_history['balance']
            # ### if the person does not have enough money, then check both person and spouse candidate can get a loan
            # if total_balance < marriage_expense:
            #     get_loan_status = self.get_loan(desired_loan_amount=marriage_expense-total_balance)
            #     if  get_loan_status is None:
            #         print('You cannot afford the marriage expense. You have reached the maximum loan amount.')
            pass


class Person_Functions():

    def __init__(self, gender:str =None, first_name = None, last_name = None, 
                      current_year = None, age_range: str = None,
                      career: str = None, future_career: str = None, income: int = None,
                      loan: int = None, loan_term: int = None, balance: int = None,
                      married: bool = False, just_married = False, children: int = 0, spender_prof: str = None,
                      spouse_name_id: str = None,
                      years_of_study: int = None,
                      years_to_study: int = None,
                      has_a_car: bool = False):
        
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
        self.age_range, self.age = self.initial_age(age_range)

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

        # Initialize the history DataFrame
        self.history_df = pd.DataFrame(self.get_values(), index=[0])

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
    
    def initial_age(self, age_range=None):#
        """Determine the initial age and age range if not provided."""
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

    # This function is just calculating the likelyhood of a person getting a car loan or not
    #  We still need to modify it to update the current loan term and interest rate
    
    def car_loan(spender_prof , balance, loan, income, age):

        '''since we do not have information on credit score we can use Spender profile as a parameter a big 
              spender will have less likelyhood to get a car loan.
           # We can use income and balance here also to determine the chances of getting a car
           # the lower the age the lesser are the chances of a person to get a car loan 
           # we need to check the downpayment made by the user, for instance for a car worth 30K
                we need atleast 10 - 20 percent downpayment.'''

        credit_profile  = spender_prof
        downpayment_capability = balance * 0.10
        debt_to_income_ratio = loan / income
        person_age = age

        if person_age >= 18 and person_age <= 22:

            if credit_profile == "Big Spender":
                if debt_to_income_ratio <= 0.8:
                    if downpayment_capability >= 3000:
                        event="Bought a Car (Car Loan)"
                    else:
                        event="Car Loan Application Rejected"

            if credit_profile == "Average":
                if debt_to_income_ratio <= 0.5:
                    if downpayment_capability >= 3000:
                        event="Bought a Car (Car Loan)"
                    else:
                        event="Car Loan Application Rejected"
            else:
                if debt_to_income_ratio <= 0.4:
                    if downpayment_capability >= 3000:
                        event="Bought a Car (Car Loan)"
                    else:
                        event="Car Loan Application Rejected"

        if person_age >= 23 and person_age <= 30:

            if credit_profile == "Big Spender":
                if debt_to_income_ratio <= 0.6:
                    if downpayment_capability >= 3000:
                        event="Bought a Car (Car Loan)"
                    else:
                        event="Car Loan Application Rejected"

            if credit_profile == "Average":
                if debt_to_income_ratio <= 0.4:
                    if downpayment_capability >= 3000:
                        event="Bought a Car (Car Loan)"
                    else:
                        event="Car Loan Application Rejected"
            else:
                if debt_to_income_ratio <= 0.3:
                    if downpayment_capability >= 3000:
                        event="Bought a Car (Car Loan)"
                    else:
                        event="Car Loan Application Rejected"

        return event
    
    @staticmethod    
    def get_a_car(temp_history,finance_option): # currently this function is working for a brand new car, whereas in most of the cases a Young adult will go for a second hand car.
        # replace the constants with a variable coming from gml_constants
        if temp_history['age'] >= 18:
            
            if finance_option is None:
                finance_option = np.random.choice(list(CAR_FINANCING_OPTION_PROBS.keys()), 
                                         p=np.array(list(CAR_FINANCING_OPTION_PROBS.values())))

            # If a person is self-financing, we will check if he/she has sufficient balance and income. 
            # If either of these things is missing,we will explain why they are unable to buy the car at this moment.

            if finance_option == "Self-Financing":
                if temp_history['balance'] >= 20000.000 and temp_history['income'] >= 70000.000:  
                    event="Bought a Car (Self-Financed)"
                else:
                    if temp_history['balance'] <= 2000.000:
                        event="Cannot Buy a Car (Insufficient Balance)"
                    else:
                        event="Cannot Buy a Car (Insufficient Income)"

            elif finance_option == "Car Loan":
                  event = car_loan(temp_history['spender_prof'],temp_history['balance'],
                                        temp_history['income'],temp_history['age'])
        else:
            event="Not Eligible to Buy a Car (Age Restriction)"
        
        return event

notes =  True 
if notes:
    ### Generate a class Person that keeps track of multiple Classes such as Baby, Child, Teenager, Young Adult, Adult, Elder
    ### if the baby ages up to a child, then the baby class is deleted and a child class is created using the baby class attributes
    ### if the child ages up to a teenager, then the child class is deleted and a teenager class is created using the child class attributes
    ### if the teenager ages up to a young adult, then the teenager class is deleted and a young adult class is created using the teenager class attributes
    ### if the young adult ages up to an adult, then the young adult class is deleted and an adult class is created using the young adult class attributes
    ### if the adult ages up to an elder, then the adult class is deleted and an elder class is created using the adult class attributes
    pass

class Person_Life(Person_Functions):
    def __init__(self, gender:str =None, first_name:str = None, last_name:str = None, current_year:int = None, age_range: str = None, married=False):
        super().__init__(gender, first_name, last_name, current_year, age_range, married)
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
    def death(self):
        ### add cause of death
        ### add probability of death based on age
        ### ????
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
        ### may get married
        ### may have children
        ### may get a house
        ### may get a car

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
               temp_history = self.handle_finished_studies(temp_history)
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
        return temp_history

    def age_up(self):
        ### check current age range and age one year for that age range
        temp_history = self.history_df.iloc[-1].copy()
        #print(temp_history)
        age_range = temp_history['age_range']
        
        #print(age_range, temp_history['age'], " age up function start")
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



#### Lets create a class to handle financial products such as loans and insurance
#### the class will later register things as tables in a database
#### one table will be the loan request table with
#  the loan_id,
#  the loan_purpose,
#  the person_id, 
#  the person_income at the time of the loan, 
#  loan_amount, 
#  loan_term, 
#  interest_rate, and check if the person is eligible for the loan
#  the loan_type,

#### another table will be the loan day to day table with
#  the loan_id,
#  the loan balance,
#  the loan total term,
#  the loan current term,
#  the loan payment,
#  the loan status,

#### how to handle the loan refinancing?

### loan refinancing will be a new loan, with a new loan_id, and a new loan term, and a new loan payment
### the previous loan will be closed and the previous loan balance will be zero and the status will be refinanced
### the previous loan will be kept in the database for historical purposes

#### how to handle the loan defaulting? Future Development

#### hot to handle the loan payment?

#### Creating a class to handle loans and other financial products - Financial Institution
#### Financial Institution will get person_id, person_income at the time of the loan, loan_amount, loan_term, interest_rate, and check if the person is eligible for the loan
#### Financial Institution will keep record of the person balance and the loan balance
#### Financial Institution will know what is the loan type/reason and if the loan was refinanced
#### main loan types: mortgage, student loan, car loan, personal loan
#### main loan reasons: buy a house, pay for college, buy a car, personal loan
#### main loan refinanced: yes, no
#### main loan status: active, paid, defaulted
#### main loan balance: current balance of the loan
#### main loan term: number of years to pay the loan
#### Financial Institution will also keep track of the interest rate and the interest rate type (fixed or variable) ### future development
#### Financial Institution will also provide the yearly payment
#### Financial Institution will provide a new Insurance table with 
# ... the insurance type, insurance amount also know as face amount, insurance term if applicable, insurance status, insurance balance, insurance term, insurance payment



class Financial_Institution():
    def __init__(self, bank_name = None):
        self.bank_name = bank_name
        self.loan_df = pd.DataFrame(columns=['person_id', 'person_income', 'loan_amount', 'loan_term', 
                                             'interest_rate', 'loan_type', 'loan_reason', 'loan_refinanced', 
                                             'person_balance', 'year'])


        self.insurance_df = pd.DataFrame()
    
    @staticmethod
    def eligibility(person_income, loan_amount, loan_term, interest_rate, loan_type, loan_reason, loan_refinanced, person_balance, year):
        # Procedure CheckLoanEligibility:
        # Input: person_income, loan_amount, loan_term, interest_rate, loan_type, loan_reason, loan_refinanced, person_balance, year, x, other_loan_amount
        # Output: eligibility

        # 1. total_loan_amount ← loan_amount + other_loan_amount  // Sum of current loan amount and loans from other sources
        # 2. income_threshold ← (x / 100) * person_income  // Maximum loan amount allowed based on person's income

        # 3. If total_loan_amount ≤ income_threshold Then
        # 4. // Additional eligibility checks can be performed here, for example:
        # 5. If loan_refinanced = True Then
        # 6. eligibility ← False
        # 7. Else If person_balance < (0.10 * total_loan_amount) Then
        # 8. eligibility ← False  // Person should have at least 10% of the total loan amount in balance
        # 9. Else If loan_term > 30 or loan_term < 1 Then
        # 10. eligibility ← False  // Loan term should be between 1 and 30 years
        # 11. Else
        # 12. eligibility ← True
        # 13. Else
        # 14. eligibility ← False
        # 15. Return eligibility

    
    
        def get_loan(self, person_id, person_income, loan_amount, loan_term, interest_rate,
                        loan_type, loan_reason, loan_refinanced, person_balance, year):
        
            ### check if the person is eligible for the loan
            ### check if the person has a loan already
            ### check if the person has a loan and is refinancing
            ### check if the person has a loan and is refinancing and the loan is the same type as the previous loan
            ### check if the person has a loan and is refinancing and the loan is a different type as the previous loan
            ### check if the person has a loan and is not refinancing
            ### check if the person has a loan and is not refinancing and the loan is the same type as the previous loan
            ### check if the person has a loan and is not refinancing and the loan is a different type as the previous loan
            ### check if the person does not have a loan
            pass

class Financial_Institution:
    def __init__(self, bank_name=None):
        self.bank_name = bank_name
        self.loan_df = pd.DataFrame(columns=[
            'loan_id', 'person_id', 'person_income', 'loan_amount', 'loan_term',
            'interest_rate', 'loan_type', 'loan_reason', 'loan_refinanced',
            'loan_balance', 'loan_status', 'loan_payment'
        ])
        self.loan_day_to_day_df = pd.DataFrame(columns=[
            'loan_id', 'loan_balance', 'loan_total_term', 'loan_current_term',
            'loan_payment', 'loan_status'
        ])
        self.insurance_df = pd.DataFrame(columns=[
            'insurance_type', 'insurance_amount', 'insurance_term',
            'insurance_status', 'insurance_balance', 'insurance_payment'
        ])

    @staticmethod
    def check_eligibility(person_income, loan_amount):
        # Example eligibility check: person's income should be at least twice the loan amount
        # simple eligibility check that will be replaced by a more complex one
        return person_income >= 2 * loan_amount

    @staticmethod
    def add_loan(loan_df, loan_id, person_id, person_income, loan_amount, loan_term, interest_rate, loan_type, loan_reason):
        if not Financial_Institution.check_eligibility(person_income, loan_amount):
            print(f'Person {person_id} is not eligible for the loan')
            return loan_df

        loan_data = {
            'loan_id': loan_id,
            'person_id': person_id,
            'person_income': person_income,
            'loan_amount': loan_amount,
            'loan_term': loan_term,
            'interest_rate': interest_rate,
            'loan_type': loan_type,
            'loan_reason': loan_reason,
            'loan_refinanced': 'no',
            'loan_balance': loan_amount,
            'loan_status': 'active',
            'loan_payment': 0  # Initial payment is 0
        }
        return loan_df.append(loan_data, ignore_index=True)

    @staticmethod
    def add_payment(loan_df, loan_day_to_day_df, loan_id, payment_amount):
        loan_idx = loan_df[loan_df['loan_id'] == loan_id].index[0]
        loan_df.at[loan_idx, 'loan_balance'] -= payment_amount
        loan_df.at[loan_idx, 'loan_payment'] += payment_amount

        day_to_day_data = {
            'loan_id': loan_id,
            'loan_balance': loan_df.at[loan_idx, 'loan_balance'],
            # ... (other necessary fields)
        }
        return loan_df, loan_day_to_day_df.append(day_to_day_data, ignore_index=True)
    
    @staticmethod
    def refinance_loan(loan_df, loan_id, new_loan_id, new_loan_term, new_loan_payment):
        # Close old loan
        loan_idx = loan_df[loan_df['loan_id'] == loan_id].index[0]
        loan_df.at[loan_idx, 'loan_status'] = 'refinanced'
        loan_df.at[loan_idx, 'loan_balance'] = 0

        # Create new loan
        new_loan_data = loan_df.loc[loan_idx].to_dict()
        new_loan_data['loan_id'] = new_loan_id
        new_loan_data['loan_term'] = new_loan_term
        new_loan_data['loan_payment'] = new_loan_payment
        return loan_df.append(new_loan_data, ignore_index=True)
    # ... (other methods)
    # @staticmethod
    # def add_insurance(insurance_type, insurance_amount, insurance_term, insurance_status, insurance_balance, insurance_payment):
    #     insurance_data = {
    #         'insurance_type': insurance_type,
    #         'insurance_amount': insurance_amount,
    #         'insurance_term': insurance_term,
    #         'insurance_status': insurance_status,
    #         'insurance_balance': insurance_balance,
    #         'insurance_payment': insurance_payment
    #     }
    #     temp_insurance_df = pd.DataFrame(columns=[
    #         'insurance_type', 'insurance_amount', 'insurance_term',
    #         'insurance_status', 'insurance_balance', 'insurance_payment'
    #     ])
    #     ### append the new insurance data to the existing insurance data

    #     return insurance_df.append(insurance_data, ignore_index=True)
# Usage example:
fi = Financial_Institution()
#fi.loan_df = Financial_Institution2.add_loan(fi.loan_df, 'loan_001', 'person_001', 50000, 20000, 5, 3.5, 'personal', 'buy a car')
