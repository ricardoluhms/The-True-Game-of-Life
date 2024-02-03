MALE_FIRST_NAMES = ['Aaron', 'Adam', 'Alan', 'Albert', 'Alexander', 'Andrew', 'Anthony', 'Arthur', 'Austin', 'Benjamin', 'Billy',
                    'Bobby', 'Bradley', 'Brandon', 'Brian', 'Bruce', 'Bryan', 'Carl', 'Charles', 'Christian', 'Christopher',
                    'Daniel', 'David', 'Dennis', 'Donald', 'Douglas', 'Dylan', 'Edward', 'Eric', 'Ethan', 'Eugene', 'Frank', 'Gabriel',
                    'Gary', 'George', 'Gerald', 'Gregory', 'Harold', 'Harry', 'Henry', 'Jack', 'Jacob', 'James', 'Jason', 'Jeffrey',
                    'Jeremy', 'Jerry', 'Jesse', 'Joe', 'John', 'Johnny', 'Jonathan', 'Jordan', 'Jose', 'Joseph', 'Joshua', 'Juan', 'Justin',
                    'Keith', 'Kenneth', 'Kevin', 'Kyle', 'Larry', 'Lawrence', 'Logan', 'Louis', 'Mark', 'Matthew', 'Michael', 
                    'Nathan', 'Nicholas', 'Noah', 'Patrick', 'Paul', 'Peter', 'Philip', 'Ralph', 'Randy', 'Raymond', 'Richard', 'Robert',
                    'Roger', 'Ronald', 'Roy', 'Russell', 'Ryan', 'Samuel', 'Scott', 'Sean', 'Stephen', 'Steven', 'Terry', 'Thomas', 'Timothy',
                    'Tyler', 'Vincent', 'Walter', 'Wayne', 'William', 'Willie', 'Zachary']

### add list of 100 most common female names

FEMALE_FIRST_NAMES = ['Abigail', 'Alexis', 'Alice', 'Amanda', 'Amber', 'Amy', 'Andrea', 'Angela', 'Ann', 'Anna', 'Ashley', 'Barbara', 'Betty',
                'Beverly', 'Brenda', 'Brittany', 'Carol', 'Carolyn', 'Catherine', 'Cheryl', 'Christina', 'Christine', 'Cynthia', 'Danielle',
                'Deborah', 'Debra', 'Denise', 'Diana', 'Diane', 'Donna', 'Doris', 'Dorothy', 'Elizabeth', 'Emily', 'Emma', 'Evelyn', 'Frances',
                'Gloria', 'Grace', 'Hannah', 'Heather', 'Helen', 'Jacqueline', 'Jane', 'Janet', 'Janice', 'Jean', 'Jennifer', 'Jessica', 'Joan',
                'Joyce', 'Judith', 'Judy', 'Julia', 'Julie', 'Karen', 'Katherine', 'Kathleen', 'Kathryn', 'Kayla', 'Kelly', 'Kimberly', 'Laura',
                'Lauren', 'Linda', 'Lisa', 'Lori', 'Madison', 'Margaret', 'Maria', 'Marie', 'Marilyn', 'Martha', 'Mary', 'Megan', 'Melissa', 'Michelle',
                'Nancy', 'Natalie', 'Nicole', 'Olivia', 'Pamela', 'Patricia', 'Rachel', 'Rebecca', 'Rose', 'Ruth', 'Samantha', 'Sandra', 'Sara',
                'Sarah', 'Sharon', 'Shirley', 'Sophia', 'Stephanie', 'Susan', 'Teresa', 'Theresa', 'Victoria', 'Virginia']

### add list of 100 most common last names in alphabetical order

LAST_NAMES = ['Adams', 'Alexander', 'Allen', 'Anderson', 'Bailey', 'Baker', 'Barnes', 'Bell', 'Bennett', 'Brooks', 'Brown', 'Bryant', 'Butler',
                'Campbell', 'Carter', 'Clark', 'Coleman', 'Collins', 'Cook', 'Cooper', 'Cox', 'Davis', 'Diaz', 'Edwards', 'Evans', 'Flores', 'Foster',
                'Garcia', 'Gonzales', 'Gonzalez', 'Gray', 'Green', 'Griffin', 'Hall', 'Harris', 'Hayes', 'Henderson', 'Hernandez', 'Hill', 'Howard',
                'Hughes', 'Jackson', 'James', 'Jenkins', 'Johnson', 'Jones', 'Kelly', 'King', 'Lee', 'Lewis', 'Long', 'Lopez', 'Martin', 'Martinez',
                'Miller', 'Mitchell', 'Moore', 'Morgan', 'Morris', 'Murphy', 'Nelson', 'Parker', 'Patterson', 'Perez', 'Perry', 'Peterson', 'Phillips',
                'Powell', 'Price', 'Ramirez', 'Reed', 'Richardson', 'Rivera', 'Roberts', 'Robinson', 'Rodriguez', 'Rogers', 'Ross', 'Russell', 'Sanchez',
                'Sanders', 'Scott', 'Simmons', 'Smith', 'Stewart', 'Taylor', 'Thomas', 'Thompson', 'Torres', 'Turner', 'Walker', 'Ward', 'Washington',
                'Watson', 'White', 'Williams', 'Wilson', 'Wood', 'Wright', 'Young']

YEARS_OF_STUDY = {'Base': 2, 'Medium': 3, 'High': 5, 'Very High': 7}
TUITION = {'Base': 6000, 'Medium': 10000, 'High': 18000, 'Very High': 25000} ### yearly values

# undergraduate programs were approximately CAD 6,500 per year for Canadian students
# Dentistry: CAD 18,000 - CAD 25,000
# Medicine: CAD 15,000 - CAD 22,000
# Pharmacy: CAD 10,000 - CAD 17,000
# Engineering: CAD 9,000 - CAD 15,000 (depending on the specialization and institution)
# Business & Commerce: CAD 8,000 - CAD 14,000 (higher for specialized or top-ranked 
# MBA (Master of Business Administration): CAD 20,000 - CAD 40,000

SPENDER_PROFILE = {'Average': 0.9, 'Big Spender': 1.05, 'Small Spender': 0.75, 'In-Debt': 0.5, 'Depressed': 0.4}
SPENDER_PROFILE_SWITCH_PROB = 0.5
### special profile for those who are in debt


SPENDER_PROFILE_PROBS = {'Average': 0.5,
                        'Big Spender': 0.3,
                        'Small Spender': 0.2}

PART_TIME_JOB_MIN_AGE = 16
PART_TIME_JOB_PROB = 0.5
UGRAD_START_AGE = 18
MAX_UGRAD_START_AGE = 18 + max(YEARS_OF_STUDY.values())

AGE_RANGES = {'Baby': [0, 2], 
              'Child': [3, 12], 
              'Teenager': [13, 17], 
              'Young Adult': [18, 25], 
              'Adult': [26, 65], 
              'Elder': [66, 96]}

AGE_RANGE_PROB_DICT = {'Baby': 0.1,
                        'Child': 0.2,
                        'Teenager': 0.2,
                        'Young Adult': 0.2,
                        'Adult': 0.2,
                        'Elder': 0.1}

GENDER_PROBS = {'Male': 0.5,
                'Female': 0.5}                   

CAR_FINANCING_OPTION_PROBS = {'Self-Financing': 0.1,
                            'Car Loan': 0.9}


FUTURE_CAREER_PAY_PROBS = {'Base': 0.4,
                           'Medium': 0.4,
                           'High': 0.1,
                           'Very High': 0.1}

INITIAL_INCOME_RANGES = {'Pocket Money': [500,500],
                         'Part Time': [10000, 5000],
                         'Base': [30000, 5000],
                         'Medium': [60000, 10000],
                         'High': [100000, 20000],
                         'Very High': [200000, 40000],
                         'Retired': [75000, 55000]}

INITIAL_CAREER_PROBS_BY_AGE = { 25: {'Base': 0.5, 'Medium': 0.4, 'High': 0.09, 'Very High': 0.01},
                                35: {'Base': 0.3, 'Medium': 0.4, 'High': 0.2, 'Very High': 0.1},
                                55: {'Base': 0.4, 'Medium': 0.3, 'High': 0.2, 'Very High': 0.1},
                                75: {'Base': 0.5, 'Medium': 0.3, 'High': 0.1, 'Very High': 0.1}}

# Something like the above dict, can be created to handel diffrent ages 
# if age is 18 - 22 
BASE_DEBT_RATIO = 0.45

### REWRITE CAR_MAX_DEBT_RATIO TO USE CAR_BASE_DEBT_VALUE and to be a function of Age and Spender Profile

MAX_DEBT_RATIO = {"Bucket 1": {"Age Range": [18, 25], "Max Debt to Income Ratio": {"Big Spender": BASE_DEBT_RATIO, 
                                                                                       "Average": BASE_DEBT_RATIO*0.85, 
                                                                                       "Small Spender": BASE_DEBT_RATIO*0.7}},
                        "Bucket 2": {"Age Range": [26, 35], "Max Debt to Income Ratio": {"Big Spender": BASE_DEBT_RATIO*0.9,
                                                                                        "Average": BASE_DEBT_RATIO*0.75,
                                                                                        "Small Spender": BASE_DEBT_RATIO*0.6}},
                        "Bucket 3": {"Age Range": [36, 45], "Max Debt to Income Ratio": {"Big Spender": BASE_DEBT_RATIO*0.8,
                                                                                        "Average": BASE_DEBT_RATIO*0.65,
                                                                                        "Small Spender": BASE_DEBT_RATIO*0.5}},
                        "Bucket 4": {"Age Range": [46, 55], "Max Debt to Income Ratio": {"Big Spender": BASE_DEBT_RATIO*0.7,
                                                                                        "Average": BASE_DEBT_RATIO*0.55,
                                                                                        "Small Spender": BASE_DEBT_RATIO*0.4}},
                        "Bucket 5": {"Age Range": [56, 65], "Max Debt to Income Ratio": {"Big Spender": BASE_DEBT_RATIO*0.6,
                                                                                        "Average": BASE_DEBT_RATIO*0.45,
                                                                                        "Small Spender": BASE_DEBT_RATIO*0.3}},
                        "Bucket 6": {"Age Range": [66, 75], "Max Debt to Income Ratio": {"Big Spender": BASE_DEBT_RATIO*0.5,
                                                                                        "Average": BASE_DEBT_RATIO*0.35,
                                                                                        "Small Spender": BASE_DEBT_RATIO*0.2}},
                        "Bucket 7": {"Age Range": [76, 100], "Max Debt to Income Ratio": {"Big Spender": BASE_DEBT_RATIO*0.4,
                                                                                        "Average": BASE_DEBT_RATIO*0.25,
                                                                                        "Small Spender": BASE_DEBT_RATIO*0.1}}}

PRIME_RATE = 4 # 4% prime rate

INTEREST_RATE_PER_TYPE = {"Student Loan": 2 + PRIME_RATE,
                            "Car Loan": 3.21 + PRIME_RATE,
                            "Mortgage": 3 + PRIME_RATE,
                            "Personal Loan": 5 + PRIME_RATE}

LOAN_TERM_PER_TYPE = {"Student Loan": [10, 15],
                        "Car Loan": [2,5],
                        "Mortgage": [15, 30],
                        "Personal Loan": [1, 5]}


CAREERS_AND_MARRIAGE_PROBS = {"Student with Part Time Job": 0.08,
                              "Student with Pocket Money": 0.005,
                              'Pocket Money': 0.001,
                              'Part Time': 0.002,
                              'Base': 0.2,
                              'Medium': 0.3,
                              'High': 0.4,
                              'Very High': 0.3}

STUDENT_LOAN_INTEREST_RATES = [0.02, 0.07]

CAR_DOWNPAYMENT_CONSTANT = 3000

CAR_SELF_FINANCING_CONSTANT= [10000,20000,70000]




MIN_MARRIAGE_ALLOWED_AGE = 16 ### Canada

SAME_GENDER_MARRIAGE_RATIO = 0.25
AVG_MARRIAGE_COST_PER_GUEST = 34000 / 100

BABY_TWINS_MODE = {1:0.949, 2:0.04, 3:0.01, 4:0.001}

EXISTING_CHILDREN_PROB_DICT = {0: 0.0, 1: 0.1, 2: 0.15, 3: 0.25, 4: 0.35, 5: 0.4, 6: 0.5, 7: 0.5, 8: 0.5, 9: 0.5}

### create a function that generates a random value given a base value and a deviation

RAISE_DEVIATION = 0.5

# RAISE_CONSTANT_DICT = {"Base": {"chance": 0.1, "hike": 0.1},
#                         "Medium": {"chance": 0.2, "hike": 0.2},
#                         "High": {"chance": 0.3, "hike": 0.3},
#                         "Very High": {"chance": 0.4, "hike": 0.4}}
# RAISE_DEVIATION_BY_AGE = {[18, 25]: 0.5,
#                             [26, 35]: 0.4,
#                             [36, 45]: 0.3,
#                             [46, 55]: 0.2,
#                             [56, 65]: 0.1,
#                             [66, 75]: 0.05,
#                             [76, 100]: 0.01}

# def fetch_raise_constant_by_age(age):
#     for age_range in RAISE_DEVIATION_BY_AGE.keys():
#         if age in range(age_range[0], age_range[1]):
#             RAISE_DEVIATION = RAISE_DEVIATION_BY_AGE[age_range]
#             break

#     return RAISE_DEVIATION

# def get_a_raise(current_salary, raise_ratio, career_path, age):


#     ### raise chance

#     raise_prob = RAISE_CONSTANT_DICT[career_path]["chance"]

#     if np.random.uniform(0,1) > raise_prob:

#         for age_range in RAISE_DEVIATION_BY_AGE.keys():
#             if age in range(age_range[0], age_range[1]):
#                 RAISE_DEVIATION = RAISE_DEVIATION_BY_AGE[age_range]
#                 break

#         base_rase_rate = RAISE_CONSTANT_DICT[career_path]["hike"]
#         random_rate = generate_random_value(base_rase_rate, RAISE_DEVIATION)
#         if random_rate < 0:
#             random_rate = RAISE_DEVIATION
#         new_salary = current_salary + current_salary *random_rate
        



#     ### raise amount
#     return current_salary + current_salary * raise_ratio

# def generate_random_value(base_value, deviation):
#     return base_value + np.random.uniform(-deviation, deviation)