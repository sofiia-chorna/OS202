import random
import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def generate_random(size,  min_num=0, max_num=10):
    return [random.randint(min_num, max_num) for i in range(size)]

def insertion_sort(array):
    for i in range(1, len(array)):
        up = array[i]
        j = i - 1
        while j >= 0 and array[j] > up:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = up
    return array


def bubble_sort(elements):
    for i in range(len(elements) - 1):
        if elements[i] < elements[i + 1]:
            temp = elements[i + 1]
            elements[i + 1] = elements[i]
            elements[i] = temp
    return elements


def bucket_sort(elements, k):
    if k < 5:
        return ValueError(f"k is too small, increase the value")

    buckets = [[] for _i in range(k)]
    max = 1 + np.max(elements)
    for i in range(len(elements)):
        buckets[int(np.floor(k * elements[i] / max))].append(elements[i])

    # Individual sort of the buckets
    for index, bucket in enumerate(buckets):
        buckets[index] = bubble_sort(bucket)

    # Concatenate the result
    key = 0
    for i in range(k):
        for j in range(len(buckets[i])):
            elements[key] = buckets[i][j]
            key += 1
    return elements


elements = generate_random(5)
print(f"Original array : {elements}")

elements = bucket_sort(elements, 10)
print(f"Sorted array : {elements}")
