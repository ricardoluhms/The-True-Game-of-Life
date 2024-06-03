import pandas as pd
### Name Generation Constants
if True:
    MALE_FIRST_NAMES = ['Aaron', 'Abel', 'Abraham', 'Adam', 'Adan', 'Adolfo', 'Adrian', 'Agustin', 'Alan', 'Albert', 
                        'Alberto', 'Alejandro', 'Alex', 'Alexander', 'Alfonso', 'Alfredo', 'Allan', 'Alonso', 'Alvaro',
                        'Alvin', 'Amado', 'Amador', 'Ambrosio', 'Amos', 'Andres', 'Andrew', 'Angel', 'Anthony', 
                        'Antonio', 'Armando', 'Arnold', 'Arthur', 'Arturo', 'Augustine', 'Augusto', 'Austin', 'Benito', 
                        'Benjamin', 'Bernardo', 'Billy', 'Bobby', 'Bradley', 'Brandon', 'Brendan', 'Brian', 'Bruce', 
                        'Bryan', 'Byron', 'Caleb', 'Calvin', 'Carl', 'Carlos', 'Carmelo', 'Cesar', 'Charles', 'Charlie',
                        'Chris', 'Christian', 'Christopher', 'Clarence', 'Claudio', 'Clemente', 'Cody', 'Colin', 
                        'Conrad', 'Cristian', 'Cristobal', 'Cruz', 'Damian', 'Damien', 'Daniel', 'Dante', 'Dario', 
                        'Darren', 'David', 'Dean', 'Dennis', 'Derek', 'Diego', 'Domingo', 'Dominic', 'Donald', 
                        'Donovan', 'Dorian', 'Douglas', 'Drew', 'Duane', 'Dustin', 'Dwayne', 'Dwight', 'Dylan', 
                        'Edgar', 'Edison', 'Eduardo', 'Edward', 'Edwin', 'Efrain', 'Elias', 'Elijah', 'Emanuel', 
                        'Emilio', 'Emmanuel', 'Enrique', 'Eric', 'Erick', 'Ernest', 'Ernesto', 'Esteban', 
                        'Ethan', 'Eugene', 'Evan', 'Everett', 'Ezequiel', 'Ezra', 'Federico', 'Felipe', 'Felix', 
                        'Fernando', 'Fidel', 'Francisco', 'Frank', 'Franklin', 'Freddie', 'Freddy', 'Frederick', 
                        'Gabriel', 'Gael', 'Garry', 'Gary', 'Gavin', 'Genaro', 'Geoffrey', 'George', 'Gerald', 
                        'Gerard', 'German', 'Gilbert', 'Gilberto', 'Giovanni', 'Gonzalo', 'Gordon', 'Gregorio', 
                        'Gregory', 'Guadalupe', 'Guillermo', 'Gustavo', 'Harold', 'Harry', 'Hector', 'Henry', 
                        'Herbert', 'Herman', 'Hernan', 'Hilario', 'Hiram', 'Homer', 'Horacio', 'Hugo', 'Ian', 
                        'Ignacio', 'Irving', 'Isaac', 'Isaias', 'Isidro', 'Ismael', 'Jack', 'Jacob', 'James', 
                        'Jason', 'Jeffrey', 'Jeremy', 'Jerry', 'Jesse', 'Joe', 'John', 'Johnny', 'Jonathan', 
                        'Jordan', 'Jose', 'Joseph', 'Joshua', 'Juan', 'Justin', 'Keith', 'Kenneth', 'Kevin', 
                        'Kyle', 'Larry', 'Lawrence', 'Logan', 'Louis', 'Mark', 'Matthew', 'Michael', 'Nathan', 
                        'Nicholas', 'Noah', 'Patrick', 'Paul', 'Peter', 'Philip', 'Ralph', 'Randy', 'Raymond', 
                        'Richard', 'Robert', 'Roger', 'Ronald', 'Roy', 'Russell', 'Ryan', 'Samuel', 'Scott', 
                        'Sean', 'Stephen', 'Steven', 'Terry', 'Thomas', 'Timothy', 'Tyler', 'Vincent', 'Walter', 
                        'Wayne', 'William', 'Willie', 'Zachary']

    FEMALE_FIRST_NAMES = ['Abigail', 'Adriana', 'Alejandra', 'Alexis', 'Alice', 'Alicia', 'Amanda', 
                          'Amber', 'Amy', 'Ana', 'Andrea', 'Angela', 'Angelica', 'Ann', 'Anna', 
                          'Antonia', 'Ashley', 'Aurora', 'Barbara', 'Beatriz', 'Betty', 'Beverly', 
                          'Blanca', 'Brenda', 'Brittany', 'Carmen', 'Carol', 'Carolina', 'Carolyn', 
                          'Catalina', 'Catherine', 'Cecilia', 'Cheryl', 'Christina', 'Christine', 
                          'Clara', 'Claudia', 'Concepcion', 'Consuelo', 'Cristina', 'Cynthia', 
                          'Danielle', 'Deborah', 'Debra', 'Denise', 'Diana', 'Diane', 'Dolores', 
                          'Donna', 'Doris', 'Dorothy', 'Elena', 'Elisa', 'Elizabeth', 'Elsa', 'Emilia', 
                          'Emily', 'Emma', 'Esperanza', 'Estela', 'Esther', 'Eva', 'Evelyn', 'Fernanda', 
                          'Frances', 'Francisca', 'Gabriela', 'Gloria', 'Grace', 'Graciela', 'Guadalupe', 
                          'Hannah', 'Heather', 'Helen', 'Hilda', 'Ines', 'Irene', 'Isabel', 'Isabela', 
                          'Jacqueline', 'Jane', 'Janet', 'Janice', 'Jean', 'Jennifer', 'Jessica', 'Joan', 
                          'Josefina', 'Joyce', 'Juana', 'Judith', 'Judy', 'Julia', 'Julie', 'Karen', 
                          'Katherine', 'Kathleen', 'Kathryn', 'Kayla', 'Kelly', 'Kimberly', 'Laura', 
                          'Lauren', 'Leticia', 'Lilia', 'Liliana', 'Linda', 'Lisa', 'Lorena', 'Lori', 
                          'Lourdes', 'Lucia', 'Luisa', 'Luz', 'Madison', 'Magdalena', 'Manuela', 
                          'Margaret', 'Margarita', 'Maria', 'Mariana', 'Maricela', 'Marie', 'Marilyn', 
                          'Marisol', 'Marta', 'Martha', 'Mary', 'Megan', 'Melissa', 'Mercedes', 'Micaela', 
                          'Michelle', 'Migdalia', 'Miguelina', 'Mireya', 'Monica', 'Nancy', 'Natalia', 
                          'Natalie', 'Nicole', 'Norma', 'Olga', 'Olivia', 'Pamela', 'Patricia', 'Paula', 
                          'Pilar', 'Rachel', 'Raquel', 'Rebeca', 'Rebecca', 'Reina', 'Rosa', 'Rosalia', 
                          'Rosario', 'Rose', 'Ruth', 'Samantha', 'Sandra', 'Sara', 'Sarah', 'Sharon', 
                          'Shirley', 'Silvia', 'Sofia', 'Soledad', 'Sonia', 'Sophia', 'Stephanie', 'Susan', 
                          'Susana', 'Teresa', 'Theresa', 'Veronica', 'Victoria', 'Virginia', 'Yolanda', 
                          'Yvette', 'Yvonne', 'Zoraida']

    LAST_NAMES = ['Adams', 'Alexander', 'Allen', 'Alvarez', 'Anderson', 'Andrade', 'Arango', 'Arias', 
                  'Arroyo', 'Avila', 'Bailey', 'Baker', 'Barnes', 'Becerra', 'Bell', 'Bennett', 
                  'Bermudez', 'Bonilla', 'Brooks', 'Brown', 'Bryant', 'Bustamante', 'Butler', 
                  'Cabrera', 'Calderon', 'Camacho', 'Campbell', 'Cardenas', 'Caro', 'Carrillo', 
                  'Carter', 'Castillo', 'Castro', 'Cedillo', 'Cervantes', 'Chavez', 'Cisneros', 
                  'Clark', 'Coleman', 'Collins', 'Contreras', 'Cook', 'Cooper', 'Cortes', 'Cox', 
                  'Cruz', 'Davis', 'Delgado', 'Diaz', 'Duarte', 'Echeverri', 'Edwards', 'Estrada', 
                  'Evans', 'Fernandez', 'Flores', 'Florez', 'Fonseca', 'Foster', 'Gallego', 'Garcia', 
                  'Gomez', 'Gonzales', 'Gonzalez', 'Gray', 'Green', 'Griffin', 'Guerra', 'Guerrero', 
                  'Gutierrez', 'Hall', 'Harris', 'Hayes', 'Henao', 'Henderson', 'Henriquez', 'Hernandez',
                  'Herrera', 'Hill', 'Howard', 'Hughes', 'Hurtado', 'Jackson', 'James', 'Jenkins', 
                  'Jimenez', 'Johnson', 'Jones', 'Kelly', 'King', 'Lee', 'Lewis', 'Long', 'Lopez', 
                  'Marin', 'Marquez', 'Martin', 'Martinez', 'Medina', 'Mejia', 'Mendoza', 'Miller', 
                  'Mitchell', 'Molina', 'Montes', 'Moore', 'Morales', 'Moreno', 'Morgan', 'Morris', 
                  'Munoz', 'Murillo', 'Murphy', 'Navarro', 'Nelson', 'Ochoa', 'Orozco', 'Ortiz', 
                  'Osorio', 'Palacios', 'Paredes', 'Parker', 'Patterson', 'Perez', 'Perry', 'Peterson', 
                  'Phillips', 'Powell', 'Price', 'Ramirez', 'Ramos', 'Reed', 'Restrepo', 'Reyes', 
                  'Richardson', 'Rios', 'Rivera', 'Roberts', 'Robinson', 'Robledo', 'Rodriguez', 
                  'Rogers', 'Rojas', 'Roldan', 'Romero', 'Ross', 'Rubio', 'Ruiz', 'Russell', 'Salazar', 
                  'Sanchez', 'Sanders', 'Sandoval', 'Santos', 'Scott', 'Serrano', 'Silva', 'Simmons', 
                  'Smith', 'Soto', 'Stewart', 'Suarez', 'Taylor', 'Thomas', 'Thompson', 'Toro', 
                  'Torres', 'Trujillo', 'Turner', 'Uribe', 'Valencia', 'Vallejo', 'Vargas', 'Vasquez', 
                  'Velez', 'Vera', 'Vergara', 'Vidal', 'Villa', 'Walker', 'Ward', 'Washington', 
                  'Watson', 'White', 'Williams', 'Wilson', 'Wood', 'Wright', 'Young', 'Zapata', 
                  'Zimmerman', 'Zuniga']

### Student Constants
if True:
    # undergraduate programs were approximately CAD 6,500 per year for Canadian students
    # Dentistry: CAD 18,000 - CAD 25,000
    # Medicine: CAD 15,000 - CAD 22,000
    # Pharmacy: CAD 10,000 - CAD 17,000
    # Engineering: CAD 9,000 - CAD 15,000 (depending on the specialization and institution)
    # Business & Commerce: CAD 8,000 - CAD 14,000 (higher for specialized or top-ranked 
    # MBA (Master of Business Administration): CAD 20,000 - CAD 40,000
    YEARS_OF_STUDY = {'Base': 2, 'Medium': 3, 'High': 5, 'Very High': 7}
    TUITION_FEES = {'Base': 6000, 'Medium': 10000, 'High': 18000, 'Very High': 25000} ### yearly values
    UGRAD_START_AGE = 18
    MAX_UGRAD_START_AGE = 18 + max(YEARS_OF_STUDY.values())

### Age-Gender Constants
if True:
    AGE_RANGES = {'Baby': [0, 2], 
                'Child': [3, 12], 
                'Teenager': [13, 17], 
                'Young Adult': [18, 25], 
                'Adult': [26, 65], 
                'Elder': [66, 120]}

    AGE_RANGE_PROB_DICT = {'Baby': 0.1,
                            'Child': 0.2,
                            'Teenager': 0.2,
                            'Young Adult': 0.2,
                            'Adult': 0.2,
                            'Elder': 0.1}

    GENDER_PROBS = {'Male': 0.45,
                    'Female': 0.55}                   

    ### create a dataframe with the age ranges and the probabilities of each age range
    age_range = []
    for a_range, value_list in AGE_RANGES.items():
        for age_val in range(value_list[0], value_list[1] + 1):
            if age_val == 0:
                event = "Born"
            elif age_val == 5:
                event = "First Pocket Money"
            else:
                event = "Age Up"
            age_event = a_range + " - " + event
            age_range.append([a_range, age_val, age_event])

    AGE_RANGE_DF = pd.DataFrame(age_range, columns = ['age_range', 'age','age_event'])

### Financial Constants
if True:    
    CAR_FINANCING_OPTION_PROBS = {'Self-Financing': 0.1,
                                'Car Loan': 0.9}

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

    STUDENT_LOAN_INTEREST_RATES = [0.02, 0.07]

    CAR_DOWNPAYMENT_CONSTANT = 3000

    CAR_SELF_FINANCING_CONSTANT= [10000,20000,70000]

### Marriage and Family Constants
if True:
    CAREERS_AND_MARRIAGE_PROBS = {  "No Career": 0.1,
                                    'Pocket Money': 0.001,
                                    'Part Time': 0.002,
                                    'Base': 0.15,
                                    'Medium': 0.25,
                                    'High': 0.3,
                                    'Very High': 0.25}

    MIN_MARRIAGE_ALLOWED_AGE = 18 ###
    SAME_GENDER_MARRIAGE_RATIO = 0.03
    ### https://www.statista.com/statistics/1381955/population-lgb-canada-province/
    SEXUAL_ORIENTATION_RATES ={"Heterosexual": 0.967,"Gay/Lesbian":0.015,"Bisexual": 0.018}
    AVG_MARRIAGE_COST_PER_GUEST = 34000 / 100

    BABY_TWINS_MODE = {1:0.949, 2:0.04, 3:0.01, 4:0.001}

    BIRTH_PROB_CURVES_CST = {"Base Birth Prob": 0.95,
                        "Age Exp Constant -> A1": 0.196888965209072, ### the higher the value the lower the prob because it subtracts from the base prob
                        "Age Sub Constant -> A2": 10, ### the higher the value the lower the prob  ## (age - A2) thus the higher the prob
                        "Age Constant Divider -> C0": 171.989701, ### the higher the value the higher the prob because it divides the input before the exp
                        "Age to Ext. Child. -> C1": 2, ### the higher the value the lower the prob because it multiplies the LN based on the number of children
                        "Non Neg. Ext. Child. Mod. -> C2": 10, ### the higher the value the higher the prob because it adds to the LN based on the number of children
                        "Correction Factor Mult -> C3": 45, ### the higher the value the lower the prob because it subtracts from the LN based on the number of children
                        }
    
    BIRTH_PROB_CURVES_CST["Age Div Constant -> A3"] = BIRTH_PROB_CURVES_CST["Age Exp Constant -> A1"] * BIRTH_PROB_CURVES_CST["Age Constant Divider -> C0"]
    BIRTH_PROB_CURVES_CST["Ext. Child Mult -> B1"] = BIRTH_PROB_CURVES_CST["Age Exp Constant -> A1"] * BIRTH_PROB_CURVES_CST["Age to Ext. Child. -> C1"]
    BIRTH_PROB_CURVES_CST["Ext. Child CT -> B2"] = BIRTH_PROB_CURVES_CST["Age Exp Constant -> A1"] * BIRTH_PROB_CURVES_CST["Non Neg. Ext. Child. Mod. -> C2"]
    BIRTH_PROB_CURVES_CST["Correction Factor -> B3"] = BIRTH_PROB_CURVES_CST["Ext. Child CT -> B2"] / BIRTH_PROB_CURVES_CST["Correction Factor Mult -> C3"]

### Career Constants
if True:
    SPENDER_PROFILE = {'Big Spender': 1.1, 'Average': 0.95, 'Small Spender': 0.85, 'In-Debt': 0.75, 'Depressed': 0.65}
    SPENDER_PROFILE_DECREASE = {'Big Spender': 'Average', 'Average': 'Small Spender', 'Small Spender': 'In-Debt', 
                                'In-Debt': 'Depressed',
                                'Depressed': 'Depressed'}
    
    SPENDER_PROFILE_SWITCH_PROB = 0.5
    ### special profile for those who are in debt

    SPENDER_PROFILE_PROBS = {'Average': 0.5,
                            'Big Spender': 0.3,
                            'Small Spender': 0.2}

    PART_TIME_JOB_MIN_AGE = 16
    PART_TIME_JOB_PROB = 0.5
    POCKET_MONEY_AGE = 5

    FUTURE_CAREER_PAY_PROBS = {'Base': 0.4,
                            'Medium': 0.4,
                            'High': 0.1,
                            'Very High': 0.1}

    INITIAL_INCOME_RANGES = {'Pocket Money': [500,500],
                            'Part Time': [10000, 5000],
                            'Base': [35000, 5000],
                            'Medium': [60000, 10000],
                            'High': [100000, 20000],
                            'Very High': [200000, 40000],
                            'Retired': [75000, 55000]}

    INITIAL_CAREER_PROBS_BY_AGE = { 25: {'Base': 0.5, 'Medium': 0.4, 'High': 0.09, 'Very High': 0.01},
                                    35: {'Base': 0.3, 'Medium': 0.4, 'High': 0.2, 'Very High': 0.1},
                                    55: {'Base': 0.4, 'Medium': 0.3, 'High': 0.2, 'Very High': 0.1},
                                    75: {'Base': 0.5, 'Medium': 0.3, 'High': 0.1, 'Very High': 0.1}}

    RAISE_PROB_CHANGE_BASE = 0.075
    RAISE_PROB_CHANCE_STEPS = 0.025
    RAISE_HIKE_BASE = 0.065
    RAISE_HIKE_BASE_STEP = 0.05 

    RAISE_DICT = {'Pocket Money': {"chance": 0, "hike_range": [0, 0] },
                  "Part Time": {"chance": RAISE_PROB_CHANGE_BASE/3, "hike_range": [RAISE_HIKE_BASE/3, RAISE_HIKE_BASE/3+RAISE_HIKE_BASE_STEP]},
                  "Base": {"chance": RAISE_PROB_CHANGE_BASE, "hike_range": [RAISE_HIKE_BASE, RAISE_HIKE_BASE+RAISE_HIKE_BASE_STEP]},
                  "Medium": {"chance": RAISE_PROB_CHANGE_BASE+RAISE_PROB_CHANCE_STEPS, "hike_range": [RAISE_HIKE_BASE, RAISE_HIKE_BASE+RAISE_HIKE_BASE_STEP*2]},
                  "High": {"chance": RAISE_PROB_CHANGE_BASE+RAISE_PROB_CHANCE_STEPS*2, "hike_range": [RAISE_HIKE_BASE+RAISE_HIKE_BASE_STEP, RAISE_HIKE_BASE+RAISE_HIKE_BASE_STEP*2.2]},
                  "Very High": {"chance": RAISE_PROB_CHANGE_BASE+RAISE_PROB_CHANCE_STEPS*3, "hike_range": [RAISE_HIKE_BASE+RAISE_HIKE_BASE_STEP, RAISE_HIKE_BASE+RAISE_HIKE_BASE_STEP*2.5]}}

### Death Constants
if True:
    ### extracted from https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=1310013501 - Statistics Canada
    SEVERE_ACCIDENT_DEATH_PROB = 0.0001
    INFANT_DEATH_PROB = 0.0045
    INFANT_DEATH_AGE = 1

    ### predict chances of being alive at a certain age (function calculated from the data)
    DEATH_PROB_MODEL_COEF = {'lin_reg': {'age': -0.0007784946236559146,
                                        'gender': 0.006999999999999982,
                                        'constant': 0.0,
                                        'intercept': 1.0103333333333333},
                            'lin_reg_log': {'age': -0.023768641037244638,
                                            'gender': 0.17413385791511007,
                                            'lin_pred': 0.0012374407646648699,
                                            'log_age': 0.11574413613333305,
                                            'intercept': 0.1693725311462318}}

    ### predict chances of being alive at a certain age (function calculated from the data)
    DEATH_PROB_MODEL_COEF_NEW = {'age^1': 0.5350243566594453,
                                'age^2': -0.09833100187477894,
                                'age^3': 0.003413713570147637,
                                'age^4': -4.4700634509943734e-05,
                                'age^5': 1.8773503441702386e-07,
                                'gender^1': 0.008583444963261737,
                                'gender^2': 0.017166889926523522,
                                'gender^3': 0.034333779853047044,
                                'gender^4': 0.06866755970609409,
                                'gender^5': 0.13733511941218818,
                                'intercept': 108.11623127556327}
                                        
    ### extracted from https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=1310039201
    CRIT_ILL_DEATH_PROB_MODEL_COEF = {'age': 8.16935778e-05,
                                    'age_sq': -4.45406073e-06,
                                    'age_cub': 7.38774654e-08,
                                    'age_qd': -3.32211603e-10,
                                    'intercept':  -0.00024762657632679795}

#### TO ADD INFLANTION RATE AND TAXES ON INCOME



# Define the data in a Python dictionary
expenditure_data = {
    "Category": ["Housing", "Transportation", "Food", "Personal Insurance and Pensions", 
                 "Healthcare", "Entertainment", "Other Expenditures", "Cash Contributions", 
                 "Apparel and Services", "Education"],
    "Single Person": [33.3, 16.8, 12.8, 12, 8, 4.7, 4.1, 3.8, 2.7, 1.8],
    "Married Couple (No Kids)": [31, 15, 13, 11, 9, 5, 6, 3, 4, 3],
    "Family of Four": [30, 15, 15, 10, 10, 5, 5, 3, 5, 2],
    "Retired Couple": [27, 14, 13, 9, 15, 4, 6, 5, 3, 2],
    "Low-Income Household": [40, 10, 20, 5, 5, 3, 5, 2, 5, 5]
}

# Create a pandas DataFrame
df_expenditure = pd.DataFrame(expenditure_data)

# import ace_tools as tools; tools.display_dataframe_to_user(name="Monthly Expenditure by Persona", dataframe=df_expenditure)

# # Display the DataFrame
# df_expenditure
