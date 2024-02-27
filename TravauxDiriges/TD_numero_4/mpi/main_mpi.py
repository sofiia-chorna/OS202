from mpi4py import MPI
import time
import sys
import patterns
import numpy as np
import pygame as pg
from grille import Grille
from app import App

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Tags for communication
TAG_NEXT_CELLS = 11
TAG_TIME = 12

# Resolutions
RES_X = 800
RES_Y = 800

# Chosen deco pattern
PATTERN_CHOICE = 'die_hard'

if __name__ == '__main__':
    pg.init()

    # Get user options
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = PATTERN_CHOICE

    if len(sys.argv) > 3:
        RES_X = int(sys.argv[2])
        RES_Y = int(sys.argv[3])

    print(f"Pattern initial choisi : {choice}")
    print(f"Resolution ecran : {RES_X, RES_Y}")

    # Validate the pattern
    try:
        init_pattern = patterns.DICO_PATTERNS[choice]
    except KeyError:
        print("No such pattern. Available ones are:", patterns.DICO_PATTERNS.keys())
        exit(1)

    # Init grid in each process
    sub_dim = (init_pattern[0][0] // size, init_pattern[0][1] // size)
    start_i = sub_dim[0] * rank
    end_i = sub_dim[0] * (rank + 1)
    start_j = sub_dim[1] * rank
    end_j = sub_dim[1] * (rank + 1)

    sub_pattern = (sub_dim, [(coord[0] - start_i, coord[1] - start_j) for coord in init_pattern[1]])
    grid = Grille(sub_dim, sub_pattern)

    # Init app
    appli = App((RES_X, RES_Y), grid)

    while True:
        if rank == 0:
            # Calculate the cells
            t1 = time.time()
            next_cells = grid.compute_next_iteration()
            comm.send(next_cells, dest=1, tag=TAG_NEXT_CELLS)

            # Send time
            t2 = time.time()
            comm.send((t1, t2), dest=1, tag=TAG_TIME)

        # time.sleep(0.5) # A régler ou commenter pour vitesse maxi

        if rank == 1:
            # Receive the cells and draw
            next_cells = comm.recv(source=0, tag=TAG_NEXT_CELLS)
            grid.cells = next_cells
            appli.draw()
            t3 = time.time()
            # print("appli.draw()")

            # Display time of calculation
            t1, t2 = comm.recv(source=0, tag=TAG_TIME)
            print(
                f"Temps calcul prochaine generation : {t2 - t1:2.2e} secondes, temps affichage : {t3 - t2:2.2e} secondes\r",
                end=''
            )

        # Stop game
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
