import numpy as np
import direction as d


class Pheromon:
    """
    Class representing pheromones in the maze.
    """

    def __init__(self, dimensions, food_position, alpha=0.7, beta=0.9999):
        """
        Initializes the Pheromon object.

        Args:
            dimensions (tuple): The dimensions of the maze.
            food_position (tuple): The position of the food in the maze.
            alpha (float): The evaporation rate of pheromones.
            beta (float): The persistence rate of pheromones.
        """
        self.alpha = alpha
        self.beta = beta

        # We add a row of cells at the bottom, top, left, and right to facilitate edge management in vectorized form
        self.pheromon = np.zeros((dimensions[0] + 2, dimensions[1] + 2), dtype=np.double)
        self.pheromon[food_position[0] + 1, food_position[1] + 1] = 1.

    def do_evaporation(self, pos_food):
        """
        Performs evaporation of pheromones in the maze.

        Args:
            pos_food (tuple): The position of the food in the maze.
        """
        self.pheromon = self.beta * self.pheromon
        self.pheromon[pos_food[0] + 1, pos_food[1] + 1] = 1.

    def mark(self, position, has_WESN_exits, old_pheromones):
        """
        Marks pheromones at a given position in the maze.

        Args:
            position (tuple): The position to mark pheromones.
            has_WESN_exits (list): List indicating the presence of exits in each cardinal direction.
            old_pheromones (numpy.ndarray): The old pheromone matrix.
        """
        assert position[0] >= 0
        assert position[1] >= 0
        cells = np.array([old_pheromones[position[0] + 1, position[1]] if has_WESN_exits[d.DIR_WEST] else 0.,
                          old_pheromones[position[0] + 1, position[1] + 2] if has_WESN_exits[d.DIR_EAST] else 0.,
                          old_pheromones[position[0] + 2, position[1] + 1] if has_WESN_exits[d.DIR_SOUTH] else 0.,
                          old_pheromones[position[0], position[1] + 1] if has_WESN_exits[d.DIR_NORTH] else 0.],
                         dtype=np.double)
        pheromones = np.maximum(cells, 0.)
        self.pheromon[position[0] + 1, position[1] + 1] = self.alpha * np.max(pheromones) + (1 - self.alpha) * 0.25 * pheromones.sum()

    def get_color(self, i: int, j: int):
        """
        Get the color representation of pheromones at a given position.

        Args:
            i (int): The row index.
            j (int): The column index.

        Returns:
            list: The RGB color representation of pheromones at the specified position.
        """
        val = max(min(self.pheromon[i, j], 1), 0)
        return [255 * (val > 1.E-16), 255 * val, 128.]

    def display(self, screen):
        """
        Displays the pheromone levels on the screen.

        Args:
            screen: The Pygame screen object.
        """
        for i in range(1, self.pheromon.shape[0] - 1):
            for j in range(1, self.pheromon.shape[1] - 1):
                screen.fill(self.get_color(i, j), (8 * (j - 1), 8 * (i - 1), 8, 8))
