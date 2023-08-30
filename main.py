import numpy as np
import pandas as pd
from collections import defaultdict

years_of_study = {'Base': 2, 'Medium': 3, 'High': 5, 'Very High': 7}
tuition = {'Base': 1000, 'Medium': 3000, 'High': 6000, 'Very High': 10000}
spender_profile = {'Average': 0.9, 'Big Spender': 1.05, 'Small Spender': 0.75}

class Person:
    def __init__(self, gender):
        self.gender = gender
        self.initial_age()
        self.spender_prof = np.random.choice(['Average', 'Big Spender', 'Small Spender'], p=[0.5, 0.3, 0.2])
        self.student_and_career_path_check()
        self.initial_income()
        self.initial_balance()
        self.loan = 0
        self.loan_term = 0
        self.married = False
        self.history = []

    def initial_age(self):
        self.age = np.random.randint(0, 95)

    def student_and_career_path_check(self):
        if self.age < 18:
            self.career = 'Cannot Work'
        elif 18 <= self.age < 25:
            self.initial_student_years_of_grad(mode='Could be Student')
        else:
            self.initial_career()
            self.initial_student_years_of_grad(mode="Graduated")

    def initial_student_years_of_grad(self, mode='Could be Student'):
        if mode == 'Could be Student':
            self.future_career = np.random.choice(['Base', 'Medium', 'High', 'Very High'], p=[0.4, 0.3, 0.2, 0.1])
            years_of_grad = self.age - 18 + years_of_study[self.future_career]

            if years_of_grad >= 0:
                self.career = self.future_career
            else:
                self.career = 'Student'
                if years_of_grad < 0:
                    years_of_grad = 0

        else:
            years_of_grad = self.age - 18 + years_of_study[self.career]
        return years_of_grad

    def childhood_savings(self):
        childhood_years = min(self.age, 17)
        savings = np.random.normal(500, 500, childhood_years).sum()
        return savings

    def part_time_job(self):
        if self.age < 18:
            part_time_years = 0
        elif 18 <= self.age < 25 and self.career == 'Student':
            part_time_years = self.age - 18
        else:
            part_time_years = years_of_study[self.career] - 1
        earnings = np.random.normal(10000, 5000, part_time_years).sum() * (1 - spender_profile[self.spender_prof])
        return earnings

    def full_time_job_static(self):
        if self.age < 18 or (18 <= self.age < 25 and self.career == 'Student'):
            full_time_years = 0
        else:
            full_time_years = self.age - years_of_study[self.career] - 18
        earnings = self.income * (1 - spender_profile[self.spender_prof]) * full_time_years
        return earnings

    def initial_balance(self):
        self.balance = self.childhood_savings() + self.part_time_job() + self.full_time_job_static()

    def initial_career(self):
        if 25 <= self.age < 35:
            self.career = np.random.choice(['Base', 'Medium', 'High'], p=[0.5, 0.4, 0.1])
        elif 35 <= self.age < 55:
            self.career = np.random.choice(['Base', 'Medium', 'High', 'Very High'], p=[0.3, 0.4, 0.2, 0.1])
        else:
            self.career = np.random.choice(['Base', 'Medium', 'High', 'Very High'], p=[0.4, 0.3, 0.2, 0.1])

    def initial_income(self):
        if self.career == 'Student' or self.career == 'Cannot Work':
            self.income = 0
        else:
            if self.career == 'Base':
                self.income = np.random.normal(30000, 5000)
            elif self.career == 'Medium':
                self.income = np.random.normal(60000, 10000)
            elif self.career == 'High':
                self.income = np.random.normal(100000, 20000)
            else:
                self.income = np.random.normal(200000, 40000)

    def student_loan(self):
        if self.career == 'Student':
            self.loan = tuition[self.future_career] * years_of_study[self.future_career]
            self.loan_term = np.random.randint(5, 20)
        else:
            self.loan = 0
            self.loan_term = 0

    def pay_loan(self):
        if self.loan > 0 and self.loan_term > 0:
            monthly_payment = self.loan / (self.loan_term * 12)
            self.balance -= monthly_payment
            self.loan -= monthly_payment
            if self.loan < 0:
                self.balance += abs(self.loan)
                self.loan = 0
        else:
            self.loan_term = 0

    def promotion(self):
        if self.career != 'Student' and self.career != 'Cannot Work':
            if np.random.random() < 0.1:
                if self.career == 'Base':
                    self.career = 'Medium'
                    self.income = np.random.normal(60000, 10000)
                elif self.career == 'Medium':
                    self.career = 'High'
                    self.income = np.random.normal(100000, 20000)
                elif self.career == 'High':
                    self.career = 'Very High'
                    self.income = np.random.normal(200000, 40000)

    def work(self):
        if self.career != 'Student' and self.career != 'Cannot Work':
            self.balance += self.income * (1 - spender_profile[self.spender_prof])

    def spend(self):
        if self.balance > 0:
            self.balance -= self.income * spender_profile[self.spender_prof]
            if self.balance < 0:
                self.balance = 0

    def marriage_chance(self):
        if self.age >= 18 and self.married == False:
            if self.career == 'Student':
                chance = 0.1
            elif self.career == 'Cannot Work':
                chance = 0.15
            elif self.career == 'Base':
                chance = 0.3
            elif self.career == 'Medium':
                chance = 0.35
            elif self.career == 'High':
                chance = 0.5
            else:
                chance = 0.0
            if np.random.random() < chance:
                self.marriage()
                _, total_cost = self.calculate_marriage_cost()
                self.balance -= total_cost
   
                
    def calculate_marriage_cost(self):
        # Average cost per person
        avg_cost_per_person = 34000 / 100  # assuming average 100 guests
        
        # Randomize number of guests, more concentrated on 50 to 100
        guests = np.random.normal(loc=75, scale=20).astype(int)
        guests = np.clip(guests, 50, 300)
        
        # Calculate cost based on random additional percentage up to 40%
        additional_percentage = np.random.uniform(0, 0.4)
        cost_per_person = avg_cost_per_person * (1 + additional_percentage)
        total_cost = guests * cost_per_person
        
        return guests, total_cost


    def marriage(self):
        if self.age >= 18 and self.married == False:
            if self.gender == "Male":
                spouse_gender = 'Female' if np.random.random() < 0.75 else 'Male'
            else:
                spouse_gender = 'Male' if np.random.random() < 0.75 else 'Female'
            spouse = Person(spouse_gender)
            spouse.married = True
            self.spouse = spouse
            self.married = True
            self.update_history()

    def age_up(self):
        self.age += 1
        if self.age >= 18:
            if self.career == 'Student':
                years_of_grad = self.initial_student_years_of_grad()
                if years_of_grad <= 0:
                    self.career = self.future_career
                    self.initial_income()
            self.pay_loan()
            self.promotion()
            self.work()
            self.spend()
            self.marriage_chance()
            
        self.update_history()

    def update_history(self):
        self.history.append({'Age': self.age,
                             'Career': self.career,
                             'Income': self.income,
                             'Loan': self.loan,
                             'Loan Term': self.loan_term,
                             'Balance': self.balance,
                             'Married': self.married})

    def run_life(self):
        while self.age < 95:
            self.age_up()


        ...

    def age_up(self):
        self.age += 1
        self.update_history()
        if self.age >= 18 and self.married == False:
            self.marriage()
        if self.married and np.random.rand() <= 0.05:
            self.have_child()
        ...



    def have_child(self):
        if self.gender == 'Female':
            mother = self
        else:
            mother = self.spouse

        age = mother.age
        education_level = {'Base': 1.2, 'Medium': 1, 'High': 0.8, 'Very High': 0.5}
        education_factor = education_level[mother.career]

        if age <= 28:
            base_prob = 0.5
        else:
            base_prob = 0.5 * np.exp(-0.1 * (age - 28))

        # Reduce probability with number of children
        child_factor = np.exp(-0.5 * len(self.children))

        # Calculate final probability
        prob = base_prob * child_factor * education_factor

        if np.random.random() < prob:
            child = Person(np.random.choice(['Male', 'Female']))
            self.children.append(child)

    ...



