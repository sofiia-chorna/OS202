import numpy as np
from PIL import Image
from time import time
import matplotlib.cm
from mpi4py import MPI
from mandelbrot_set import MandelbrotSet


def calculate_pixel(x, y, scaleX, scaleY, mandelbrot_set):
    calc = complex(-2. + scaleX * x, -1.125 + scaleY * y)
    return mandelbrot_set.convergence(calc, smooth=True)


if __name__ == "__main__":
    mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
    width, height = 1024, 1024
    scaleX = 3. / width
    scaleY = 2.25 / height
    convergence = np.empty((width, height), dtype=np.double)

    # mpi4py params
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Recorder le temps du debut
    start_time = time()

    chunk_size = height // size
    local_convergence = np.zeros((width, chunk_size), dtype=np.double)

    start_row = rank * chunk_size
    end_row = (rank + 1) * chunk_size if rank != size - 1 else height

    for y in range(start_row, end_row):
        for x in range(width):
            local_convergence[x, y - start_row] = calculate_pixel(x, y, scaleX, scaleY, mandelbrot_set)

    # Collecter les resultats partielles
    all_convergence = comm.gather(local_convergence, root=0)

    if rank == 0:
        for i, partial_convergence in enumerate(all_convergence):
            start = i * chunk_size
            end = start + partial_convergence.shape[1]
            convergence[:, start:end] = partial_convergence

        end_time = time()
        execution_time = end_time - start_time

        print(f"Temps du calcul de l'ensemble de Mandelbrot : {execution_time}")

        speedup = mandelbrot_set.calculate_speedup(execution_time)
        print(f"Speedup: {speedup}")

        image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T) * 255))
        image.show()
