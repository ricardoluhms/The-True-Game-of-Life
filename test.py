
#%%### import Person from main.py

from main import Person
#%%
### create a Child using Person class

children = Person(age_range="Child")
print(children.__dict__)

#%%
### create a Teen using Person class

teen = Person(age_range="Teenager",gender="Female")
print(teen.__dict__)
# %%
young_a = Person(age_range= 'Young Adult',first_name= "Mac", last_name="Donalds",gender="Male")

print(young_a.__dict__)
# %%
