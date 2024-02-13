# process_data.py

import numpy as np

def process_data():
    # Read data from the shared volume
    data_path = 'ass2_data'
    with open(data_path, 'r') as file:
        data_str = file.read()

    # Convert the string back to a list of integers
    data = list(map(int, data_str.split(',')))

    # Calculate mean
    mean = np.mean(data)
    print(f"Mean: {mean}")

    # Calculate variance
    variance = np.var(data)
    print(f"Variance: {variance}")

    # Calculate max and min
    max_value = np.max(data)
    min_value = np.min(data)
    print(f"Max: {max_value}")
    print(f"Min: {min_value}")

if __name__ == "__main__":
    process_data()
