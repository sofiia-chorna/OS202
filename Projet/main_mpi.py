"""
Module managing an ant colony in a labyrinth.
"""
import numpy as np
from mpi4py import MPI
import maze
import pheromone
import pygame as pg
import colony

comm = MPI.COMM_WORLD.Dup()
nbp = comm.size
rank = comm.rank

UNLOADED, LOADED = False, True

exploration_coefs = 0.

if __name__ == "__main__":
    import sys
    import time

    pg.init()
    size_laby = 25, 25
    if len(sys.argv) > 2:
        size_laby = int(sys.argv[1]), int(sys.argv[2])

    resolution = size_laby[1] * 8, size_laby[0] * 8
    screen = pg.display.set_mode(resolution)
    nb_ants = size_laby[0] * size_laby[1] // 4
    max_life = 500
    if len(sys.argv) > 3:
        max_life = int(sys.argv[3])
    pos_food = size_laby[0] - 1, size_laby[1] - 1
    pos_nest = 0, 0
    a_maze = maze.Maze(size_laby, 12345)
    ants = colony.Colony(nb_ants, pos_nest, max_life)
    unloaded_ants = np.array(range(nb_ants))
    alpha = 0.9
    beta = 0.99
    if len(sys.argv) > 4:
        alpha = float(sys.argv[4])
    if len(sys.argv) > 5:
        beta = float(sys.argv[5])
    pherom = pheromone.Pheromon(size_laby, pos_food, alpha, beta)
    mazeImg = a_maze.display()
    food_counter = 0

    snapshop_taken = False
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit(0)

        deb = time.time()
        pherom.display(screen)
        screen.blit(mazeImg, (0, 0))
        ants.display(screen)
        pg.display.update()

        food_counter = ants.advance(a_maze, pos_food, pos_nest, pherom, food_counter)
        pherom.do_evaporation(pos_food)
        end = time.time()
        if food_counter == 1 and not snapshop_taken:
            pg.image.save(screen, "MyFirstFood.png")
            snapshop_taken = True
        # pg.time.wait(500)
        print(f"FPS : {1. / (end - deb):6.2f}, nourriture : {food_counter:7d}", end='\r')
