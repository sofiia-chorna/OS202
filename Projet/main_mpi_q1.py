import time
import pygame as pg
from mpi4py import MPI
import maze
import pheromone
import colony
import params

# Initialize MPI communication
comm = MPI.COMM_WORLD
size = comm.size
rank = comm.rank

# MPI Tags
TAG_PHEROM = 1
TAG_MAZE = 2

# Flag for game loop
PLAYING = True


def master_display(parameters, snapshop_taken=False, food_counter=0):
    # Initialize pygame screen
    screen_resolution = parameters["resolution"]
    screen = pg.display.set_mode(screen_resolution)

    # Create maze and ants objects
    a_maze = maze.Maze(parameters["size_laby"], seed=12345)
    maze_img = a_maze.display()
    ants = colony.Colony(
        nb_ants=parameters["nb_ants"],
        pos_init=parameters["pos_nest"],
        max_life=parameters["max_life"]
    )

    # Broadcast maze, food counter, and ants information to all processes
    comm.bcast((a_maze.get_maze(), food_counter, ants), root=0)
    ants.init()

    # Receive food counter and pheromone information from all processes
    received_food_counters = []
    pheromones = []
    for i in range(1, size):
        received_food_counter, pherom = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_PHEROM)
        received_food_counters.append(received_food_counter)
        pheromones.append(pherom)

    # Update food counter with the maximum value received
    food_counter = max(received_food_counters)

    # Display the game screen
    start_time = time.time()
    pherom.display(screen)
    screen.blit(maze_img, (0, 0))
    ants.display(screen)
    pg.display.update()
    pherom.do_evaporation(parameters["pos_food"])
    end_time = time.time()

    # Calculate and display FPS
    fps = 1. / (end_time - start_time)
    print(f"FPS: {fps:6.2f}, Food Counter: {food_counter:7d}", end='\r')

    # Save snapshot if food is collected for the first time
    if food_counter == 1 and not snapshop_taken:
        pg.image.save(screen, "MyFirstFood.png")
        snapshop_taken = True

    return snapshop_taken


def slave_calculation():
    # Receive maze, food counter, and ants information from the master process
    a_maze, received_food_counter, ants = comm.bcast(None, root=0)

    # Initialize pheromone object
    pherom = pheromone.Pheromon(
        the_dimensions=parameters["size_laby"],
        the_food_position=parameters["pos_food"],
        the_alpha=parameters["alpha"],
        the_beta=parameters["beta"]
    )

    # Calculate new food counter based on ant movements
    food_counter = ants.advance(
        the_maze=a_maze,
        pos_food=parameters["pos_food"],
        pos_nest=parameters["pos_nest"],
        pheromones=pherom,
        food_counter=received_food_counter
    )

    # Send updated food counter and pheromone information back to the master process
    comm.send((food_counter, pherom), dest=0, tag=TAG_PHEROM)


if __name__ == "__main__":
    pg.init()

    # Get user parameters
    parameters = params.get_params()

    snapshop_taken = False

    while PLAYING:
        # Master process handles display
        if rank == 0:
            snapshop_taken = master_display(parameters, snapshop_taken)

            # Check for events to quit the game
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    PLAYING = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        PLAYING = False

        # Slave processes handle ant movement calculation
        else:
            slave_calculation()

    pg.quit()
