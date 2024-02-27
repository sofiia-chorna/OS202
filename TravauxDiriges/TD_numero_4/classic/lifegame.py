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
import patterns
from app import App

class Grille:
    """
    Grille torique décrivant l'automate cellulaire.
    En entrée lors de la création de la grille :
        - dimensions est un tuple contenant le nombre de cellules dans les deux directions (nombre lignes, nombre colonnes)
        - init_pattern est une liste de cellules initialement vivantes sur cette grille (les autres sont considérées comme mortes)
        - color_life est la couleur dans laquelle on affiche une cellule vivante
        - color_dead est la couleur dans laquelle on affiche une cellule morte
    Si aucun pattern n'est donné, on tire au hasard quels sont les cellules vivantes et les cellules mortes
    Exemple :
       grid = Grille( (10,10), init_pattern=[(2,2),(0,2),(4,2),(2,0),(2,4)], color_life=pg.Color("red"), color_dead=pg.Color("black"))
    """

    def __init__(self, dim, init_pattern=None, color_life=pg.Color("black"), color_dead=pg.Color("white")):
        self.dimensions = dim
        if init_pattern is not None:
            self.cells = np.zeros(self.dimensions, dtype=np.uint8)
            indices_i = [v[0] for v in init_pattern]
            indices_j = [v[1] for v in init_pattern]
            self.cells[indices_i, indices_j] = 1
        else:
            self.cells = np.random.randint(2, size=dim, dtype=np.uint8)
        self.col_life = color_life
        self.col_dead = color_dead

    def compute_next_iteration(self):
        """
        Calcule la prochaine génération de cellules en suivant les règles du jeu de la vie
        """
        # Remarque 1: on pourrait optimiser en faisant du vectoriel, mais pour plus de clarté, on utilise les boucles
        # Remarque 2: on voit la grille plus comme une matrice qu'une grille géométrique. L'indice (0,0) est donc en haut
        #             à gauche de la grille !
        ny = self.dimensions[0]
        nx = self.dimensions[1]
        next_cells = np.empty(self.dimensions, dtype=np.uint8)
        diff_cells = []
        for i in range(ny):
            i_above = (i + ny - 1) % ny
            i_below = (i + 1) % ny
            for j in range(nx):
                j_left = (j - 1 + nx) % nx
                j_right = (j + 1) % nx
                voisins_i = [i_above, i_above, i_above, i, i, i_below, i_below, i_below]
                voisins_j = [j_left, j, j_right, j_left, j_right, j_left, j, j_right]
                voisines = np.array(self.cells[voisins_i, voisins_j])
                nb_voisines_vivantes = np.sum(voisines)
                if self.cells[i, j] == 1:  # Si la cellule est vivante
                    if (nb_voisines_vivantes < 2) or (nb_voisines_vivantes > 3):
                        next_cells[i, j] = 0  # Cas de sous ou sur population, la cellule meurt
                        diff_cells.append(i * nx + j)
                    else:
                        next_cells[i, j] = 1  # Sinon elle reste vivante
                elif nb_voisines_vivantes == 3:  # Cas où cellule morte mais entourée exactement de trois vivantes
                    next_cells[i, j] = 1  # Naissance de la cellule
                    diff_cells.append(i * nx + j)
                else:
                    next_cells[i, j] = 0  # Morte, elle reste morte.
        self.cells = next_cells
        return diff_cells


if __name__ == '__main__':
    import time
    import sys

    pg.init()

    choice = 'glider'
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    resx = 800
    resy = 800
    if len(sys.argv) > 3:
        resx = int(sys.argv[2])
        resy = int(sys.argv[3])
    print(f"Pattern initial choisi : {choice}")
    print(f"resolution ecran : {resx, resy}")
    try:
        init_pattern = patterns.DICO_PATTERNS[choice]
    except KeyError:
        print("No such pattern. Available ones are:", patterns.DICO_PATTERNS.keys())
        exit(1)
    grid = Grille(*init_pattern)
    appli = App((resx, resy), grid)

    while True:
        # time.sleep(0.5) # A régler ou commenter pour vitesse maxi
        t1 = time.time()
        diff = grid.compute_next_iteration()
        t2 = time.time()
        appli.draw()
        t3 = time.time()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
        print(
            f"Temps calcul prochaine generation : {t2 - t1:2.2e} secondes, temps affichage : {t3 - t2:2.2e} secondes\r",
            end='')
