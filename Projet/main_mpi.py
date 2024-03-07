import time
import pygame as pg
from mpi4py import MPI
import maze
import pheromone
import colony
import params

comm = MPI.COMM_WORLD.Dup()
size = comm.size
rank = comm.rank

# Tags
TAG_PHEROM = 1
TAG_MAZE = 2

PLAYING = True


def display(parameters, snapshop_taken=False, food_counter=0):
    screen_resolution = parameters["resolution"]
    screen = pg.display.set_mode(screen_resolution)
    a_maze = maze.Maze(parameters["size_laby"], seed=12345)
    maze_img = a_maze.display()
    ants = colony.Colony(
        nb_ants=parameters["nb_ants"],
        pos_init=parameters["pos_nest"],
        max_life=parameters["max_life"]
    )

    comm.bcast((a_maze.get_maze(), food_counter, ants), root=0)
    ants.init()

    received_food_counter, pherom = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_PHEROM)
    food_counter = received_food_counter

    start_time = time.time()
    pherom.display(screen)
    screen.blit(maze_img, (0, 0))
    ants.display(screen)
    pg.display.update()
    pherom.do_evaporation(parameters["pos_food"])
    end_time = time.time()

    fps = 1. / (end_time - start_time)
    print(f"FPS: {fps:6.2f}, Food Counter: {food_counter:7d}", end='\r')

    if food_counter == 1 and not snapshop_taken:
        pg.image.save(screen, "MyFirstFood.png")
        snapshop_taken = True


def calculation():
    a_maze, received_food_counter, ants = comm.bcast(None, root=0)
    pherom = pheromone.Pheromon(
        the_dimensions=parameters["size_laby"],
        the_food_position=parameters["pos_food"],
        the_alpha=parameters["alpha"],
        the_beta=parameters["beta"]
    )
    food_counter = ants.advance(
        the_maze=a_maze,
        pos_food=parameters["pos_food"],
        pos_nest=parameters["pos_nest"],
        pheromones=pherom,
        food_counter=received_food_counter
    )

    comm.send((food_counter, pherom), dest=0, tag=TAG_PHEROM)


if __name__ == "__main__":
    pg.init()

    # Get user params
    parameters = params.get_params()

    while PLAYING:
        # Master
        if rank == 0:
            display(parameters)

        # Slave
        else:
            calculation()
