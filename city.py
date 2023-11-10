import numpy as np
import pandas as pd

from  gml_constants import ( AGE_RANGES,
                            CAREERS_AND_MARRIAGE_PROBS,
                            MIN_MARRIAGE_ALLOWED_AGE, 
                            SAME_GENDER_MARRIAGE_RATIO)
from person import Person_Life

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
