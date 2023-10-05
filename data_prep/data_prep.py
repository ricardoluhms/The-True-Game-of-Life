### Create a test code that read data from City module

import sys
sys.path.append('../')
from data_prep import data_prep

# Read data from City module
data = data_prep.read_data()
