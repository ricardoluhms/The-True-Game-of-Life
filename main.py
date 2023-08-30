import numpy as np
import pandas as pd
from collections import defaultdict
import random
years_of_study = {'Base': 2, 'Medium': 3, 'High': 5, 'Very High': 7}
tuition = {'Base': 1000, 'Medium': 3000, 'High': 6000, 'Very High': 10000}
spender_profile = {'Average': 0.9, 'Big Spender': 1.05, 'Small Spender': 0.75}

class Person:
    def __init__(self, gender, age_range=None):
        self.gender = gender
        self.initial_age(age_range)
        self.spender_prof = np.random.choice(['Average', 'Big Spender', 'Small Spender'], p=[0.5, 0.3, 0.2])
        self.student_and_career_path_check()
        self.initial_income()
        self.initial_balance()
        self.loan = 0
        self.loan_term = 0
        self.married = False
        self.history = []
        self.children = []

    def initial_age(self, age_range=None):
        if age_range == 'Baby':
            self.age = np.random.randint(0, 2)
        elif age_range == 'Child':
            self.age = np.random.randint(2, 13)
        elif age_range == 'Teenager':
            self.age = np.random.randint(13, 18)
        elif age_range == 'Young Adult':
            self.age = np.random.randint(18, 25)
        elif age_range == 'Adult':
            self.age = np.random.randint(25, 65)
        elif age_range == 'Elder':
            self.age = np.random.randint(65, 96)
        else:
            ### raise error if age_range is not specified
            raise ValueError('age_range is not specified')
        self.age_range = age_range

    def update_age_range(self):
        if 0 <= self.age <= 1:
            age_range = 'Baby'
        elif 2 <= self.age <= 12:
            age_range = 'Child'
        elif 13 <= self.age <= 17:
            age_range = 'Teenager'
        elif 18 <= self.age <= 24:
            age_range = 'Young Adult'
        elif 25 <= self.age <= 64:
            age_range = 'Adult'
        else:
            age_range = 'Elder'
        self.age_range = age_range

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
        if self.loan > 0:
            self.balance = self.childhood_savings() + self.part_time_job() + self.full_time_job_static() - self.loan
        else:        
            self.balance = self.childhood_savings() + self.part_time_job() + self.full_time_job_static()
    
    def initial_career(self):
        if 25 <= self.age < 35:
            self.career = np.random.choice(['Base', 'Medium', 'High'], p=[0.5, 0.4, 0.1])
        elif 35 <= self.age < 55:
            self.career = np.random.choice(['Base', 'Medium', 'High', 'Very High'], p=[0.3, 0.4, 0.2, 0.1])
        else:
            self.career = np.random.choice(['Base', 'Medium', 'High', 'Very High'], p=[0.4, 0.3, 0.2, 0.1])

    def initial_income(self, gender_bias=None):
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
        if gender_bias and self.gender == 'Female':
            ### multiply by a random number between 0.8 and 1.0
            self.income *= np.random.uniform(0.8, 1.0)

    def student_loan(self):
        if self.career == 'Student':
            total_tuition = tuition[self.future_career] * years_of_study[self.future_career]
            # Amount to be paid by loan
            loan_required = total_tuition - self.balance
            
            if loan_required <= 0:
                self.balance -= total_tuition
                self.loan = 0
                self.loan_term = 0
            else:
                self.loan = loan_required
                self.loan_term = np.random.randint(5, 20)
                self.balance = 0  # all money used to pay part of the tuition
        else:
            self.loan = 0
            self.loan_term = 0

    def composed_interest(self, principal_loan_amount, interest_rate, loan_term=10):
        loan_term = 10  # assume a fixed loan term
        # compound interest formula: A = P (1 + r/n)^(nt)
        # where: 
        # A = the money accumulated after n years, including interest.
        # P = principal amount (the initial money before interest)
        # r = annual interest rate (in decimal form)
        # n = number of times that interest is compounded per year
        # t = the time the money is invested for, in years
        n = 1  # assume the interest is compounded annually
        compound_loan_amount = principal_loan_amount * (1 + interest_rate/n)**(n*loan_term)
        return compound_loan_amount

    def get_loan(self, interest_rate=None, desired_loan_amount=None, loan_term_years=10):
        # Set Interest Rate
        if interest_rate is None:
            interest_rate = random.uniform(0.02, 0.12)

        # Check Income
        if self.married:
            total_income = self.income + self.spouse.income
        else:
            total_income = self.income

        # Check Current Loan(s)
        if self.married and self.loan > 0 and self.spouse.loan > 0:
            current_loan_amount = self.loan + self.spouse.loan + desired_loan_amount
        elif self.married and self.loan > 0:
            current_loan_amount = self.loan + desired_loan_amount
        elif self.married and self.spouse.loan > 0:
            current_loan_amount = self.spouse.loan + desired_loan_amount
        elif self.loan > 0:
            current_loan_amount = self.loan + desired_loan_amount
        else:
            current_loan_amount = desired_loan_amount   
        
        # Check max loan amount
        max_loan_amount = total_income * 0.45 if not self.student else total_income * 0.50
        desired_loan_amount = max_loan_amount - current_loan_amount
        
        if current_loan_amount > max_loan_amount:
            # warning message without raising error
            print('You cannot get more loans. You have reached the maximum loan amount.')
            return None
        else:
            # calculate the compounded interest
            future_value = desired_loan_amount * ((1 + interest_rate)**loan_term_years)
            future_value = self.composed_interest(desired_loan_amount, interest_rate, loan_term_years)
            yearly_payment = future_value / loan_term_years
            
            if self.married:
                self.loan = future_value / 2
                self.spouse.loan = future_value / 2
                self.loan_yearly_payment = yearly_payment / 2
                self.spouse.loan_yearly_payment = yearly_payment / 2
                self.loan_term = loan_term_years
                self.spouse.loan_term = loan_term_years
            else:
                self.loan = future_value
                self.loan_yearly_payment = yearly_payment
                self.loan_term = loan_term_years
    
    def pay_loan(self):
        if self.loan > 0 and self.loan_term > 0:
            self.balance -= self.yearly_payment
            self.loan -= self.yearly_payment
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
        # Tax Brackets
        if self.income <= 30000:
           tax = 0.10  # 10% tax
        elif 30000 < self.income <= 50000:
            tax = 0.20  # 20% tax
        elif 50000 < self.income <= 100000:
            tax = 0.30  # 30% tax
        else:
            tax = 0.40  # 30% tax

        if self.career != 'Student' and self.career != 'Cannot Work':
            self.balance += self.income * (1 - spender_profile[self.spender_prof]- tax)

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
            elif self.career == 'Very High':
                chance = 0.8
            else:
                chance = 0.0
            if np.random.random() < chance:
                self.marriage()
                _, marriage_expense = self.calculate_marriage_cost()
                total_balance = self.balance + self.spouse.balance
                if total_balance < marriage_expense:
                    get_loan_status = self.get_loan(desired_loan_amount=marriage_expense-total_balance)
                    if  get_loan_status is None:
                        print('You cannot afford the marriage expense. You have reached the maximum loan amount.')

    def calculate_marriage_cost(self):
        # Average cost per person
        avg_cost_per_person = 34000 / 100  # assuming average 100 guests
        
        # Randomize number of guests, more concentrated on 50 to 100
        guests = np.random.normal(loc=75, scale=20).astype(int)
        guests = np.clip(guests, 25, 300)
        
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
            spouse = Person(spouse_gender,age_range=self.age_range)
            spouse.married = True
            self.spouse = spouse
            self.married = True
            self.update_history()

    def age_up(self):
        self.age += 1
        self.update_age_range()
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
        if self.married and np.random.rand() <= 0.05:
            self.have_child()
        elif self.married == False and self.age >= 18 and np.random.rand() <= 0.025:
            self.have_child()
        self.marriage_chance()
        self.update_history()

    def update_history(self):
        self.history.append({'Age': self.age,
                             'Age Range': self.age_range,
                             'Career': self.career,
                             'Income': self.income,
                             'Loan': self.loan,
                             'Loan Term': self.loan_term,
                             'Balance': self.balance,
                             'Married': self.married,
                             'Children': self.children})

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
### to do
### add buy insurance
### check for life events that could lead to insurance
### add likelihood of getting insurance
### add buy house or rent
### add buy car
### chances of death
### add current year in history

### in city - generate starting population
### in city - if there were life events that adds new people to the city, add them to the city
### check if spouse is randomly generated or not if true then add to city else update relationship
### check for children events and add them to the city
### check for death events and change their status to dead and the year they died
### for kids, add their parents in the relationship list

### create a marketing campaign class
### this class will generate a random list of a subset of the population and send them insurance offers
### if the person is not insured, check if they are targets with high likelihood of getting insurance
### -	Create a unique measure of risk to evaluate if they are going to buy or not insurance.
### We would assume that a normal campaign would have X% of open ratio, 
### ... and Y% out of the X that opened would engage with the website
###	Z% would be the ones that opened, engaged and bought insurance
### this class will keep record of the campaign and the results
### this will count the amount of policies sold and the amount of money made from the campaign
### the campaign will have a cost associated with it based on the number of people targeted
### the campaign will also track the number of people that were eligible for the campaign but were not targeted
### and check if they bought insurance or not 

### a dataset with all the campaigns will be created and will be used to train several models
### customer segmentation clustering
### likelihood of buying insurance
### campaign success prediction
### campaign cost prediction

class City:
    def __init__(self, name):
        self.name = name
        self.citizens = []
        self.relationship_changes = []
        
    def add_citizen(self, person):
        self.citizens.append(person)
        
    def form_relationship(self, person1, person2, relationship):
        person1.form_relationship(person2, relationship)
        self.relationship_changes.append({
            'Person1': person1.name,
            'Person2': person2.name,
            'Relationship': relationship
        })
        
    def get_relationship_changes(self):
        return self.relationship_changes