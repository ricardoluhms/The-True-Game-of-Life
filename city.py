#%%
import numpy as np
import pandas as pd
from person import Person_Life
from  gml_constants import ( AGE_RANGES, CAREERS_AND_MARRIAGE_PROBS,MIN_MARRIAGE_ALLOWED_AGE, 
                            SAME_GENDER_MARRIAGE_RATIO)


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
        pass

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
fi.loan_df = Financial_Institution.add_loan(fi.loan_df, 'loan_001', 'person_001', 50000, 20000, 5, 3.5, 'personal', 'buy a car')