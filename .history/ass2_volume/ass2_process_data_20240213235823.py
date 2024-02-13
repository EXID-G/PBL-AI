# process_data.py
import sys
import argparse
import numpy as np
import pickle

def process_data():
    args = sys.argv
    data_path = args[1]
    chunk_index1 = int(args[2])
    chunk_index2 = int(args[2])
    # Convert the string back to a list of integers
    with open(data_path, 'rb') as file:
        data = pickle.load(file)[chunk_index1,chunk_index2]


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
