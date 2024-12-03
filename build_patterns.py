# %%
#file to recurseively search for all possible container -> order patterns
#similar to cutting stock problem
import pandas as pd
# Define constants
MAX_WEIGHT = 45000
MAX_VOLUME = 3600
MAX_PALLETS = 60
data = pd.read_csv('test data copy.csv')
data.values.tolist()

# %%
data.head(1)

# %%
all_container_patterns = []
current_orders_in_container = []
current_weight = 0
current_volume = 0
current_pallets = 0
container_index = 0
counter = 0
data_values = data.values.tolist()
data_values.sort(key=lambda x: x[1])
def search_all_patterns(data_values, container_index, current_orders_in_container, current_weight, current_volume, current_pallets):
    added_more = False
    for i in range(container_index, len(data_values)):
        order = data_values[i]
        if current_weight + order[1] > MAX_WEIGHT:
            break
        if current_weight + order[1] <= MAX_WEIGHT and current_volume + order[2] <= MAX_VOLUME and current_pallets + order[3] <= MAX_PALLETS:
            current_orders_in_container.append(order)
            search_all_patterns(data_values, i + 1, current_orders_in_container, current_weight + order[1], current_volume + order[2], current_pallets + order[3])
            current_orders_in_container.pop()
            added_more = True
    if not added_more:
        all_container_patterns.append(current_orders_in_container.copy())
        print("counter ", len(all_container_patterns))



# %%
search_all_patterns(data_values, container_index, current_orders_in_container, current_weight, current_volume, current_pallets)

# %%
all_container_patterns
with open('container_patterns.txt', 'w') as f:
    for pattern in all_container_patterns:
        f.write(f"{pattern}\n")


