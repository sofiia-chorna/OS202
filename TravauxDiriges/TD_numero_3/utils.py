import numpy as np


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


def split_array(elements, bucket_size):
    buckets = np.empty(bucket_size, dtype=object)
    buckets[:] = [[] for _ in range(bucket_size)]
    m = 1 + np.max(elements)
    for i in range(len(elements)):
        index = int(np.floor(bucket_size * elements[i] / m))
        buckets[index].append(elements[i])
    return buckets
