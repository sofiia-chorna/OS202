"""
Module managing an ant colony in a labyrinth.
"""
import numpy as np
import maze
import direction as d
import pygame as pg
from mpi4py import MPI
from mpi_init import initialize_mpi

# Initialize MPI communication
comm, rank, size, new_comm, comm_display, rank_new, size_new = initialize_mpi()

# Constants
UNLOADED, LOADED = False, True
EXPLORATION_COEFFICIENT = 0.


class Colony:
    def __init__(self, num_ants, initial_position, max_life, min_index, max_index):
        # Parameters
        self.min_index = min_index
        self.max_index = max_index
        self.sprites = []

        # Initialize colony attributes
        self._init_colony(num_ants, initial_position, max_life)

    def _init_colony(self, num_ants, initial_position, max_life):
        # Initialize ant attributes
        self._init_ant_attributes(num_ants, max_life, initial_position)

        # Initialize ant sprites
        self._init_ant_sprites()

    def _init_ant_attributes(self, num_ants, max_life, initial_position):
        # Generate unique random seeds for each ant
        self.seeds = np.arange(self.min_index + 1, self.max_index + 1, dtype=np.int64)

        # State of each ant: loaded or unloaded
        self.is_loaded = np.zeros(num_ants, dtype=np.int8)

        # Compute the maximal life amount for each ant
        self.max_life = max_life * np.ones(num_ants, dtype=np.int32)
        self.max_life -= np.int32(max_life * (self.seeds / 2147483647.)) // 4

        # Ages of ants: zero at the beginning
        self.age = np.zeros(num_ants, dtype=np.int64)

        # History of the path taken by each ant
        self.historic_path = np.zeros((num_ants, max_life + 1, 2), dtype=np.int16)
        self.historic_path[:, 0, 0] = initial_position[0]
        self.historic_path[:, 0, 1] = initial_position[1]

        # Direction in which the ant is currently facing
        self.directions = d.DIR_NONE * np.ones(num_ants, dtype=np.int8)

    def _init_ant_sprites(self):
        # Load ant sprites
        img = pg.image.load("ants.png").convert_alpha()
        for i in range(0, 32, 8):
            self.sprites.append(pg.Surface.subsurface(img, i, 0, 8, 8))

    def return_to_nest(self, loaded_ants, nest_position, food_counter):
        """
        Return ants carrying food to their nests.

        Args:
            loaded_ants: Indices of ants carrying food.
            nest_position: Position of the nest.
            food_counter: Current quantity of food in the nest.

        Returns:
            The updated quantity of food in the nest.
        """
        self.age[loaded_ants] -= 1

        in_nest_tmp = self.historic_path[loaded_ants, self.age[loaded_ants], :] == nest_position
        if in_nest_tmp.any():
            in_nest_loc = np.nonzero(np.logical_and(in_nest_tmp[:, 0], in_nest_tmp[:, 1]))[0]
            if in_nest_loc.shape[0] > 0:
                in_nest = loaded_ants[in_nest_loc]
                self.is_loaded[in_nest] = UNLOADED
                self.age[in_nest] = 0
                food_counter += in_nest_loc.shape[0]

        return food_counter

    def advance(self, the_maze, food_position, nest_position, pheromones, food_counter=0):
        # Rank 0 initialization
        if rank == 0:
            results_hist = []
            results_seeds = []
            results_is_loaded = []
            results_max_life = []
            results_age = []
            results_directions = []

        # Communication barrier
        if not new_comm == MPI.COMM_NULL:
            loaded_ants = np.nonzero(self.is_loaded == True)[0]
            unloaded_ants = np.nonzero(self.is_loaded == False)[0]

            # Return loaded ants to the nest
            if food_counter is None:
                food_counter = 0
            if loaded_ants.shape[0] > 0:
                food_counter = self.return_to_nest(loaded_ants, nest_position, food_counter)
            new_comm.barrier()

        # Reduce food counter across processes
        food_counter = comm.reduce(food_counter, op=MPI.SUM, root=0)

        # Exploration and pheromone update
        if not new_comm == MPI.COMM_NULL:
            if unloaded_ants.shape[0] > 0:
                self.explore(unloaded_ants, the_maze, food_position, nest_position, pheromones)
            new_comm.barrier()

            # Update pheromones
            old_pos_ants = self.historic_path[range(0, self.seeds.shape[0]), self.age[:], :]
            has_north_exit = np.bitwise_and(the_maze.maze[old_pos_ants[:, 0], old_pos_ants[:, 1]], maze.NORTH) > 0
            has_east_exit = np.bitwise_and(the_maze.maze[old_pos_ants[:, 0], old_pos_ants[:, 1]], maze.EAST) > 0
            has_south_exit = np.bitwise_and(the_maze.maze[old_pos_ants[:, 0], old_pos_ants[:, 1]], maze.SOUTH) > 0
            has_west_exit = np.bitwise_and(the_maze.maze[old_pos_ants[:, 0], old_pos_ants[:, 1]], maze.WEST) > 0

            # Marking pheromones
            old_pheromones = pheromones.pheromon.copy()
            [pheromones.mark(self.historic_path[i, self.age[i], :],
                             [has_north_exit[i], has_east_exit[i], has_west_exit[i], has_south_exit[i]],
                             old_pheromones) for i in range(self.directions.shape[0])]
            result = np.zeros_like(pheromones.pheromon)
            new_comm.Allreduce(pheromones.pheromon, result, op=MPI.MAX)
            pheromones.pheromon = result.copy()

        # Broadcast updated pheromones
        if not comm_display == MPI.COMM_NULL:
            pheromones.pheromon = comm_display.bcast(pheromones.pheromon, root=1)

        # Send/receive data between processes
        if rank != 0:
            comm.send(self.seeds, dest=0, tag=rank * 1)
            comm.send(self.is_loaded, dest=0, tag=rank * 2)
            comm.send(self.max_life, dest=0, tag=rank * 3)
            comm.send(self.age, dest=0, tag=rank * 4)
            comm.send(self.historic_path, dest=0, tag=rank * 5)
            comm.send(self.directions, dest=0, tag=rank * 6)

        # Gather data at rank 0
        if rank == 0:
            for i in range(1, size):
                results_seeds.append(comm.recv(source=i, tag=i * 1))
                results_is_loaded.append(comm.recv(source=i, tag=i * 2))
                results_max_life.append(comm.recv(source=i, tag=i * 3))
                results_age.append(comm.recv(source=i, tag=i * 4))
                results_hist.append(comm.recv(source=i, tag=i * 5))
                results_directions.append(comm.recv(source=i, tag=i * 6))

            # Concatenate received data
            self.seeds = np.hstack(results_seeds)
            self.is_loaded = np.hstack(results_is_loaded)
            self.max_life = np.hstack(results_max_life)
            self.age = np.hstack(results_age)
            self.historic_path = np.vstack(results_hist)
            self.directions = np.hstack(results_directions)

        return food_counter

    def explore(self, unloaded_ants, the_maze, food_position, nest_position, pheromones):
        """
        Manage unloaded ants exploring the maze.

        Args:
            unloaded_ants: Indices of ants that are not loaded.
            the_maze: The maze in which ants move.
            food_position: Position of food in the maze.
            nest_position: Position of the ants' nest in the maze.
            pheromones: The pheromone map.

        Returns:
            None
        """
        # Update random seeds for unloaded ants
        self.seeds[unloaded_ants] = np.mod(16807 * self.seeds[unloaded_ants], 2147483647)
        choices = self.seeds[:] / 2147483647.

        # Calculate possible exits for each ant in the maze
        old_pos_ants = self.historic_path[range(0, self.seeds.shape[0]), self.age[:], :]
        has_north_exit = np.bitwise_and(the_maze.maze[old_pos_ants[:, 0], old_pos_ants[:, 1]], maze.NORTH) > 0
        has_east_exit = np.bitwise_and(the_maze.maze[old_pos_ants[:, 0], old_pos_ants[:, 1]], maze.EAST) > 0
        has_south_exit = np.bitwise_and(the_maze.maze[old_pos_ants[:, 0], old_pos_ants[:, 1]], maze.SOUTH) > 0
        has_west_exit = np.bitwise_and(the_maze.maze[old_pos_ants[:, 0], old_pos_ants[:, 1]], maze.WEST) > 0

        # Read neighboring pheromones
        north_pos = np.copy(old_pos_ants)
        north_pos[:, 1] += 1
        north_pheromone = pheromones.pheromon[north_pos[:, 0], north_pos[:, 1]] * has_north_exit

        # Similar calculations for east, south, and west
        east_pos = np.copy(old_pos_ants)
        east_pos[:, 0] += 1
        east_pos[:, 1] += 2
        east_pheromone = pheromones.pheromon[east_pos[:, 0], east_pos[:, 1]] * has_east_exit

        south_pos = np.copy(old_pos_ants)
        south_pos[:, 0] += 2
        south_pos[:, 1] += 1
        south_pheromone = pheromones.pheromon[south_pos[:, 0], south_pos[:, 1]] * has_south_exit

        west_pos = np.copy(old_pos_ants)
        west_pos[:, 0] += 1
        west_pheromone = pheromones.pheromon[west_pos[:, 0], west_pos[:, 1]] * has_west_exit

        max_pheromones = np.maximum(north_pheromone, east_pheromone)
        max_pheromones = np.maximum(max_pheromones, south_pheromone)
        max_pheromones = np.maximum(max_pheromones, west_pheromone)

        # Ants explore the maze by choice or if no pheromone can guide them
        ind_exploring_ants = \
            np.nonzero(np.logical_or(choices[unloaded_ants] <= EXPLORATION_COEFFICIENT, max_pheromones[unloaded_ants] == 0.))[
                0]
        if ind_exploring_ants.shape[0] > 0:
            ind_exploring_ants = unloaded_ants[ind_exploring_ants]
            valid_moves = np.zeros(choices.shape[0], np.int8)
            nb_exits = has_north_exit * np.ones(has_north_exit.shape) + has_east_exit * np.ones(has_east_exit.shape) + \
                       has_south_exit * np.ones(has_south_exit.shape) + has_west_exit * np.ones(has_west_exit.shape)
            while np.any(valid_moves[ind_exploring_ants] == 0):
                ind_ants_to_move = ind_exploring_ants[valid_moves[ind_exploring_ants] == 0]
                self.seeds[:] = np.mod(16807 * self.seeds[:], 2147483647)
                dir = np.mod(self.seeds[ind_ants_to_move], 4)
                old_pos = self.historic_path[ind_ants_to_move, self.age[ind_ants_to_move], :]
                new_pos = np.copy(old_pos)
                new_pos[:, 1] -= (
                        np.logical_and(dir == d.DIR_WEST, has_west_exit[ind_ants_to_move])
                        * np.ones(new_pos.shape[0], dtype=np.int16)
                )

                new_pos[:, 1] += (
                        np.logical_and(dir == d.DIR_EAST, has_east_exit[ind_ants_to_move])
                        * np.ones(new_pos.shape[0], dtype=np.int16)
                )
                new_pos[:, 0] -= (np.logical_and(
                    dir == d.DIR_NORTH, has_north_exit[ind_ants_to_move])
                                  * np.ones(new_pos.shape[0], dtype=np.int16)
                                  )
                new_pos[:, 0] += (np.logical_and(
                    dir == d.DIR_SOUTH, has_south_exit[ind_ants_to_move])
                                  * np.ones(new_pos.shape[0], dtype=np.int16)
                                  )
                valid_moves[ind_ants_to_move] = np.logical_or(new_pos[:, 0] != old_pos[:, 0],
                                                              new_pos[:, 1] != old_pos[:, 1])
                valid_moves[ind_ants_to_move] = np.logical_and(
                    valid_moves[ind_ants_to_move],
                    np.logical_or(dir != 3 - self.directions[ind_ants_to_move], nb_exits[ind_ants_to_move] == 1))
                ind_valid_moves = ind_ants_to_move[np.nonzero(valid_moves[ind_ants_to_move])[0]]
                self.historic_path[ind_valid_moves, self.age[ind_valid_moves] + 1, :] \
                    = new_pos[valid_moves[ind_ants_to_move] == 1, :]
                self.directions[ind_valid_moves] = dir[valid_moves[ind_ants_to_move] == 1]

        ind_following_ants = np.nonzero(np.logical_and(choices[unloaded_ants] > EXPLORATION_COEFFICIENT,
                                                       max_pheromones[unloaded_ants] > 0.))[0]
        if ind_following_ants.shape[0] > 0:
            ind_following_ants = unloaded_ants[ind_following_ants]
            self.historic_path[ind_following_ants, self.age[ind_following_ants] + 1, :] = \
                self.historic_path[ind_following_ants, self.age[ind_following_ants], :]
            max_east = (east_pheromone[ind_following_ants] == max_pheromones[ind_following_ants])
            self.historic_path[ind_following_ants, self.age[ind_following_ants] + 1, 1] += \
                max_east * np.ones(ind_following_ants.shape[0], dtype=np.int16)
            max_west = (west_pheromone[ind_following_ants] == max_pheromones[ind_following_ants])
            self.historic_path[ind_following_ants, self.age[ind_following_ants] + 1, 1] -= \
                max_west * np.ones(ind_following_ants.shape[0], dtype=np.int16)
            max_north = (north_pheromone[ind_following_ants] == max_pheromones[ind_following_ants])
            self.historic_path[ind_following_ants, self.age[ind_following_ants] + 1, 0] -= max_north * np.ones(
                ind_following_ants.shape[0], dtype=np.int16)
            max_south = (south_pheromone[ind_following_ants] == max_pheromones[ind_following_ants])
            self.historic_path[ind_following_ants, self.age[ind_following_ants] + 1, 0] += max_south * np.ones(
                ind_following_ants.shape[0], dtype=np.int16)

        # Age ants not carrying food
        if unloaded_ants.shape[0] > 0:
            self.age[unloaded_ants] += 1

        # Kill ants at the end of their life
        ind_dying_ants = np.nonzero(self.age == self.max_life)[0]
        if ind_dying_ants.shape[0] > 0:
            self.age[ind_dying_ants] = 0
            self.historic_path[ind_dying_ants, 0, 0] = nest_position[0]
            self.historic_path[ind_dying_ants, 0, 1] = nest_position[1]
            self.directions[ind_dying_ants] = d.DIR_NONE

        # Update state for ants reaching food
        ants_at_food_loc = \
            np.nonzero(np.logical_and(self.historic_path[unloaded_ants, self.age[unloaded_ants], 0] == food_position[0],
                                      self.historic_path[unloaded_ants, self.age[unloaded_ants], 1] == food_position[1]))[0]
        if ants_at_food_loc.shape[0] > 0:
            ants_at_food = unloaded_ants[ants_at_food_loc]
            self.is_loaded[ants_at_food] = True

    def display(self, screen):
        [screen.blit(self.sprites[self.directions[i]],
                     (8 * self.historic_path[i, self.age[i], 1], 8 * self.historic_path[i, self.age[i], 0])) for i in
         range(self.directions.shape[0])]
