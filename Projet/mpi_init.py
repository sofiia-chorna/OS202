from mpi4py import MPI


def initialize_mpi():
    """
    Initializes MPI communication.
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Create new communicator group excluding rank 0
    new_comm = comm.Create_group(comm.group.Excl([0]))
    if rank != 0:
        rank_new = new_comm.Get_rank()
        size_new = new_comm.Get_size()
    else:
        rank_new = None
        size_new = None

    # Create communicator group including ranks 0 and 1 for display
    comm_display = comm.Create_group(comm.group.Incl([0, 1]))

    return comm, rank, size, new_comm, comm_display, rank_new, size_new
