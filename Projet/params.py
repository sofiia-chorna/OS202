import sys


def get_size_laby(default_size=25):
    if len(sys.argv) > 2:
        return int(sys.argv[1]), int(sys.argv[2])
    return default_size, default_size


def get_resolution(size_laby):
    return size_laby[1] * 8, size_laby[0] * 8


def get_nb_ants(size_laby):
    return size_laby[0] * size_laby[1] // 4


def get_max_life(default_max_life=500):
    if len(sys.argv) > 3:
        return int(sys.argv[3])
    return default_max_life


def get_pos_food(size_laby):
    return size_laby[0] - 1, size_laby[1] - 1


def get_pos_nest():
    return 0, 0


def get_alpha(default_alpha=0.9):
    if len(sys.argv) > 4:
        return float(sys.argv[4])
    return default_alpha


def get_beta(default_beta=0.99):
    if len(sys.argv) > 5:
        return float(sys.argv[5])
    return default_beta


def get_params():
    size_laby = get_size_laby()
    return {
        "size_laby": size_laby,
        "resolution": get_resolution(size_laby),
        "nb_ants": get_nb_ants(size_laby),
        "max_life": get_max_life(),
        "pos_food": get_pos_food(size_laby),
        "pos_nest": get_pos_nest(),
        "alpha": get_alpha(),
        "beta": get_beta()
    }
