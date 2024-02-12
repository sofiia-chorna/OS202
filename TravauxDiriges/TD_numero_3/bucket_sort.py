import sys
import numpy as np
from time import time
import utils
import constants


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 bucket_sort.py <value>")
        return

    bucket_size = int(sys.argv[1])

    start_time = time()

    elements = utils.generate_random(size=constants.N_ELEMENTS, high=constants.MAX_VALUE)
    print(f"Original array : {elements}")

    buckets = utils.split_array(elements, bucket_size)
    print(f"Buckets : {buckets}")

    for index, bucket in enumerate(buckets):
        buckets[index] = utils.insertion_sort(bucket)
        print(f"Index {index}, sorted bucket : {buckets}")

    sorted_buckets = np.concatenate(buckets)
    print(f"Sorted array : {sorted_buckets}")

    end_time = time()
    execution_time = end_time - start_time
    print(f"Execution time : {execution_time}")


if __name__ == "__main__":
    main()
