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
from mpi4py import MPI
import time
import sys
import grille
import app
import patterns

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
