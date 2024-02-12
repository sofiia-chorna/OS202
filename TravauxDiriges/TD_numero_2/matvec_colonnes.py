import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

dim = 120
N_loc = dim // size

# Créer la matrice A localement sur chaque tâche
A_local = np.array([[(i + j) % dim + 1. for i in range(rank * N_loc, (rank + 1) * N_loc)] for j in range(dim)])
u = np.array([i + 1. for i in range(dim)])

# Calculer la somme partielle du produit matrice-vecteur pour chaque tâche
partial_result = A_local.dot(u)

if rank == 0:
    v = np.empty(dim, dtype=float)
else:
    v = None

# Envoyer les résultats partiels à la tâche 0
comm.Gather(partial_result, v, root=0)

if rank == 0:
    print(f"v = {v}")
