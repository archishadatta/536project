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
dataset_name = 'Term project data final.csv'
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


# Decision variables
# Binary variable where x_ij = 1 if order i is assigned to container j, 0 otherwise
x = pulp.LpVariable.dicts("x", [(i, j) for i in range(len(data)) for j in range(MAX_CONTAINERS)], cat="Binary") 
# Binary variable where y_j = 1 if container j is used, 0 otherwise
y = pulp.LpVariable.dicts("y", [j for j in range(MAX_CONTAINERS)], cat="Binary")

# Objective: minimize the number of containers used
prob += pulp.lpSum([y[j] for j in range(MAX_CONTAINERS)])

# Constraint 1: Each order is assigned to exactly one container
for i in range(len(data)):
    prob += pulp.lpSum([x[i, j] for j in range(MAX_CONTAINERS)]) == 1

# Constraint 2: Weight capacity of each container
for j in range(MAX_CONTAINERS):
    prob += pulp.lpSum([weights[i] * x[i, j] for i in range(len(data))]) <= MAX_WEIGHT * y[j]

# Constraint 3: Volume capacity of each container
for j in range(MAX_CONTAINERS):
    prob += pulp.lpSum([volumes[i] * x[i, j] for i in range(len(data))]) <= MAX_VOLUME * y[j]

# Constraint 4: Pallet capacity of each container
for j in range(MAX_CONTAINERS):
    prob += pulp.lpSum([pallets[i] * x[i, j] for i in range(len(data))]) <= MAX_PALLETS * y[j]


# Symmetry constraints
#prob += x[0, 0] == 1
count = 0
for j, orders in greedy_solution.items():
    for order in orders:
        order_index = order_numbers.index(order)
        x[order_index, j].setInitialValue(1)
        #reduce symmetries
        vol = data["Volume (in3)"].iloc[order_index] 
        if vol > MAX_VOLUME / 2:
            prob += x[order_index, j] == 1
            count += 1
    y[j].setInitialValue(1)

print("Number of hardcoded symmetries",count)   
        
         

# print("Initial value of y: ", y[0])
# print("Initial value of x: ", x[0, 0])


try:
    prob.solve(solver=GUROBI_CMD())
except KeyboardInterrupt:
    print("Optimization interrupted. Checking for feasible solution...")
    with open("interrupted_solution.txt", "w") as f:
        for v in prob.variables():
            if v.varValue == 1:
                f.write(f"{v.name}: {v.varValue}\n")

# Output results
print(f"Status: {pulp.LpStatus[prob.status]}")

# Containers used
containers_used = sum([y[j].varValue for j in range(MAX_CONTAINERS)])
print(f"Total Containers Used: {containers_used}")

with open("solution.txt", "w") as f:
    for v in prob.variables():
            if v.varValue == 1:
                f.write(f"{v.name}: {v.varValue}\n")
