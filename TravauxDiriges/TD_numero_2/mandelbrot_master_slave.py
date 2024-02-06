# Calcul de l'ensemble de Mandelbrot en python avec MPI maître-esclave
import numpy as np
from PIL import Image
from time import time
import matplotlib.cm
from mpi4py import MPI
from mandelbrot_set import MandelbrotSet

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
width, height = 1024, 1024
scaleX = 3. / width
scaleY = 2.25 / height

deb = time()

# Distribution des lignes de l'image à calculer
if rank == 0:
    pixels = [{"x": x, "y": y} for x in range(width) for y in range(height)]
    chunk_size = len(pixels) // size
    pixels_chunks = [pixels[i:i + chunk_size] for i in range(0, len(pixels), chunk_size)]
else:
    pixels_chunks = None

pixels_chunk = comm.scatter(pixels_chunks, root=0)

convergence = np.empty((width, height), dtype=np.double)
for pixel in pixels_chunk:
    x = pixel['x']
    y = pixel['y']
    calc = complex(-2. + scaleX * x, -1.125 + scaleY * y)
    convergence[x, y] = mandelbrot_set.convergence(calc, smooth=True)

# Collecte des résultats partiels
result = comm.gather(convergence, root=0)

if rank == 0:
    fin = time()
    print(f"Temps du calcul de l'ensemble de Mandelbrot : {fin - deb}")
    speedup = mandelbrot_set.calculate_speedup(fin)
    print(f"Speedup: {speedup}")

    # Construction de l'image résultante
    final_convergence = np.zeros((width, height), dtype=np.double)
    for conv in result:
        final_convergence += conv
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(final_convergence.T) * 255))
    image.show()
