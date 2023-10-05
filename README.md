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


---
