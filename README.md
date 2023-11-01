Based on the provided repository and the initial idea for the project, here's a detailed README:

---

# The True Game of Life

## Introduction

The True Game of Life aims to simulate the life of individuals in a city, capturing their financial and life events. This synthetic dataset will serve as a foundation for various marketing models, especially in the domain of Digital Marketing. The primary goal is to understand and strategize Data-Driven Marketing techniques that bridge the gap between businesses and customers.

## What is it about?

### Digital Marketing - Data Driven Strategies as Bridge to Customers

#### Types of Marketing by Product:
- **B2B2C**: Marketing to another company that will sell your product, targeting them instead of the end customer.
- **B2C**: Marketing and Sales Strategy is directly oriented to the end customer.
- **Individual or Mass Marketing**: Deciding if a campaign should target a broad audience or be very specific.

#### B2B2C Challenges:
- Identifying wholesalers/sellers that sells to your customers.
- Measuring the success of wholesalers and marketing strategies.
- Understanding the effectiveness of marketing leads.
- Differentiating between Sales Conversion and Marketing Conversion.
- Exploring various Delivery Modes like Social Media, Mass Media, Ads, Email Campaigns, and Influencers.
- How do measure the success of the wholesalers and marketing strategies, when they are not the end customers?
- Marketing “Lead” – Hot or Cold – When delivering insights about customer/sellers behavior, which actionable insights (lead) are more effective (hot) than others? How do you measure conversion rate?
- Sales Conversion vs Marketing Conversion – Sometimes the success of a campaign is just to raise awareness (clicks and views) but that does not means that it will convert into sales

#### Purposes:
- Acquire new customers.
- Increase Sales/ Profitability.
- Achieve better Customer Segmentation and Content Delivery.

## Scope of the Repository:

- Create Synthetic datasets that store life and financial events to be used as ground truth for marketing models.
- Simulate the life of a person using a Python class.
- Store attributes like age, gender, income, bank balance, fixed bills, etc.
- Simulate life events like aging, marriage, and death.
- Manage population aging and life events through the City Module in `main.py`.
- Historic data and their live events should be stored as a data frame

## Repository Structure:

- **gml_constants.py**: Contains constants used throughout the project.
- **main.py**: Contains the City Module which manages population aging, life/death events, insurance records, and relationships between citizens.
    - City Module will manage the population aging.
    - Since there are events that generates a new person (new born) the city show add those members and also age all of the members at the same time
    - Life/Death events also affects insurance so they should be recorded
    - Lastly, marriage will also affect the relationship between citizens so their financial relations and other life events will be affected.
    - City will manage that relationship.

- **test.py**: Contains tests for the project modules.

## Future Use of the Synthetic Dataset:

### First Stage:
- Use a synthetic dataset to simulate persons in a city as they age, and their spend behavior and their major life events such as going to university, marrying, having kids, buying house, getting promotions, buying life insurance, and random events that would cause death or revenue loss. 
- Each year would cause each person to have updates in their lives or not based on probabilities.
- Because those events, they might be more inclined to buy insurance or getting a loan.
- Whenever a person reaches one of those events a chance of them buying insurance increases or decreases
- Create a unique measure of risk to evaluate if they are going to buy or not insurance.
- Another mechanism will be created to send emails to them randomly, and we would assume that a normal campaign would have X% of open ratio, and Y% out of the X that opened would engage with the website
- Z% would be the ones that opened, engaged and bought insurance or got a loan
- There would be persons that would buy insurance regardless of the campaign.

### Second Stage:
- Use synthetic data to create customer segmentation models targeted by campaigns.

## Additional Details:

- Generate datasets with fake customers, Canadian postal codes, ages, genders, marital status, unique IDs, and birth dates.
- Create datasets for insurance and bank products.
- Generate customer datasets with their financial products.
- We will store their age, gender, income, bank balance, fixed bills…
- We player will live to 65-85 years and then, each year there will be a chance of dying.
- Each year that goes by after 65 year the chances increases.
- Historic data and their live events should be stored as a data frame
- It will start with 100 players. 50 Men and 50 Woman. (can be less for testing code purposes first)
- Each person  starts with 0 balance in their account.
- They will be randomly assigned to career paths
- Study level will also be set randomly

## Future Modules
- Generate a second dataset with insurance and bank products, insurance term 10 years, insurance term 20 years, and insurance whole life, house mortgage and personal loans. Insurance values for term are 1000 for 10 year term, 2000 for 2000 term and 3000 per year. Loans could be a 1 year, 5 years or 10 years, mortgage are only provided to people with ages 24 and above and last 20 or 25 years.
-Generate a third dataset for each customer in the first dataset. Each customer has a 30% of chance of having one insurance product, but they cannot have more than one insurance product. Each customer that do not have a insurance has 25% of having a loan, 40% of having a mortgage. 5% of the customers can have insurance and mortgage and 10% of the customer can have insurance and loan, 5% percent can have loans and mortgages but no insurance. 
 -Loan cannot exceed 10% of their annual income. Insurance cannot exceed 2% of their annual income,
Mortgage yearly value cannot exceed 20% of their income.


# Future Features on existing modules - TO DO LIST
# 1. Person_Life
## 1.1 Get a Car
 - Include get a car function and check which car they will get and if they can afford using personal balance or loan
 - check if is a single person or a couple
 - check if both their loan status (how many they have, to refinance them or append a new one without the sum of all active loans surpass both their incomes)
## 1.2 Get a House
 - Include get a house function and check which house they will get and if they can afford using personal balance or loan
 - check if is a single person or a couple
 - check how many kids they have (house size and price)
 - check how much from their income was being used for rent (if they were renting) (set all the new people as renter for start)
## 1.3 Get a Raise or Promotion
 - Include get a raise or promotion function and check if they will get a raise or promotion and how much
## 1.4 Change Spending Habits
 - Include change spending habits function and check if they will change their spending habits and how much
## 1.5 Add a new kid
 - Include add a new kid function and check if they will have a new kid and how much it will cost
## 1.6 Critical Illness or Disability event
 - Include critical illness or disability event and check if they will have a critical illness or disability event and how much it will cost
## 1.7. Add Marriage Costs
 - Include add marriage costs function and check if they will get married and how much it will cost
## 1.8. Create the Adult Life functions
 - Create one function that will simulate one year of adult life
 - Create one function that will simulate the adult life until the age of X
## 1.9 Create the Elder Life functions
 - Create one function that will simulate one year of elder life
 - Create one function that will simulate the elder life until the age of X
## 1.10 Create the Dead function
 - Create one function that will simulate the probability of death
## 1.11 Review the Spender Profile to check main expenses such as housing, loan, kids, ...
## 1.12 Check how money will be transferred to kids/ next generation in life and death events (from pocket money to house and car inheritance)
## 1.13 Defien when and how a Children or Young Adult will not be dependent anymore and their finances will be separated from their parents

# 2. Financial Institution
## 2.1. Test get loan functions
## 2.2. Create the refinance loan function
## 2.3. Create the function to combine existing loans
## 2.4. Create the function to check loans from couples and opportunities to combine them
## 2.4. Create the function to pay loan
## 2.5. Create the function to handle when a loan is not paid
## 2.6. Create the function to handle when a loan is paid
## 2.7. Create the get insurance function
## 2.8. Create the function to handle when a insurance is not paid
## 2.9. Create the function to handle when a insurance is paid
## 2.10. Create the function to handle death befenit from insurance
## 2.11. Create Default scenarios for loans and insurance - How and when we will default a loan or insurance
## 2.12. Create the function to measure sales and profit from loans and insurance

# 3. City
# 4. Marketing
## 4.1. Create the function to handle when a campaign is sent
## 4.2. Create the function to handle when a campaign is opened
## 4.3. Create the function to handle when a campaign is engaged
## 4.4. Create the function to handle when a campaign is converted
## 4.5. Create the function to handle when a campaign is not converted
## 4.6. Create the function to measure sales and profit from campaigns

# 5. Data Science
## 5.1. Evaluate marketing campaigns and their effectiveness
## 5.2. Evaluate marketing campaigns and their effectiveness by customer segment
## 5.3. Evaluate marketing campaigns and their effectiveness by customer segment and the respective lift

## create a new folder for the project to split life classes from city, financial institution and marketing
## create a new folder for test related files
## create csv files with test data for the tests


