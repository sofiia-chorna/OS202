import pygame as pg


class App:
    """
    Cette classe décrit la fenêtre affichant la grille à l'écran
        - geometry est un tuple de deux entiers donnant le nombre de pixels verticaux et horizontaux (dans cet ordre)
        - grid est la grille décrivant l'automate cellulaire (voir plus haut)
    """

    def __init__(self, geometry, grid):
        self.grid = grid
        # Calcul de la taille d'une cellule par rapport à la taille de la fenêtre et de la grille à afficher :
        self.size_x = geometry[1] // grid.dimensions[1]
        self.size_y = geometry[0] // grid.dimensions[0]
        if self.size_x > 4 and self.size_y > 4:
            self.draw_color = pg.Color('lightgrey')
        else:
            self.draw_color = None

        # Ajustement de la taille de la fenêtre pour bien fitter la dimension de la grille
        self.width = grid.dimensions[1] * self.size_x
        self.height = grid.dimensions[0] * self.size_y

        # Création de la fenêtre à l'aide de tkinter
        self.screen = pg.display.set_mode((self.width, self.height))
        self.canvas_cells = []

    def compute_rectangle(self, i: int, j: int):
        """
        Calcul la géométrie du rectangle correspondant à la cellule (i,j)
        """
        return self.size_x * j, self.height - self.size_y * i - 1, self.size_x, self.size_y

    def compute_color(self, i: int, j: int):
        if self.grid.cells[i, j] == 0:
            return self.grid.col_dead
        else:
            return self.grid.col_life

    def draw(self):
        [self.screen.fill(self.compute_color(i, j), self.compute_rectangle(i, j)) for i in
         range(self.grid.dimensions[0]) for j in range(self.grid.dimensions[1])]
        if self.draw_color is not None:
            [pg.draw.line(self.screen, self.draw_color, (0, i * self.size_y), (self.width, i * self.size_y)) for i in
             range(self.grid.dimensions[0])]
            [pg.draw.line(self.screen, self.draw_color, (j * self.size_x, 0), (j * self.size_x, self.height)) for j in
             range(self.grid.dimensions[1])]
        pg.display.update()
