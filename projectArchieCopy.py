import pandas as pd
from greedy import compute_metric, greedy_initial_solution
import pulp
from pulp.apis import GUROBI_CMD, GUROBI
import gurobipy as gp
# Load the dataset
import sys



dataset_name = 'Term project data 1b.csv'
dataset_name_no_extension = dataset_name.split('.')[0]
data = pd.read_csv(dataset_name)

# orig_stdout = sys.stdout
# f = open(dataset_name_no_extension+'.txt', 'w')
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



# options = {"WLSACCESSID": "",
#     "WLSSECRET": "",
#     "LICENSEID": }

# Greedy initial solution
data = compute_metric(data)
greedy_solution = greedy_initial_solution(data)
MAX_CONTAINERS = len(greedy_solution)
print("num containers initial ", MAX_CONTAINERS)


# Decision variables
# Binary variable where x_ij = 1 if order i is assigned to container j, 0 otherwise
x = pulp.LpVariable.dicts("x", [(i, j) for i in range(len(data)) for j in range(MAX_CONTAINERS)], cat="Binary") 
# Binary variable where y_j = 1 if contai ner j is used, 0 otherwise
y = pulp.LpVariable.dicts("y", [j for j in range(MAX_CONTAINERS)], cat="Binary")

# Objective: minimize the number of containers used
prob += pulp.lpSum([y[j] for j in range(MAX_CONTAINERS)])
# Constraint to force x[0, 0] to 1
prob += x[0, 0] == 1

# Constraint to force y at index 0 to 262 to 1
# for j in range(262):
#     prob += y[j] == 1

# Constraint to force y[j] to be 1 only if y[j-1] is 1
for j in range(1, MAX_CONTAINERS):
    prob += y[j] <= y[j-1]

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

for j, orders in greedy_solution.items():
    for order in orders:
        order_index = order_numbers.index(order)
        x[order_index, j].setInitialValue(1)
    y[j].setInitialValue(1)

# print("Initial value of y: ", y[0])
# print("Initial value of x: ", x[0, 0])


# Solve the problem

try:
    prob.solve(solver=GUROBI_CMD())
except KeyboardInterrupt:
    print("Optimization interrupted. Checking for feasible solution...")
    with open("interrupted_solution.txt", "w") as f:
        for j in range(MAX_CONTAINERS):
            if y[j].varValue == 1:
                print(f"Container {j+1}:")
                f.write(f"Container {j+1}:\n")
                for i in range(len(data)):
                    if x[i, j].varValue == 1:
                        print(f"  Order {order_numbers[i]} - Weight: {weights[i]}, Volume: {volumes[i]}, Pallets: {pallets[i]}")
                        f.write(f"  Order {order_numbers[i]} - Weight: {weights[i]}, Volume: {volumes[i]}, Pallets: {pallets[i]}\n")

# Output results
print(f"Status: {pulp.LpStatus[prob.status]}")

# Containers used
containers_used = sum([y[j].varValue for j in range(MAX_CONTAINERS)])
print(f"Total Containers Used: {containers_used}")

with open("solution.txt", "w") as f:
    for j in range(MAX_CONTAINERS):
        if y[j].varValue == 1:
            print(f"Container {j+1}:")
            f.write(f"Container {j+1}:\n")
            for i in range(len(data)):
                if x[i, j].varValue == 1:
                    print(f"  Order {order_numbers[i]} - Weight: {weights[i]}, Volume: {volumes[i]}, Pallets: {pallets[i]}")
                    f.write(f"  Order {order_numbers[i]} - Weight: {weights[i]}, Volume: {volumes[i]}, Pallets: {pallets[i]}\n")