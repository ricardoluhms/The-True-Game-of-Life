

#%%
import pandas as pd
from gml_constants import MAX_DEBT_RATIO, INTEREST_RATE_PER_TYPE,LOAN_TERM_PER_TYPE

class Financial_Institution:
    def __init__(self, bank_name=None):
        self.bank_name = bank_name
        self.loan_df = pd.DataFrame(columns=[
            'loan_id', 'person_id', 'person_income', 'loan_amount', 'loan_term',
            'interest_rate', 'loan_type', 'loan_reason', 'loan_refinanced',
            'loan_balance', 'loan_status', 'loan_term_payment',
            'interest_paid_yearly',
        ])
        self.loan_day_to_day_df = pd.DataFrame(columns=[
            'loan_id', 'loan_balance', 'loan_total_term', 'loan_current_term',
            'loan_term_payment', 'loan_status'
        ])
        self.insurance_df = pd.DataFrame(columns=[
            'insurance_type', 'insurance_amount', 'insurance_term',
            'insurance_status', 'insurance_balance', 'insurance_payment'
        ])

    def retrieve_existing_loan_data(self, family_loans_df, ids):
        if len(ids) > 1:
            ### retrieve their loan data
            f_loans_df = family_loans_df[family_loans_df['person_id'].isin(ids)]

        elif len(ids) == 1 and type(ids) == list:
            f_loans_df = family_loans_df[family_loans_df['person_id'] == ids[0]]
        elif len(ids) == 1 and type(ids) != list:
            f_loans_df = family_loans_df[family_loans_df['person_id'] == ids]
        else:
            existing_loan_yearly_payment = 0

        f_loans_df['interest_paid_yearly'], f_loans_df['principal_paid_yearly'] = \
            zip(*f_loans_df.apply(lambda x: self.yearly_loan_amount_paid( principal = x['loan_amount'], 
                                                                          annual_interest_rate = x['interest_rate'], 
                                                                          loan_term_years = x['loan_term']- x['loan_term_payment']), axis=1))
        
        f_loans_df['existing_yearly_payment'] = f_loans_df['interest_paid_yearly'] + f_loans_df['principal_paid_yearly']
        existing_loan_yearly_payment = f_loans_df['existing_yearly_payment'].sum()
        return existing_loan_yearly_payment

    @staticmethod
    def retrieve_finanacial_background(city,person_id):
        
        income_and_bal_df, family_loans = city.retrieve_loan_customer_data(person_id)
        person_income = income_and_bal_df[income_and_bal_df['unique_name_id'] == person_id]["income"].values[0]
        family_income = income_and_bal_df["income"].sum()
        person_balance = income_and_bal_df[income_and_bal_df['unique_name_id'] == person_id]["balance"].values[0]
        family_balance = income_and_bal_df["balance"].sum()
        personal_loan = family_loans[family_loans['person_id'] == person_id]

        return person_income, family_income, person_balance, family_balance, personal_loan, family_loans

    @staticmethod
    def retrieve_max_debt_to_income_ratio(city, person_id):
        person_age = city.people_obj_dict[person_id].age
        person_spender_profile = city.people_obj_dict[person_id].spender_profile
        for _, bucket_details in MAX_DEBT_RATIO.items():
            if person_age >= bucket_details["Age Range"][0] and person_age <= bucket_details["Age Range"][1]:
                return bucket_details["Max Debt Ratio"][person_spender_profile]

    @staticmethod
    def debt_to_income_ratio(person_income, person_balance, yearly_loan_payment, use_balance_downp_ratio = 0.2):
        ### calculate the debt to income ratio
        debt_to_income_ratio_with_balance = (yearly_loan_payment - person_balance * use_balance_downp_ratio) / (person_income )

        return debt_to_income_ratio_with_balance
    
    @staticmethod
    def debt_to_income_ratio_family(family_income, family_balance, yearly_loan_payment, use_balance_downp_ratio = 0.2):
        ### calculate the debt to income ratio
        debt_to_income_ratio_with_fam_balance = (yearly_loan_payment - family_balance * use_balance_downp_ratio) / (family_income )

        return debt_to_income_ratio_with_fam_balance
    
    @staticmethod
    def balance_status(balance):
        if balance < 0:
            balance = 0
            balance_status = False
        else:
            balance_status = True
        return balance, balance_status

    @staticmethod
    def debt_to_income_ratio_check(debt_to_income_ratio, debt_to_income_ratio_threshold):
        ### calculate the specific debt to income ratio for the family
        sdepth_2_income_status = debt_to_income_ratio < debt_to_income_ratio_threshold

        return sdepth_2_income_status

    def loan_request(self, city, person_id, loan_type, new_loan_amount, loan_term, interest_rate, financial_background):

        _, interest_paid_yearly, principal_paid_yearly = self.yearly_loan_amount_paid(principal=new_loan_amount,
                                                                                                            annual_interest_rate=interest_rate,
                                                                                                            loan_term_years=loan_term)
        new_loan_yearly_payment = interest_paid_yearly + principal_paid_yearly

        person_income, family_income, person_balance, family_balance, personal_loan, family_loans = financial_background
        yearly_loan_payment = self.retrieve_existing_loan_data(personal_loan, person_id)

        yearly_family_loan_payment = self.retrieve_existing_loan_data(family_loans, family_loans['person_id'].unique())
        max_debt_to_income_ratio = self.retrieve_max_debt_to_income_ratio(city, person_id)
        if loan_type == 'Personal':
            max_debt_to_income_ratio -= 0.1
            if max_debt_to_income_ratio < 0:
                max_debt_to_income_ratio = 0.1

        person_balance, person_balance_status = self.balance_status(person_balance)
        family_balance, family_balance_status = self.balance_status(family_balance)

        debt_to_income_ratio= self.debt_to_income_ratio(person_income, person_balance, yearly_loan_payment+new_loan_yearly_payment)
        depth_2_income_status = self.debt_to_income_ratio_check(debt_to_income_ratio, max_debt_to_income_ratio)

        debt_to_income_ratio_family = self.debt_to_income_ratio_family(family_income, family_balance, yearly_family_loan_payment+new_loan_yearly_payment)
        depth_2_income_status_family = self.debt_to_income_ratio_check(debt_to_income_ratio_family, max_debt_to_income_ratio)

        ### create list of lists that will consider person_balance_status, family_balance_status, depth_2_income_status, depth_2_income_status_family, loan_type, loan_approved, personal_criteria, family_criteria, loan_decision_description
        ### Personal loan will not consider family_balance_status and depth_2_income_status_family
        ### Student loan will not consider person_balance_status, family_balance_status, depth_2_income_status, depth_2_income_status_family because it does not require income or balance so it not required in the criteria list
        ### Mortgage loan will consider all the criteria
        ### Car loan will consider all the criteria
        # person_balance_status, family_balance_status, depth_2_income_status, depth_2_income_status_family, loan_type, loan_approved, personal_criteria, family_criteria, loan_decision_description
        LOAN_CRITERIA = [[True, True, True, True, 'Mortgage', True, True, True, "Loan approved - Person & Family Criteria met"],
                         [True, True, False, False, 'Mortgage', True, True, True, "Loan approved - Person Criteria met"],
                         [True, True, False, False, 'Mortgage', True, False, True, "Loan approved - Family Criteria met"],
                         [False, False, True, False, 'Mortgage', True, True, False, "Loan approved - Person Debt to Income Ratio met"],
                         [False, False, False, True, 'Mortgage', True, False, False, "Loan approved - Family Debt to Income Ratio met"],
                         [True, True, False, False, 'Car', True, True, True, "Loan approved - Person Criteria met"],
                         [True, True, False, False, 'Car', True, False, True, "Loan approved - Family Criteria met"],
                         [False, False, True, False, 'Car', True, True, False, "Loan approved - Person Debt to Income Ratio met"],
                         [False, False, False, True, 'Car', True, False, False, "Loan approved - Family Debt to Income Ratio met"],
                         [True, True, False, False, 'Personal', True, True, True, "Loan approved - Person Criteria met"],
                         [False, False, True, False, 'Personal', True, True, False, "Loan approved - Person Debt to Income Ratio met"]]

        load_criteria_df = pd.DataFrame(LOAN_CRITERIA, columns=['person_balance_status', 'family_balance_status', 'depth_2_income_status', 'depth_2_income_status_family', 
                                                                'loan_type', 'loan_approved', 'personal_criteria', 'family_criteria', 'loan_decision_description'])
        
        ### check if criteria is in loan criteria dataframe
        criteria_b_person = load_criteria_df["person_balance_status"] == person_balance_status
        criteria_b_family = load_criteria_df["family_balance_status"] == family_balance_status
        criteria_d2i_person = load_criteria_df["depth_2_income_status"] == depth_2_income_status
        criteria_d2i_family = load_criteria_df["depth_2_income_status_family"] == depth_2_income_status_family
        all_criteria = criteria_b_person & criteria_b_family & criteria_d2i_person & criteria_d2i_family


        if load_criteria_df[all_criteria].sum()== 0 and loan_type != 'Student':
            loan_approved = False
            personal_criteria = False
            family_criteria = False
            loan_description = f"{loan_type} Loan not approved - No criteria met"

        elif loan_type == 'Student':
            ### special case for student loan - check if the person has an active student loan , if so the loan will not be refinanced but will have the same terms
            is_student_loan = family_loans['loan_type'] == 'Student'
            is_student_loan_active = family_loans['loan_status'] == 'active'
            is_person_student_loan = family_loans['person_id'] == person_id
            student_loan_criteria = is_student_loan & is_student_loan_active & is_person_student_loan
            student_loan_df = family_loans[student_loan_criteria]
            if len(student_loan_df) > 0:
                interest_rate = student_loan_df['interest_rate'].values[0]
                loan_term = student_loan_df['loan_term'].values[0]
                _, interest_paid_yearly, principal_paid_yearly = self.yearly_loan_amount_paid(principal=new_loan_amount,
                                                                                                    annual_interest_rate=interest_rate,
                                                                                                    loan_term_years=loan_term)
                new_loan_yearly_payment = interest_paid_yearly + principal_paid_yearly

            loan_approved = True
            personal_criteria = None
            family_criteria = None
            loan_description = "Loan approved - Student loan does not require income or balance"
        
        else:
            loan_approved = load_criteria_df[all_criteria]['loan_approved'].values[0]
            personal_criteria = load_criteria_df[all_criteria]['personal_criteria'].values[0]
            family_criteria = load_criteria_df[all_criteria]['family_criteria'].values[0]
            loan_description = loan_type +" "+ load_criteria_df[all_criteria]['loan_decision_description'].values[0]

        loan_status_pack = [loan_approved, personal_criteria, family_criteria, loan_description]
        loan_details_pack = [new_loan_yearly_payment, interest_rate, loan_term]
        loan_balance = [person_balance, family_balance]

        return loan_status_pack, loan_details_pack, loan_balance

    def quick_eligibility(self, city, person_id, new_loan_amount, loan_term, interest_rate,financial_background):
        ### check if the person is eligible for the loan
        person_income, _, person_balance, _, _, _= financial_background
        _, interest_paid_yearly, principal_paid_yearly = self.yearly_loan_amount_paid(principal=new_loan_amount,
                                                                                                    annual_interest_rate=interest_rate,
                                                                                                    loan_term_years=loan_term)
        new_loan_yearly_payment = interest_paid_yearly + principal_paid_yearly
        
        debt_to_income_ratio = self.debt_to_income_ratio(person_income, person_balance, new_loan_yearly_payment)
        debt_to_income_ratio_threshold = self.retrieve_max_debt_to_income_ratio(city, person_id)

        return new_loan_yearly_payment, debt_to_income_ratio, debt_to_income_ratio_threshold
    
    @staticmethod
    def add_loan_record(loan_df, loan_id, person_id, person_income, loan_amount, loan_term, interest_rate, loan_type, loan_reason):
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
            'loan_term_payment': 0  # Initial payment is 0
        }
        return loan_df.append(loan_data, ignore_index=True)
        
    @staticmethod
    def add_payment(loan_df, loan_day_to_day_df, loan_id, payment_amount):
        loan_idx = loan_df[loan_df['loan_id'] == loan_id].index[0]
        loan_df.at[loan_idx, 'loan_balance'] -= payment_amount
        loan_df.at[loan_idx, 'loan_term_payment'] += payment_amount

        day_to_day_data = {
            'loan_id': loan_id,
            'loan_balance': loan_df.at[loan_idx, 'loan_balance'],
            # ... (other necessary fields)
        }
        return loan_df, loan_day_to_day_df.append(day_to_day_data, ignore_index=True)
    
    @staticmethod
    def yearly_loan_amount_paid(principal, annual_interest_rate =  9.39, loan_term_years = 10):
        # Given loan details
        # Principal amount in dollars
        # Loan term in years
        # Annual interest rate converted to decimal number

        annual_interest_rate = annual_interest_rate/ 100  
        monthly_interest_rate = annual_interest_rate / 12  # Monthly interest rate
        loan_term_years = 3  
        total_payments = loan_term_years * 12  # Total number of payments

        # Calculating monthly payment using the formula
        monthly_payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate)**total_payments) / ((1 + monthly_interest_rate)**total_payments - 1)

        # Initializing variables for the calculation
        loan_balance = principal  # Starting balance is the principal amount

        for _ in range(1, loan_term_years + 1):
            interest_paid_yearly = 0
            principal_paid_yearly = 0

            for _ in range(1, 13):  # Calculating for each month in the year
                interest_for_month = loan_balance * monthly_interest_rate  # Interest for the month
                principal_for_month = monthly_payment - interest_for_month  # Principal repayment for the month

                loan_balance -= principal_for_month  # Reducing the balance by the principal paid
                interest_paid_yearly += interest_for_month  # Total interest paid in the year
                principal_paid_yearly += principal_for_month  # Total principal paid in the year


        return loan_balance, interest_paid_yearly, principal_paid_yearly

    @staticmethod
    def refinance_loan(loan_df, loan_id, new_loan_id, new_loan_term, new_loan_payment): ### to be reviewed
        # Close old loan
        loan_idx = loan_df[loan_df['loan_id'] == loan_id].index[0]
        loan_df.at[loan_idx, 'loan_status'] = 'refinanced'
        loan_df.at[loan_idx, 'loan_balance'] = 0

        # Create new loan
        new_loan_data = loan_df.loc[loan_idx].to_dict()
        new_loan_data['loan_id'] = new_loan_id
        new_loan_data['loan_term'] = new_loan_term
        new_loan_data['loan_term_payment'] = new_loan_payment
        return loan_df.append(new_loan_data, ignore_index=True)
    
    @staticmethod
    def approval_pipeline():
        pass

    @staticmethod
    def downpayment_pipeline():
        pass

    @staticmethod
    def decline_pipeline():
        pass 

    def loan_pipeline(self, city, person_id, loan_type, new_loan_amount):
        ### get rates
        interest_rate = INTEREST_RATE_PER_TYPE[loan_type]
        loan_term_ranges = LOAN_TERM_PER_TYPE[loan_type]

        person_income, family_income, person_balance, family_balance, personal_loan, family_loans = self.retrieve_finanacial_background(city,person_id)
        financial_background = [person_income, family_income, person_balance, family_balance, personal_loan, family_loans]
        
        ### use the highest loan term for the loan type to check if the person is eligible for the loan if debt to income is met keep that value
        new_loan_yearly_payment, debt_to_income_ratio, debt_to_income_ratio_threshold = self.quick_eligibility(city, person_id, new_loan_amount, loan_term_ranges[1], 
                                                                                                                   interest_rate,financial_background)
        if debt_to_income_ratio< debt_to_income_ratio_threshold:
            loan_term = loan_term_ranges[1]
        

        ### check personal loan debt to income ratio
        loan_status_pack, loan_details_pack, loan_balance = self.loan_request(city, person_id, loan_type, new_loan_amount, loan_term, interest_rate, financial_background)
        loan_approved, personal_criteria, family_criteria, loan_description = loan_status_pack
        new_loan_yearly_payment, interest_rate, loan_term = loan_details_pack
        person_balance_status, family_balance_status = loan_balance


        ### if loan approved check if the personal criteria and loan person balance is met
        ### if true deduct the 0.2 downpayment from the person balance
        ### if loan approved check and if the family criteria and loan family balance is met
        ### if true deduct the 0.2 downpayment from the family balance
  

    def print_load_df(self):
        return self.loan_df
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