#### generate a class baby that inherits from person
class Baby(Person):
    ### set age range to baby
    def 



class Adult:
    def __init__(self, gender:str =None, age_range:str=None, first_name = None, last_name = None):
        """ age_range options: 'Baby', 'Child', 'Teenager', 'Young Adult', 'Adult', 'Elder' \n
            gender options: 'Male' or 'Female' """
        if gender is None:
            gender = np.random.choice(GENDER_PROBS.keys(),p=GENDER_PROBS.values())
        self.gender = gender
        if age_range is None:
            age_range = np.random.choice(AGE_RANGE_PROB_DICT.keys(), p=AGE_RANGE_PROB_DICT.values())
        self.initial_age(age_range)
        self.spender_prof = np.random.choice(SPENDER_PROFILE_PROBS.keys(), p=SPENDER_PROFILE_PROBS.values())
        self.loan = 0
        self.loan_term = 0
        self.balance = 0
        self.student_and_career_path_check()
        self.initial_income()
        self.initial_balance()
        self.married = False
        self.history = []
        self.children = []
        self.first_name = first_name;  self.last_name = last_name
        self.generate_full_name()
        self.unique_name_id = self.generate_unique_name_id()
        
    def initial_age(self, age_range=None):#
        if age_range is None:
            self.age = np.random.randint(AGE_RANGES["Baby"][0], AGE_RANGES["Elder"][1])
            self.age_range = self.update_age_range()
        else:
            self.age = np.random.randint(AGE_RANGES[age_range][0], AGE_RANGES[age_range][1])
            self.age_range = age_range

    def update_age_range(self):
        for key, value in AGE_RANGES.items():
            if value[0] <= self.age <= value[1]:
                self.age_range = key
                break

    def student_and_career_path_check(self):
        if self.age < UGRAD_START_AGE:
            self.career = 'Pocket Money'
        elif UGRAD_START_AGE <= self.age < MAX_UGRAD_START_AGE:
            self.initial_student_years_of_grad(mode='Could be UGrad Student')
        else:
            self.initial_career()
            self.initial_student_years_of_grad(mode="Graduated")

    def initial_student_years_of_grad(self, mode='Could be UGrad Student'):
        
        self.future_career = np.random.choice(FUTURE_CAREER_PAY_PROBS.keys(), 
                                            p=FUTURE_CAREER_PAY_PROBS.values())
        years_to_study = YEARS_OF_STUDY[self.future_career]
        year_after_study_start = self.age - UGRAD_START_AGE
        self.years_of_grad = year_after_study_start - YEARS_OF_STUDY[self.future_career] 
        remaining_years = self.years_of_grad*-1

        ## 21 - 18 = 3 year_a..... 3 - 2 = 1  year of grad
        ## 20 - 18 = 2 year_a..... 2 - 2 = 0  year of grad
        ## 19 - 18 = 1 year_a..... 1 - 2 = -1  year of grad

        if mode == 'Could be UGrad Student' and remaining_years > 0:

            self.years_studied = years_to_study - remaining_years
            self.years_to_study = remaining_years
            self.career = 'Student'    
            status = self.career

        else:
            self.years_studied = years_to_study
            self.years_to_study = 0
            self.career = self.future_career
            status = 'Not a Student'

        print(mode,status, self.age, self.years_of_grad)

    def childhood_savings(self): ### review this function
        childhood_years = min(self.age, PART_TIME_JOB_MIN_AGE)
        savings = np.random.normal(500, 500, childhood_years).sum()
        return savings

    def part_time_job(self): ### review this function
        if self.age < PART_TIME_JOB_MIN_AGE:
            part_time_years = 0
        elif UGRAD_START_AGE <= self.age < MAX_UGRAD_START_AGE and self.career == 'Student':
            part_time_years = self.age - UGRAD_START_AGE
        else:
            part_time_years = YEARS_OF_STUDY[self.career] - 1
        earnings = np.random.normal(10000, 5000, part_time_years).sum() * (1 - SPENDER_PROFILE[self.spender_prof])
        return np.round(earnings,2)

    def full_time_job_static(self):
        if self.age < 18 or (18 <= self.age < 25 and self.career == 'Student'):
            full_time_years = 0
        else:
            full_time_years = self.age - YEARS_OF_STUDY[self.career] - 18
        earnings = self.income * (1 - SPENDER_PROFILE[self.spender_prof]) * full_time_years
        return np.round(earnings, 2)

    def initial_balance(self):
        if self.loan > 0:
            self.balance = self.childhood_savings() + self.part_time_job() + self.full_time_job_static() - self.loan
        else:        
            self.balance = self.childhood_savings() + self.part_time_job() + self.full_time_job_static()
        self.balance = np.round(self.balance, 2)

    def initial_career(self):### to test this function
        for age_val in INITIAL_CAREER_PROBS_BY_AGE.keys():
            if self.age <= age_val:
                self.career = np.random.choice(list(INITIAL_CAREER_PROBS_BY_AGE[age_val].keys()), 
                                            p=list(INITIAL_CAREER_PROBS_BY_AGE[age_val].values()))
                break
            else:
                self.career = "Retired" ### Later we will add a function to handle retirement

    def initial_income(self, gender_bias=None):### to test this function
        if self.age < PART_TIME_JOB_MIN_AGE:
            self.income = 0
        else:
            self.income = np.random.normal(INITIAL_INCOME_RANGES[self.career][0], 
                                        INITIAL_INCOME_RANGES[self.career][1])
        
        if gender_bias and self.gender == 'Female':
            ### multiply by a random number between 0.8 and 1.0
            self.income *= np.random.uniform(0.8, 1.0)
        self.income = np.round(self.income, 2)

    def student_loan(self, interest_rate=None, loan_term_years=10)### review this function:
        
        ### Tuition due
        tuition_due = TUITION[self.future_career] * self.years_studied
        
        if interest_rate is None:
            self.interest_rate = random.uniform(0.02, 0.06)

        # Subtract tuition from balance
        self.balance -= tuition_due

        if self.balance > 0:
            ### Student has enough money to pay for the tuition
            self.loan = 0
            self.loan_term = 0
        else:
            ### Student does not have enough money to pay for the tuition and
            ### ... will need to get a loan on the remaining balance
            self.loan_term = loan_term_years + self.years_to_study
            self.loan = abs(self.balance) * (1 + self.interest_rate)**(self.loan_term)

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
            self.interest_rate = random.uniform(0.02, 0.12)

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
            future_value = desired_loan_amount * ((1 + self.interest_rate)**loan_term_years)
            future_value = self.composed_interest(desired_loan_amount, self.interest_rate, loan_term_years)
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
        if self.career != 'Student' and self.career != 'Pocket Money':
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

        if self.career != 'Student' and self.career != 'Pocket Money':
            self.balance += self.income * (1 - SPENDER_PROFILE[self.spender_prof]- tax)

    def marriage_chance(self):
        if self.age >= 18 and self.married == False:
            if self.career == 'Student':
                chance = 0.1
            elif self.career == 'Pocket Money':
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
        ### check if person is already in the city
        ### if not, add them to the city
        citizen_check = [person.name for person in self.citizens]
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
# %%
