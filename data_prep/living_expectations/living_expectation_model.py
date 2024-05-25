#%%
import pandas as pd
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


### load data considering that the data is in the same folder as the script
### file name living_expectations_canada_by_gender_age.csv
# 1. load the data

data = pd.read_csv('C:/Users/ricar/Documents/GitHub/TGoL/data_prep/living_expectations/living_expectations_canada_by_gender_age.csv')

### row_select must be 1

#%%
# 2. select rows Age.1 Gender VALUE
data_select = data[data['row_select'] == 1]
data_select = data_select[['Age.1', 'Gender', 'VALUE']]
data_select = data_select.rename(columns = {'Age.1': 'age',
                                            'Gender':'gender',
                                            'VALUE':'value'})

# Crie um modelo para prever o valor de expectativa de vida
# este modelo sera uma combinanção de idade e genero
# e tera um componente linear e um componente com regressao logistica

### import libraries
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

#%%
# 3. create a linear model
# 3.1. create a linear model for the whole dataset

lin_model = LinearRegression()
cols = ['age','gender']
X = data_select[cols]
y = data_select['value']

lin_model.fit(X, y)

### return the coefficients and the intercept
print(lin_model.coef_, lin_model.intercept_)
#%%
# 3.2. create a polynomial model for the whole dataset
### give labels to the columns knowing that:
### - first column is the intercept
### - second column is the x^1 term for age
### - third column is the x^1 term for gender
### - fourth column is the x^2 term for age
### - fifth column is the x^2 term for gender
### - sixth column is the x^3 term for age
### - seventh column is the x^3 term
### - eighth column is the x^4 term for age
### - ninth column is the x^4 term for gender
### - tenth column is the x^5 term for age
### - eleventh column is the x^5 term for gender
# replace gender value equals 1 by value equals 2
data_select2 = data_select.copy()
mask = data_select2['gender'] == 1
data_select2.loc[mask, 'gender'] = 2

order = 5
for col  in cols:
    for i in range(1,order+1):
        data_select2[col + "^" + str(i)] = data_select2[col]**i

#%%
poly_model = LinearRegression()
### select the columns to be used in the polynomial model
cols_poly = [col + "^" + str(i) for col in cols for i in range(1,order+1)]
X_poly = data_select2[cols_poly]

poly_model.fit(X_poly, y)

### get the coefficients and the intercept
print(poly_model.coef_, poly_model.intercept_)

### print the mean absolute error for the linear model and polynomial model

#%%
### extend the data to include ages from 0 to 120
data_extended = pd.DataFrame()
data_extended['age'] = range(0,121)
data_extendedM = data_extended.copy()
data_extendedF = data_extended.copy()
data_extendedM['gender'] = 0
data_extendedF['gender'] = 2

data_extended = pd.concat([data_extendedM, data_extendedF])

order = 5
for col  in cols:
    for i in range(1,order+1):
        data_extended[col + "^" + str(i)] = data_extended[col]**i
     
#%%
X2 = data_extended[cols]
X_poly2 = data_extended[cols_poly]

### merge the data with data_select
data_extended = data_extended.merge(data_select, on = cols, how = 'left')
data_extended["lin_pred"] = lin_model.predict(X2)
data_extended["poly_pred"] = poly_model.predict(X_poly2)
### compare the predictions error with the original data when available
data_extended["lin_error"] = data_extended["lin_pred"] - data_extended["value"]
data_extended["poly_error"] = data_extended["poly_pred"] - data_extended["value"]

drop = data_extended["value"].isna()
data_extended[~drop]
#%%
### print the mean absolute error for the linear model and polynomial model
print(data_extended["lin_error"].abs().mean())
print(data_extended["poly_error"].abs().mean())
#%%
local_folder = 'C:/Users/ricar/Documents/GitHub/TGoL/'
# 4. save the data
data.to_csv(local_folder+'data_prep/living_expectations/living_expectations_results.csv')
#%%
### get the coefficients for the polynomial model
coefficients = poly_model.coef_
intercept = poly_model.intercept_

### transform the coefficients and intercept into a dataframe
### add name to the columns
coefficients_df = pd.DataFrame([list(coefficients)],columns = cols_poly)
coefficients_df["intercept"] = intercept

### find the age where the polynomial error is higher than the linear error
data_extended["poly_error"] = data_extended["poly_error"].abs()
data_extended["lin_error"] = data_extended["lin_error"].abs()
mask = data_extended["poly_error"] > data_extended["lin_error"]

data_extended[mask]['age']




#%%
X_poly_df = pd.DataFrame(X_poly)
#%%
### plot lin_pred and poly_pred
import matplotlib.pyplot as plt
plt.scatter(data_extended["age^1"], data_extended["lin_pred"] , color = 'red')
plt.scatter(data_extended["age^1"], data_extended["poly_pred"], color = 'blue')
plt.scatter(data_extended["age^1"], data_extended["value"], color = 'yellow')

### the model 



# %%
