import numpy as np
import pygame as pg
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


class Grille:
    """
    Grille torique décrivant l'automate cellulaire.
    En entrée lors de la création de la grille :
        - dimensions est un tuple contenant le nombre de cellules dans les deux directions (nombre lignes, nombre colonnes)
        - init_pattern est une liste de cellules initialement vivantes sur cette grille (les autres sont considérées comme mortes)
        - color_life est la couleur dans laquelle on affiche une cellule vivante
        - color_dead est la couleur dans laquelle on affiche une cellule morte
    Si aucun pattern n'est donné, on tire au hasard quels sont les cellules vivantes et les cellules mortes
    Exemple :
       grid = Grille((10,10), init_pattern=[(2,2),(0,2),(4,2),(2,0),(2,4)], color_life=pg.Color("red"), color_dead=pg.Color("black"))
    """

    def __init__(self, dim, sub_pattern, color_life=pg.Color("black"), color_dead=pg.Color("white")):
        self.dimensions = dim
        self.cells = np.zeros(self.dimensions, dtype=np.uint8)
        indices_i = [v[0] - 51 for v in sub_pattern[1]]
        indices_j = [v[1] - 51 for v in sub_pattern[1]]
        self.cells[indices_i, indices_j] = 1
        self.col_life = color_life
        self.col_dead = color_dead

    def compute_next_iteration(self):
        """
        Calcule la prochaine génération de cellules en suivant les règles du jeu de la vie
        """
        ny = self.dimensions[0]
        nx = self.dimensions[1]
        next_cells = np.empty(self.dimensions, dtype=np.uint8)
        diff_cells = []
        for i in range(ny):
            i_above = (i + ny - 1) % ny
            i_below = (i + 1) % ny
            for j in range(nx):
                j_left = (j - 1 + nx) % nx
                j_right = (j + 1) % nx
                voisins_i = [i_above, i_above, i_above, i, i, i_below, i_below, i_below]
                voisins_j = [j_left, j, j_right, j_left, j_right, j_left, j, j_right]
                voisines = np.array(self.cells[voisins_i, voisins_j])
                nb_voisines_vivantes = np.sum(voisines)
                if self.cells[i, j] == 1:  # Si la cellule est vivante
                    if (nb_voisines_vivantes < 2) or (nb_voisines_vivantes > 3):
                        next_cells[i, j] = 0  # Cas de sous ou sur population, la cellule meurt
                        diff_cells.append(i * nx + j)
                    else:
                        next_cells[i, j] = 1  # Sinon elle reste vivante
                elif nb_voisines_vivantes == 3:  # Cas où cellule morte mais entourée exactement de trois vivantes
                    next_cells[i, j] = 1  # Naissance de la cellule
                    diff_cells.append(i * nx + j)
                else:
                    next_cells[i, j] = 0  # Morte, elle reste morte.
        self.cells = next_cells
        return next_cells
