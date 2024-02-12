import numpy as np
from mpi4py import MPI

# Initialiser MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

dim = 120
N_loc = dim // size

# Créer la matrice A localement sur chaque tâche
if rank == 0:
    A = np.array([[(i + j) % dim + 1. for i in range(dim)] for j in range(dim)])
else:
    A = None

# Envoyer les lignes de A aux tâches
A_local = np.empty((N_loc, dim), dtype=float)
comm.Scatter(A, A_local, root=0)
u = np.array([i + 1. for i in range(dim)])
partial_result = A_local.dot(u)

if rank == 0:
    v = np.empty(dim, dtype=float)
else:
    v = None

# Envoyer les résultats partiels à la tâche 0
comm.Gather(partial_result, v, root=0)

if rank == 0:
    print(f"v = {v}")
