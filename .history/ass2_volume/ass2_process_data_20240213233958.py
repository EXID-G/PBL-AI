# process_data.py
import sys
import argparse
import numpy as np
import pickle

def process_data():
    data_path = 'ass2_data.pkl'

    args = sys.argv
    chunk_index = int(args[1])
    # Convert the string back to a list of integers
    with open(volume_data_path, 'rb') as file:
        data = pickle.load(data_path, 'rb')[chunk_index[0]:chunk_index[1]]


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
