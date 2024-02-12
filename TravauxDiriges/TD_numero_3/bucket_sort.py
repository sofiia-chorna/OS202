from mpi4py import MPI
import numpy as np
from time import time

N_ELEMENTS = 1000
MAX_VALUE = 100

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def generate_random(size, low=0, high=11):
    return np.random.randint(low=low, high=high, size=size)


def insertion_sort(array):
    for i in range(1, len(array)):
        up = array[i]
        j = i - 1
        while j >= 0 and array[j] > up:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = up
    return array


def split(elements, bucket_size):
    buckets = np.empty(bucket_size, dtype=object)
    buckets[:] = [[] for _ in range(bucket_size)]
    m = 1 + np.max(elements)
    for i in range(len(elements)):
        index = int(np.floor(bucket_size * elements[i] / m))
        buckets[index].append(elements[i])
    return buckets


start_time = time()

elements = []
buckets = []

# All processes need to initialize empty lists
if rank == 0:
    elements = generate_random(size=N_ELEMENTS, high=MAX_VALUE)
    print(f"Original array : {elements}")

    buckets = split(elements, size)
    print(f"Buckets : {buckets}")

# Scatter les buckets to different processes
buckets = comm.scatter(buckets, root=0)

# Sort values in each bucket
buckets = insertion_sort(buckets)
print(f"Rank {rank}, sorted bucket : {buckets}")

# Gather buckets together
buckets = comm.gather(buckets, root=0)

if rank == 0:
    sorted_buckets = np.concatenate(buckets)
    print(f"Sorted array : {sorted_buckets}")

    end_time = time()
    execution_time = end_time - start_time
    print(f"Execution time : {execution_time}")
