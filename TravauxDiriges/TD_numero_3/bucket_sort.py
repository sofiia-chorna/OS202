import numpy as np
from time import time
import utils

N_ELEMENTS = 1000
MAX_VALUE = 100
CHUNK_SIZE = 3

start_time = time()

elements = utils.generate_random(size=N_ELEMENTS, high=MAX_VALUE)
print(f"Original array : {elements}")

buckets = utils.split_array(elements, CHUNK_SIZE)
print(f"Buckets : {buckets}")

for index, bucket in enumerate(buckets):
    buckets[index] = utils.insertion_sort(bucket)
    print(f"Index {index}, sorted bucket : {buckets}")

sorted_buckets = np.concatenate(buckets)
print(f"Sorted array : {sorted_buckets}")

end_time = time()
execution_time = end_time - start_time
print(f"Execution time : {execution_time}")
