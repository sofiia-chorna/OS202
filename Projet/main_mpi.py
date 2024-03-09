import maze
import pheromone
import pygame as pg
from math import floor
import colony
import sys
import time
from mpi_init import initialize_mpi

# Initialize MPI communication
comm, rank, size, new_comm, comm_display, rank_new, size_new = initialize_mpi()


def initialize_screen():
    """
    Initializes the Pygame screen.
    """
    pg.init()
    size_laby = (25, 25)
    if len(sys.argv) > 2:
        size_laby = (int(sys.argv[1]), int(sys.argv[2]))
    resolution = size_laby[1] * 8, size_laby[0] * 8
    if rank == 0:
        screen = pg.display.set_mode(resolution)
    if rank != 0:
        screen = pg.display.set_mode((0, 0), pg.HIDDEN | pg.NOFRAME | pg.HWSURFACE | pg.DOUBLEBUF)
    return screen, size_laby


def initialize_parameters():
    """
    Initializes parameters such as number of ants, max life, etc.
    """
    nb_ants = size_laby[0] * size_laby[1] // 4
    max_life = 500
    if len(sys.argv) > 3:
        max_life = int(sys.argv[3])
    pos_food = size_laby[0] - 1, size_laby[1] - 1
    pos_nest = 0, 0
    alpha = 0.9
    beta = 0.99
    max_iterations = 5000  # Default value
    if len(sys.argv) > 4:
        alpha = float(sys.argv[4])
    if len(sys.argv) > 5:
        beta = float(sys.argv[5])
    if len(sys.argv) > 6:
        max_iterations = int(sys.argv[6])
    return nb_ants, max_life, pos_food, pos_nest, alpha, beta, max_iterations


def divide_ants_among_processes(nb_ants, max_life, pos_nest):
    """
    Divides ants among processes.
    """
    if rank == 0:
        ants = colony.Colony(nb_ants, pos_nest, max_life, 0, nb_ants)
    if rank != 0:
        index_min = floor(rank_new * nb_ants / size_new)
        index_max = floor((rank_new + 1) * nb_ants / size_new)
        ants = colony.Colony(index_max - index_min, pos_nest, max_life, index_min, index_max)
    return ants


if __name__ == "__main__":
    screen, size_laby = initialize_screen()
    nb_ants, max_life, pos_food, pos_nest, alpha, beta, max_iterations = initialize_parameters()
    ants = divide_ants_among_processes(nb_ants, max_life, pos_nest)
    a_maze = maze.Maze(size_laby, 12345)
    pherom = pheromone.Pheromon(size_laby, pos_food, alpha, beta)

    # Main loop
    food_counter = 0
    fps_counter = 0
    fps_mean = 0
    iteration = 0  # Initialize iteration count
    finish = False

    while not finish and iteration < max_iterations:  # Stop loop when reaching max_iterations
        # Handle events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                finish = True

        # Broadcast finish flag to all processes
        finish = comm.bcast(finish, root=0)
        if finish:
            exit(0)

        # Display environment
        pherom.display(screen)
        screen.blit(a_maze.display(), (0, 0))
        ants.display(screen)
        pg.display.update()

        # Time measurement
        deb = time.time()

        # Divide work between processes
        food_counter = ants.advance(a_maze, pos_food, pos_nest, pherom, food_counter)
        pherom.do_evaporation(pos_food)

        end = time.time()

        # Update FPS mean
        fps_counter += 1
        fps_mean += 1. / (end - deb)
        if fps_counter == 100:
            fps_counter = 1
            fps_mean = 0
        print(f"FPS mean: {fps_mean / fps_counter:10.2f}, FPS counter: {fps_counter}, nourriture : {food_counter}", end='\r')

        iteration += 1  # Increment iteration count
