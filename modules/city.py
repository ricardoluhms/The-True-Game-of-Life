import numpy as np
import pandas as pd
import os
import sys
import tqdm
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from  modules.gml_constants import ( CAREERS_AND_MARRIAGE_PROBS,
                            MIN_MARRIAGE_ALLOWED_AGE, 
                            SAME_GENDER_MARRIAGE_RATIO,
                            BABY_TWINS_MODE, 
                            EXISTING_CHILDREN_PROB_DICT,
                            SPENDER_PROFILE_DECREASE,
                            BASE_BIRTH_PROB,
                            MAX_DEBT_RATIO,
                            INTEREST_RATE_PER_TYPE)

from modules.person import Person_Life
from modules.financial_institution import Financial_Institution
from logging import getLogger
### import time library for testing
import time

logger = getLogger(__name__)

class City():
  
    ### create a city with a name and a population of young adults 

    def __init__(self, name:str, population:int, current_year:int = 1950, mode:str = 'default', finance_institution = None):

        ### explain what City class does and the inputs, outputs and attributes
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
        self.history = pd.DataFrame()
        self.financial_institution = finance_institution
        self.deceased_people = {}
        if mode == 'default':
            ###For generating random 
            self.people_obj_dict = self.generate_starting_pop(population=population, age_range='Young Adult')
            self.retrieve_history_from_people()
        elif mode == 'testing':
            ###For generating specific people
            self.people_obj_dict = {}
        ### explain what City class does and the inputs, outputs and attributes
        if finance_institution is None:
            finance_institution = Financial_Institution(bank_name=f"{name} Bank")
        self.financial_institution = finance_institution
        self.time_record = [time.time()]
    
    @staticmethod
    def update_person_constant(person, person_history):
        ### loop over person constants and check if the person has the constant
        ### loop over person last history and update the constant based on the person history
        ### person is a class object and some of the constants are in the class object
        for constant in person.__dict__.keys():
            if constant in person_history:
                person.__dict__[constant] = person_history[constant]
        return person

    def age_up(self):
        self.current_year += 1
        logger.info(f"### Ageing up the city {self.current_year}")
        logger.info(f"### Number of people in the city {len(self.people_obj_dict)}")
        logger.info(f"### Number of deceased people in the city {len(self.deceased_people)}")

        ### Had to be changed to .copy() since we can't change the size of the acutal dictionary while its looping (when adding spouse)
        for person_id in self.people_obj_dict.copy():

            #dead_not_removed = temp_history["event"] == "This is a test event - this should be overwritten by the function"
            
            ### check if the person is deceased list
            if person_id not in self.deceased_people:

                ### retrieve the person object in active people
                person_obj = self.people_obj_dict[person_id]
                temp_history = person_obj.history_df.iloc[-1].copy()
                ### Age up the person and check if the person is deceased
                ### track time for testing
                self.time_record.append(time.time())
                death = person_obj.age_up_one_year_any_life_stage(temp_history)
                self.time_record.append(time.time())
                delta = round((self.time_record[-1] - self.time_record[-2]),4)
                logger.info(f"### Age Up: {delta}s - {person_obj.history_df.iloc[-1]['age']} - {person_obj.history_df.iloc[-1]['year']}")

                ### check if the person is deceased
                if death or death is None:
                    ### if the person is deceased, add the person to the deceased list and remove from the active people
                    self.deceased_people[person_id] = person_obj

                    del self.people_obj_dict[person_id]
                    logger.info(f"  Death Status: {death} -\n\
                                    Person ID: {person_id} -\n\
                                    Event: {person_obj.history_df.iloc[-1]['event']} -\n\
                                    Age: {person_obj.history_df.iloc[-1]['age']} -\n\
                                    Year: {person_obj.history_df.iloc[-1]['year']}")

                else:
                    ### check current history, if there is a marriage, check person id is in the city history
                    ### Placeholder for marriage function
                    self.time_record.append(time.time())
                    spouse = self.handle_marriage(person_obj)
                    self.time_record.append(time.time())
                    delta = round((self.time_record[-1] - self.time_record[-2]),4)
                    logger.info(f"### Marriage Check: {delta}s - {person_obj.history_df.iloc[-1]['age']} - {person_obj.history_df.iloc[-1]['year']}")
                    if spouse is not None:

                        ### check if the spouse has the person as the spouse
                        if spouse.spouse_name_id != person_obj.unique_name_id:
                            ### if true then solve the issue
                            spouse.spouse_name_id = person_obj.unique_name_id
                            spouse.married = True
                            spouse.just_married = True
                            ### update the spouse history for the current and previous year

                            updated_spouse_history = spouse.history_df.iloc[-1].copy()
                            updated_spouse_history_ly = spouse.history_df.iloc[-2].copy()

                            updated_spouse_history['spouse_name_id'] = person_obj.unique_name_id
                            updated_spouse_history_ly['spouse_name_id'] = person_obj.unique_name_id

                            updated_spouse_history['married'] = True
                            updated_spouse_history_ly['married'] = True
                            updated_spouse_history['just_married'] = False
                            updated_spouse_history_ly['just_married'] = True
                            spouse.history_df.iloc[-1] = updated_spouse_history
                            spouse.history_df.iloc[-2] = updated_spouse_history_ly

                        ### append the spouse to the city history
                        self.history = pd.concat([self.history, spouse.history_df])
                        ### update the spouse object in the active people
                        self.people_obj_dict[spouse.unique_name_id] = spouse
                    
                    self.handle_child_born(person_obj)
                    self.pay_loan(person_obj)
                    ### Placeholder for getting a loan for:
                    # - buying a house (loan reason)
                    # - buying a car (loan reason)
                    # - getting married (loan reason)
                    # - having a child (loan reason)
                    # - going to college (loan reason)
                    ### if the person is not deceased, update the person object in the active people
                    person_obj = self.update_person_constant(person_obj, person_obj.history_df.iloc[-1]) 

                    self.people_obj_dict[person_id] = person_obj

                ### append the person history to the city history
                self.history = pd.concat([self.history, person_obj.history_df])
                ### drop duplicates
                self.history = self.history.drop_duplicates(subset=['unique_name_id', 'year','event'], keep='last')
                    
    def generate_starting_pop(self, population:int = None, age_range:str = 'Young Adult'):
        # make a even distribution of gender
        people_list = {}
        if population is None:
            population = 1
        for _ in tqdm.tqdm(range(self.population)):
            current_person = Person_Life(age_range= age_range, current_year=self.current_year)

            ### a random max age to a teenager
            #max_age = np.random.randint(AGE_RANGES[age_range][0],AGE_RANGES[age_range][1])

            current_person.generate_past_events()
            ### retrieve the last history of the person and the unique_name_id
            temp_history = current_person.history_df.iloc[-1].copy()
            unique_name_id = temp_history['unique_name_id']
            people_list[unique_name_id] = current_person
        
        return people_list

    def retrieve_history_from_people(self): ### will be deprecated in the future
        for person_id in self.people_obj_dict.keys():
            person = self.people_obj_dict[person_id]
            if len(self.history) == 0:
                self.history = person.history_df
            else:
                self.history = pd.concat([self.history, 
                                 person.history_df])

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
        if person_last_history['age_range'] not in ["Baby", "Child", "Teenager"]:
            
            if person_last_history['career'] is None:
                return None
            ### check current employment status to retrieve the marriage probability
            career_crit_chance = CAREERS_AND_MARRIAGE_PROBS[person_last_history['career']] ### test for all careers later - to be developed
            
            ### check if the person is old enough to get married and is not married
            age_cri = person_last_history["age"] >= MIN_MARRIAGE_ALLOWED_AGE
            married_cri = person_last_history["married"] == False
            prob_cri = np.random.random() < career_crit_chance

            ### FOR TESTING MARRIAGE
            prob_cri = True

            ### Based on the career of the person, check if the person will get married
            can_marry_cri = age_cri and married_cri and prob_cri

            if can_marry_cri:
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

                does_not_have_the_same_parentsA = all_population['parent_name_id_A'] != person_last_history['parent_name_id_A']
                does_not_have_the_same_parentsB = all_population['parent_name_id_B'] != person_last_history['parent_name_id_B']
                marriage_criteria = marriage_criteria & does_not_have_the_same_parentsA & does_not_have_the_same_parentsB

                eligible_people_crit_within_city = marriage_criteria.sum() > 0

                if eligible_people_crit_within_city:
                    # retrieve the spouse candidate from the city
                    spouse_id = all_population[marriage_criteria].sample(1).iloc[0].copy()['unique_name_id'] ### select on from the list

                    spouse = self.people_obj_dict[spouse_id]
                    spouse_last_history = spouse.history_df.iloc[-1].copy()
                    #Retrieve the person history
                    person_last_history = person.history_df.iloc[-1].copy()

                    ### quick error check to see if the last history is the same year as the person - else solve the issue
                    if spouse_last_history['year'] != person_last_history['year']:
                        logger.debug(f"Solve the issue \n\
                                     - Last history of the spouse candidate -\
                                      is not the same year as the person which means there is a problem with the current logic -\n\
                                      {spouse_last_history['year']} -\n\
                                      {person_last_history['year']} -\n\
                                      {person_last_history['unique_name_id']}")
                        pass

                    ###Update the spouse and person values so they are married

                    # - change the married status to True
                    spouse_last_history['married'] = True
                    # - change the just_married status to True
                    spouse_last_history['just_married'] = True
                    # - change the spouse_name_id to the person unique_name_id
                    spouse_last_history['spouse_name_id'] = person_last_history['unique_name_id']
                    # the person last history:

                    # - change the spouse_name_id to the spouse unique_name_id
                    last_index = person.history_df.index[-1]
                    person.history_df.loc[last_index, 'spouse_name_id'] = spouse_last_history['unique_name_id']


                    # update the history of the person and the spouse candidate
                    
                    person_last_history['married'] = True
                    person_last_history['just_married'] = True
                    person_last_history['spouse_name_id'] = spouse_last_history['unique_name_id']

                    ###Update the actual dataframes
                    person.history_df.iloc[-1] = person_last_history
                    spouse.history_df.iloc[-1] = spouse_last_history

                    # update the object status
                    person.married = True
                    person.just_married = True
                    self.people_obj_dict[spouse.unique_name_id] = spouse
                    
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
                    
                    ### Stage 1 - select the age of the spouse
                    spouse_age = np.random.randint(spouse_min_age, person_age + 5)

                    ### Stage 2 - get age range based on the age
                    spouse_age_range = Person_Life.update_age_range(spouse_age) ### TO BE DEVELOPED - SKIP AGE RANGE TO REPLACE WITH THE AGE WHEN CREATING A NEW PERSON

                    ### Stage 3 - create a new person with the age range and the current year
                    spouse = Person_Life(gender= spouse_gender, age_range= spouse_age_range, current_year= person_most_recent_year, married = True)

                    ### Stage 4 - generate the past events of the new spouse
                    spouse.generate_past_events()

                    ### Stage 5 - update the history of the spouse
                    ### married to true will be applied to all the history of the person so it need to be removed from the history later
                    spouse_all_history = spouse.history_df.copy()
                    criteria_arange = spouse_all_history["age_range"] == spouse_age_range
                    criteria_age = spouse_all_history["age"] == spouse_age
                    criteria_year = spouse_all_history["year"] == person_most_recent_year

                    marriage_status_crit = criteria_arange & criteria_age & criteria_year


                    spouse_all_history.loc[~marriage_status_crit,"married"] = False
                    spouse_all_history.loc[marriage_status_crit,"just_married"] = True
                    spouse_all_history.loc[marriage_status_crit,"married"] = True
                    spouse_all_history.loc[marriage_status_crit,"spouse_name_id"] = person_last_history['unique_name_id']
                    spouse.history_df = spouse_all_history


                    ###Grabs the histories we need
                    spouse_last_history = spouse.history_df.iloc[-1].copy()
                    person_last_history = person.history_df.iloc[-1].copy()

                    ###Updates everything for the person getting married to the spouse
                    person_last_history['married'] = True
                    person_last_history["just_married"] = True
                    person_last_history["spouse_name_id"] = spouse.unique_name_id
                    person.history_df.iloc[-1] = person_last_history

                    ###Updates the values of the acutal object
                    person.married = True
                    person.just_married = True
                    self.people_obj_dict[spouse.unique_name_id] = spouse
                    ### append the spouse to the city history
                    self.history = pd.concat([self.history, spouse.history_df])

                ### TO BE DEVELOPED ###
                # # check if the person has enough money to get married    
                # _, marriage_expense = self.calculate_marriage_cost() ### to be developed
                # total_balance = person_last_history['balance'] + spouse_last_history['balance']
                # ### if the person does not have enough money, then check both person and spouse candidate can get a loan
                # if total_balance < marriage_expense:
                #     get_loan_status = self.get_loan(desired_loan_amount=marriage_expense-total_balance)
                #     if  get_loan_status is None:
                #         print('You cannot afford the marriage expense. You have reached the maximum loan amount.')
                return spouse
            else:
                return None
        else:
            return None

    def handle_child_born(self, person, baby_count = None):
        t_start = time.time()
        # retrieve the last history of the person and:
        person_last_history = person.history_df.iloc[-1].copy()
        spouse_id = person_last_history['spouse_name_id']
        ### if there is no spouse, then skip the function
        if spouse_id is None:
            ### Adoption could be a future feature
            return "Cannot have a child - No spouse"
        
        elif spouse_id not in self.people_obj_dict:
            ### child born but parent might have died - future feature
            return "Cannot have a child - Spouse not in city"
        
        elif spouse_id in self.deceased_people:
            return "Cannot have a child - Spouse is deceased"

        spouse = self.people_obj_dict[spouse_id]
        spouse_last_history = spouse.history_df.iloc[-1].copy()

        ### check if the person is married and is old enough to have a child
        age_cri = person_last_history["age"] >= 18
        married_cri = person_last_history["married"] == True

        age_spouse_cri = spouse_last_history["age"] >= 18
        married_spouse_cri = spouse_last_history["married"] == True

        ### age of the mother
        if person_last_history["gender"] == "Female":
            age_mother = person_last_history["age"]
            existing_children_count = len(person_last_history["children_name_id"])
        elif spouse_last_history["gender"] == "Female":
            age_mother = spouse_last_history["age"]
            existing_children_count = len(spouse_last_history["children_name_id"])
        else:
            age_mother = None
        
        ### combine the criterias
        age_cri = age_cri and age_spouse_cri
        married_cri = married_cri and married_spouse_cri
        can_have_child_cri = age_cri and married_cri
        
        if can_have_child_cri is False:
            ### check if the mother is old enough to have a child
            return "Cannot have a child - Mother is not old enough"

        if age_mother is None:
            return "Cannot have a child - Mother is not defined"

        ### rewrite base_prob to be a function of the age of the mother and will decrease with age
        try:
            decreasing_prob_existin_children = EXISTING_CHILDREN_PROB_DICT[existing_children_count]
        except:
            decreasing_prob_existin_children = max(EXISTING_CHILDREN_PROB_DICT.values())+0.1
        decreasing_prob = -0.11306*np.exp((age_mother-10)/25) -\
                             decreasing_prob_existin_children

        total_prob = BASE_BIRTH_PROB + decreasing_prob
        if total_prob <= 0:
            return "Cannot have a child - Age of the mother is too high"

        if np.random.random() <= total_prob:
            return ""

        ### twins or more probability
        if baby_count is None:
            baby_count = np.random.choice( list(BABY_TWINS_MODE.keys()),
                                        p=np.array(list(BABY_TWINS_MODE.values())))
        
        for _ in range(baby_count):
            baby = Person_Life(age_range='Baby', current_year=self.current_year,
                                      last_name=person_last_history['last_name']+" "+spouse_last_history['last_name'],
                                      parent_name_id_A = person_last_history["unique_name_id"], 
                                      parent_name_id_B= spouse_last_history["unique_name_id"])
            
            ### add the baby into the person and spouse children_name_id list
            if baby.unique_name_id not in person_last_history["children_name_id"]:

                person_last_history["children_name_id"].append(baby.unique_name_id)
            if baby.unique_name_id not in spouse_last_history["children_name_id"]:
                spouse_last_history["children_name_id"].append(baby.unique_name_id)
            ### add baby to city
            self.people_obj_dict[baby.unique_name_id] = baby
             
        ### Add Event to the history of the person and the spouse
        if baby_count == 1:
            logger.info(f"### Child Born - {baby.unique_name_id} - {person_last_history['unique_name_id']} - {spouse_last_history['unique_name_id']}")
            person_last_history["event"] += " - 1 Child Born"
            spouse_last_history["event"] += " - 1 Child Born"
        else:
            logger.info(f"### Children Born - {baby_count} -\
                        {person_last_history['unique_name_id']} -\
                        {spouse_last_history['unique_name_id']}")
            person_last_history["event"] += f" - {baby_count} Children Born"
            spouse_last_history["event"] += f" - {baby_count} Children Born"
        
        ### update the history of the person and the spouse in the city
        person.history_df.iloc[-1] = person_last_history
        spouse.history_df.iloc[-1] = spouse_last_history

        ### update the person and the spouse in the city
        self.people_obj_dict[person.unique_name_id] = person
        self.people_obj_dict[spouse.unique_name_id] = spouse
        t_end =time.time()
        delta = round((t_end - t_start),4)
        logger.info(f"### Children Born - {baby_count} -\
                    {person_last_history['unique_name_id']} -\
                    {spouse_last_history['unique_name_id']} - {delta}s")

    def retrieve_loan_customer_data(self, person_id = None):

        ids = [person_id]
        # check if the person has spouse
        spouse_id = self.people_obj_dict[person_id].spouse_name_id
        if spouse_id is not None:
            ids.append(spouse_id)
        
        # check if the person has children
        children_ids = self.people_obj_dict[person_id].children_name_id

        if len(children_ids) > 0:
            for child_id in children_ids:
                ### check if the child is older than 18 so they will not be included in the loan calculation ### improve this later
                if self.people_obj_dict[child_id].age < 18:
                    ids.append(child_id)
        
        ### retrieve their income and balance
        income_and_bal_df = pd.DataFrame()

        for id in ids:
            income_and_bal_df = income_and_bal_df.append(self.people_obj_dict[id].history_df.iloc[-1].copy()[['unique_name_id','income','balance']])

        ### retrieve their loan data
        loan_df = self.financial_institution.loan_df.copy()
        family_loans_df = loan_df[loan_df['person_id'].isin(ids)]

        ### loan must be active
        family_loans_df = family_loans_df[family_loans_df['loan_status'] == 'active']

        return income_and_bal_df, family_loans_df

    def pay_loan(self, person_obj):
            ### retrieve the person object
            ###  check career and income
            person_last_history = person_obj.history_df.iloc[-1].copy()
            career = person_last_history['career']
            if career in ['Pocket Money','Part Time']:
                pass
            
            else:
                balance = person_last_history['balance']

                ### retrieve the loan data
                loan = person_last_history['loan']
                loan_term = person_last_history['loan_term']

                c1 = loan is None
                c2 = loan == 0
                c3 = c1 or c2
                c4 = not c3

                if c4 and loan_term != 0:
                    
                    ### loan term should not be 0
                    if loan_term == 0:
                        logger.debug(f"### Loan Term is 0 - {loan_term} - {person_last_history['unique_name_id']}")
                        loan_term = 1

                    amount_to_pay = loan/loan_term
                    loan_text_p1 = f"A.M.T: {round(amount_to_pay,2)} - Loan: {round(loan,2)} - L.Term: {loan_term}"
                    loan_text_p2 = f" Balance: {round(balance,2)} - PID: {person_last_history['unique_name_id']}"
                    logger.info(f"### Paying Loan - {loan_text_p1} - {loan_text_p2}")

                    if amount_to_pay > balance:
                        ### add interest to the loan
                        interest_rate = person_last_history['interest_rate']
                        amount_to_pay += amount_to_pay*interest_rate

                        ### update the loan amount
                        amount_to_pay += amount_to_pay
                        ### change spender profile
                        new_spender_prof = SPENDER_PROFILE_DECREASE[person_last_history['spender_prof']]
                        person_last_history['spender_prof'] = new_spender_prof
                        person_last_history["event"] = "Loan Payment Failed - Spender Profile Decreased"
                        person_last_history['loan'] = amount_to_pay

                        ### update object info
                        person_obj.spender_prof = new_spender_prof
                        person_obj.loan = amount_to_pay

                    else:
                        ### pay the loan
                        balance -= amount_to_pay
                        loan_term -= 1

                        if loan_term == 0:
                            ### remove the loan
                            loan = 0
                            interest_rate = 0
                            person_last_history["event"] = "Loan Payment Complete"
                            ### change spender profile - increase
                            current = person_last_history['spender_prof']
                            if current == 'Depressed' or current == 'In-Debt':
                                ### retrieve new spender profile
                                person_last_history['spender_prof']  = person_obj.set_spender_profile()
                            
                        else:
                            person_last_history["event"] = "Loan Payment OK"
                            loan = loan - amount_to_pay

                        person_last_history['loan_term'] = loan_term
                        #loan['loan_status'] = loan_status
                        person_last_history['loan'] = loan
                        person_last_history['balance'] = balance
                    person_obj.history_df.iloc[-1] = person_last_history
                    person_id = person_last_history['unique_name_id']
                    self.people_obj_dict[person_id] = person_obj
            #return person_last_history
                


# %%
