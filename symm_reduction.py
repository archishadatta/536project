import pandas as pd
from greedy import compute_metric, greedy_initial_solution
import pulp
from pulp.apis import GUROBI_CMD, GUROBI
import gurobipy as gp
# Load the dataset
import sys


# options = {"WLSACCESSID": "",
#     "WLSSECRET": "",
#     "LICENSEID": ,
#     "LogFile": "gurobi1a.log",}

# Read in data
dataset_name = 'Term project data 1b.csv'
dataset_name_no_extension = dataset_name.split('.')[0]
data = pd.read_csv(dataset_name)

# orig_stdout = sys.stdout
# f = open(dataset_name_no_extension+'.txt', 'a')
# sys.stdout = f

# Define constants
MAX_CONTAINERS = len(data)  # Maximum possible containers in worst case
MAX_WEIGHT = 45000
MAX_VOLUME = 3600
MAX_PALLETS = 60

# Initialize the optimization problem
prob = pulp.LpProblem("Container_Optimization", pulp.LpMinimize)

# Extract data from DataFrame
weights = data['Weight (lbs)'].tolist()
volumes = data['Volume (in3)'].tolist()
pallets = data['Pallets'].tolist()
order_numbers = data['Order Number'].tolist()

# Greedy initial solution
data = compute_metric(data)
greedy_solution = greedy_initial_solution(data)
MAX_CONTAINERS = len(greedy_solution)
print("Number of containers initial (greedy) ", MAX_CONTAINERS)



# Symmetry constraints
#prob += x[0, 0] == 1
count = 0
for j, orders in greedy_solution.items():
    for order in orders:
        order_index = order_numbers.index(order)
        #reduce symmetries
        vol = data["Volume (in3)"].iloc[order_index] 
        if vol > MAX_VOLUME / 2:
            count += 1

print("Number of hardcoded symmetries volume ",count)   

count = 0
for j, orders in greedy_solution.items():
    for order in orders:
        order_index = order_numbers.index(order)
        #reduce symmetries
        vol = data["Weight (lbs)"].iloc[order_index] 
        if vol > MAX_WEIGHT / 2:
            count += 1

print("Number of hardcoded symmetries weight ",count)  

count = 0
for j, orders in greedy_solution.items():
    for order in orders:
        order_index = order_numbers.index(order)
        #reduce symmetries
        vol = data["Pallets"].iloc[order_index] 
        if vol > MAX_PALLETS / 2:
            count += 1

print("Number of hardcoded symmetries pallets ",count)  