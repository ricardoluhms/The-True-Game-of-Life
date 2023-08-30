import numpy as np
import pandas as pd
from collections import defaultdict
#from faker import Faker

years_of_study = {'Base': 2, 'Medium': 3, 'High': 5, 'Very High': 7}
tuition = {'Base': 1000, 'Medium': 3000, 'High': 6000, 'Very High': 10000}
spender_profile = {'Average':0.9, 'Big Spender':1.05, 'Small Spender':0.75}
class Person:
    def __init__(self, gender, age=None, income=None, balance=None, career=None,spender_prof = None, to_check=None):
        if spender_prof == None:
            self.spender_prof = np.random.choice(['Average', 'Big Spender', 'Small Spender'], p=[0.5, 0.3, 0.2])
        if age == None:
            self.initial_age()

        if income == None and career == None:
            # Determine the career level based on the age
            self.student_and_career_path_check()
            self.initial_income()
        if balance == None:
            pass

        if to_check == None:
            if balance == 0:
                balance = np.random.normal(50000, 40000)

            self.gender = gender
            self.age = age
            self.income = income
            self.balance = balance
            self.career = career

            if career == 'Student':
                self.loan = np.random.randint(10000, 20000)

            self.loan = 0
            self.loan_term = 0
            self.married = False
            self.history = pd.DataFrame(columns=['age', 'balance', 'income', 'loan','married','career'])

    def initial_age(self):
        # Generate a random age between 0 and 95
        self.age = np.random.randint(0, 95)

    def student_and_career_path_check(self):
        if self.age < 18:
            ### no student loan
            self.career = 'Cannot Work'

        elif 18 <= self.age < 25:
            self.initial_student_years_of_grad(mode='Could be Student')
        else:
            self.initial_career()
            self.initial_student_years_of_grad(mode = "Graduated")
            
    def initial_student_years_of_grad(self, mode = 'Could be Student'):

        if mode == 'Could be Student':
            self.future_career = np.random.choice(['Base', 'Medium', 'High', 'Very High'], p=[0.4, 0.3, 0.2, 0.1])
            years_of_grad = self.age - 18 + years_of_study[self.future_career]

            ### check if they are old and completed their study
            if years_of_grad>= 0:
                self.career = self.future_career
            else:
                self.career = 'Student'
                if years_of_study<0:
                    years_of_grad = 0

        else:
            years_of_grad = self.age - 18 + years_of_study[self.career]
        return years_of_grad

    def childhood_savings(self):
        if self.age < 18:
            childhood_years = self.age
        else:
            childhood_years = 17
        for _ in range(childhood_years):
            self.balance += np.random.normal(500, 500)

    def part_time_job(self):
        if self.age < 18:
            part_time_years = 0
        elif 18 <= self.age < 25 and self.career == 'Student':
            part_time_years = self.age - 18
        else:
            part_time_years = years_of_study[self.career] - 1
        for _ in range(part_time_years):
            self.balance += np.random.normal(10000, 5000) * (1-spender_profile[self.spender_prof])

    def full_time_job_static(self):
        if self.age < 18:
            full_time_years = 0
        elif 18 <= self.age < 25 and self.career == 'Student':
            full_time_years = 0
        else:
            full_time_years = self.age - years_of_study[self.career]-18
        for _ in range(full_time_years):
            self.balance += self.income * (1-spender_profile[self.spender_prof])

    def initial_balance(self):
        ### calculate the balance based on the income and age and career
        self.childhood_savings()
        self.part_time_job()


    def loan_to_balance_check(self):
        if self.balance < 0:
            self.balance = 0


    def student_loan(self,years_of_grad):
        
        student_loan_rate = np.random.normal(0.02, 0.01)
        student_loan_term = np.random.randint(10, 21)
    
        if self.career == 'Student':
            base_loan = (tuition[self.future_career] * years_of_study[self.future_career])*(1+student_loan_rate)**student_loan_term

        elif self.career != 'Cannot Work':
            base_loan =  (tuition[self.career] * years_of_study[self.career])*(1+student_loan_rate)**student_loan_term
            
        

    def initial_career(self):
        if 25 <= self.age < 35:
            self.career = np.random.choice(['Base', 'Medium', 'High'], p=[0.5, 0.4, 0.1])
        elif 35 <= self.age < 55:
            self.career = np.random.choice(['Base', 'Medium', 'High', 'Very High'], p=[0.3, 0.4, 0.2, 0.1])
        else:  # age >= 55
            self.career = np.random.choice(['Base', 'Medium', 'High', 'Very High'], p=[0.4, 0.3, 0.2, 0.1])
    
    

    def initial_income (self):
        if self.career == 'Student':
            self.income = np.random.normal(5000, 4000)
        elif self.career == 'Base':
            self.income = np.random.normal(40000, 10000)
        elif self.career == 'Medium':
            self.income = np.random.normal(60000, 15000)
        elif self.career == 'High':
            self.income = np.random.normal(80000, 20000)
        else:  # career == 'Very High'
            self.income = np.random.normal(120000, 40000)

    def update_history(self):
        self.history = self.history.append({'age': self.age, 'balance': self.balance, 
                                            'income': self.income, 'loan': self.loan, 
                                            'married':self.loan,'career':self.career}, ignore_index=True)

    def study(self):
        costs = np.random.randint(20000, 30000)
        years_of_study = {'Base': 2, 'Medium': 3, 'High': 5, 'Very High': 7}
        tuition = {'Base': 1000, 'Medium': 3000, 'High': 6000, 'Very High': 10000}
        
        for i in range(years_of_study[self.career]):
            self.loan += tuition[self.career] + costs
            self.age += 1
            self.update_history()
        
        self.loan_term = np.random.randint(10, 21)  # loan term can be from 10 to 20 years

    def pay_loan(self):
        if self.loan_term > 0:
            self.loan -= self.loan * 0.02  # 2% of loan amount
            self.balance -= self.loan * 0.02
            self.loan_term -= 1
            self.update_history()

    def work(self):
        if self.career == 'Base':
            self.income = np.random.randint(45000, 55000)
        elif self.career == 'Medium':
            self.income = np.random.randint(50000, 75000)
        elif self.career == 'High':
            self.income = np.random.randint(70000, 85000)
        
        self.balance += self.income - np.random.randint(20000, 30000)
        self.update_history()

    def promotion(self):
        if np.random.rand() <= 0.5:
            raise_percent = np.random.choice([0.2, 0.15, 0.1, 0.05], p=[0.05, 0.15, 0.4, 0.4])
            self.income *= 1 + raise_percent
            self.balance += self.income
            self.update_history()

    def get_dataframe(self):
        return pd.DataFrame(self.history)

class Marriage:
    def __init__(self, person1, person2):
        self.person1 = person1
        self.person2 = person2
        self.balance = person1.balance + person2.balance
        self.income = person1.income + person2.income
        self.history = defaultdict(list)
        self.renegotiate_loan()

    def update_history(self):
        self.history['balance'].append(self.balance)
        self.history['income'].append(self.income)

    def renegotiate_loan(self):
        # Add your logic for loan renegotiation here
        pass

    def get_dataframe(self):
        return pd.DataFrame(self.history)
    
    def have_child(self):
        if self.children == 0 and np.random.rand() <= 0.4:
            self.children += 1
        elif self.children == 1 and np.random.rand() <= 0.2:
            self.children += 1
        elif self.children == 2 and np.random.rand() <= 0.1:
            self.children += 1
        elif self.children >= 3 and np.random.rand() <= 0.02:
            self.children += 1
        self.update_history()

class Bank:
    def __init__(self):
        self.loan_products = {
            'Base': 20000,
            'Medium': 30000,
            'High': 40000,
            'Very High': 50000,
            'Student': 10000
        }

    def offer_loan(self, person):
        if person.career == 'Student' and person.age == 18:
            loan_amount = self.loan_products[person.career]
        else:
            loan_amount = self.loan_products.get(person.career, 0)

        # Check if the loan amount exceeds 10% of the person's annual income
        if loan_amount > 0.1 * person.income:
            loan_amount = 0.1 * person.income

        loan_term = np.random.randint(10, 21)  # loan term can be from 10 to 20 years
        person.loan += loan_amount
        person.loan_term += loan_term
        person.update_history()

players = []


### generate 1 