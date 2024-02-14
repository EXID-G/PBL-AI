# process_data.py
import sys
import argparse
import numpy as np
import pickle
import platform

def process_data():
    args = sys.argv
    data_path = args[1]
    chunk_index1 = int(args[2])
    # print(f"chunk_index1: {chunk_index1}")
    chunk_index2 = int(args[3])

    # allocate the data
    with open(data_path, 'rb') as file:
        data = pickle.load(file)[chunk_index1:chunk_index2]

    # However, here I am not using the hostname instead passing data chunk indexes so that containers can also get what they should process.
    with open(data_path, 'rb') as file:
        hname = platform.node()
        if hname == "ass2-container1":
            data = pickle.load(file)[0:2500]
        if hname == "ass2-container2":
            data = pickle.load(file)[2500:5000]
        if hname == "ass2-container3":
            data = pickle.load(file)[5000:7500]
        if hname == "ass2-container4":
            data = pickle.load(file)[7500:10000]
    
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
