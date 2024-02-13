"""
Le jeu de la vie
################
Le jeu de la vie est un automate cellulaire inventé par Conway se basant normalement sur une grille infinie
de cellules en deux dimensions. Ces cellules peuvent prendre deux états :
    - un état vivant
    - un état mort
A l'initialisation, certaines cellules sont vivantes, d'autres mortes.
Le principe du jeu est alors d'itérer de telle sorte qu'à chaque itération, une cellule va devoir interagir avec
les huit cellules voisines (gauche, droite, bas, haut et les quatre en diagonales.) L'interaction se fait selon les
règles suivantes pour calculer l'irération suivante :
    - Une cellule vivante avec moins de deux cellules voisines vivantes meurt ( sous-population )
    - Une cellule vivante avec deux ou trois cellules voisines vivantes reste vivante
    - Une cellule vivante avec plus de trois cellules voisines vivantes meurt ( sur-population )
    - Une cellule morte avec exactement trois cellules voisines vivantes devient vivante ( reproduction )

Pour ce projet, on change légèrement les règles en transformant la grille infinie en un tore contenant un
nombre fini de cellules. Les cellules les plus à gauche ont pour voisines les cellules les plus à droite
et inversement, et de même les cellules les plus en haut ont pour voisines les cellules les plus en bas
et inversement.

On itère ensuite pour étudier la façon dont évolue la population des cellules sur la grille.
"""
import pygame as pg
import numpy as np
from mpi4py import MPI
import time
import sys
import grille
import app

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Tags for communication
TAG_NEXT_CELLS = 11
TAG_TIME = 12

# Resolutions
RES_X = 800
RES_Y = 800

# Dimension et pattern dans un tuple
DICO_PATTERNS = {
    'blinker': ((5, 5), [(2, 1), (2, 2), (2, 3)]),
    'toad': ((6, 6), [(2, 2), (2, 3), (2, 4), (3, 3), (3, 4), (3, 5)]),
    "acorn": ((100, 100), [(51, 52), (52, 54), (53, 51), (53, 52), (53, 55), (53, 56), (53, 57)]),
    "beacon": ((6, 6), [(1, 3), (1, 4), (2, 3), (2, 4), (3, 1), (3, 2), (4, 1), (4, 2)]),
    "boat": ((5, 5), [(1, 1), (1, 2), (2, 1), (2, 3), (3, 2)]),
    "glider": ((100, 90), [(1, 1), (2, 2), (2, 3), (3, 1), (3, 2)]),
    "glider_gun": ((200, 100),
                   [(51, 76), (52, 74), (52, 76), (53, 64), (53, 65), (53, 72), (53, 73), (53, 86), (53, 87),
                    (54, 63), (54, 67), (54, 72), (54, 73), (54, 86), (54, 87), (55, 52), (55, 53), (55, 62),
                    (55, 68), (55, 72), (55, 73), (56, 52), (56, 53), (56, 62), (56, 66), (56, 68), (56, 69),
                    (56, 74), (56, 76), (57, 62), (57, 68), (57, 76), (58, 63), (58, 67), (59, 64), (59, 65)]),
    "space_ship": ((25, 25),
                   [(11, 13), (11, 14), (12, 11), (12, 12), (12, 14), (12, 15), (13, 11), (13, 12), (13, 13),
                    (13, 14), (14, 12), (14, 13)]),
    "die_hard": ((100, 100), [(51, 57), (52, 51), (52, 52), (53, 52), (53, 56), (53, 57), (53, 58)]),
    "pulsar": ((17, 17),
               [(2, 4), (2, 5), (2, 6), (7, 4), (7, 5), (7, 6), (9, 4), (9, 5), (9, 6), (14, 4), (14, 5), (14, 6),
                (2, 10), (2, 11), (2, 12), (7, 10), (7, 11), (7, 12), (9, 10), (9, 11), (9, 12), (14, 10), (14, 11),
                (14, 12), (4, 2), (5, 2), (6, 2), (4, 7), (5, 7), (6, 7), (4, 9), (5, 9), (6, 9), (4, 14), (5, 14),
                (6, 14), (10, 2), (11, 2), (12, 2), (10, 7), (11, 7), (12, 7), (10, 9), (11, 9), (12, 9), (10, 14),
                (11, 14), (12, 14)]),
    "floraison": (
        (40, 40), [(19, 18), (19, 19), (19, 20), (20, 17), (20, 19), (20, 21), (21, 18), (21, 19), (21, 20)]),
    "block_switch_engine": ((400, 400),
                            [(201, 202), (201, 203), (202, 202), (202, 203), (211, 203), (212, 204), (212, 202),
                             (214, 204), (214, 201), (215, 201), (215, 202), (216, 201)]),
    "u": ((200, 200),
          [(101, 101), (102, 102), (103, 102), (103, 101), (104, 103), (105, 103), (105, 102), (105, 101),
           (105, 105), (103, 105), (102, 105), (101, 105), (101, 104)]),
    "flat": ((200, 400),
             [(80, 200), (81, 200), (82, 200), (83, 200), (84, 200), (85, 200), (86, 200), (87, 200), (89, 200),
              (90, 200), (91, 200), (92, 200), (93, 200), (97, 200), (98, 200), (99, 200), (106, 200), (107, 200),
              (108, 200), (109, 200), (110, 200), (111, 200), (112, 200), (114, 200), (115, 200), (116, 200),
              (117, 200), (118, 200)])
}
PATTERN_CHOICE = 'glider'

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
        init_pattern = DICO_PATTERNS[choice]
    except KeyError:
        print("No such pattern. Available ones are:", DICO_PATTERNS.keys())
        exit(1)

    # Init grid in each process
    grid = grille.Grille(*init_pattern)

    # Init app in one process
    if rank == 1:
        appli = app.App((RES_X, RES_Y), grid)

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

            # Display time of calcul
            t1, t2 = comm.recv(source=0, tag=TAG_TIME)
            print(
                f"Temps calcul prochaine generation : {t2 - t1:2.2e} secondes, temps affichage : {t3 - t2:2.2e} secondes\r",
                end=''
            )

            # Stop game
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
