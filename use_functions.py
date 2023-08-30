from main import Person, Marriage
import pandas as pd

### use the person class to generate a person

p = Person('Male')
p.run_life()
print(pd.DataFrame(p.history))

m = Marriage(Person('Male'), Person('Female'))
m.marry()
print(m.married)
m.divorce()
print(m.married)
m.have_child()
print(m.children)

