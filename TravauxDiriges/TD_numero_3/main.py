import subprocess
import matplotlib.pyplot as plt
from tabulate import tabulate


def execute_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout.strip()
    # Extract execution time from the output
    execution_time = float(output.split()[-1])
    return execution_time


def main():
    values = [2, 3, 4]
    execution_times_mpi = []
    execution_times_normal = []

    table_data = []

    for value in values:
        # Execute MPI command
        command_mpi = f"mpiexec -np {value} python3 bucket_sort_mpi.py"
        execution_time_mpi = execute_command(command_mpi)
        execution_times_mpi.append(execution_time_mpi)

        # Execute normal command
        command_normal = f"python3 bucket_sort.py {value}"
        execution_time_normal = execute_command(command_normal)
        execution_times_normal.append(execution_time_normal)

        # Add data to table
        table_data.append([value, execution_time_mpi, execution_time_normal])

    # Plotting
    plt.plot(values, execution_times_mpi, label='MPI Execution Time')
    plt.plot(values, execution_times_normal, label='Normal Execution Time')
    plt.xlabel('Number of Processes / Values')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Comparison of Execution Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('execution_time_comparison.png')

    # Print table
    headers = ['N processes / buckets', 'MPI Execution Time', 'Normal Execution Time']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


if __name__ == "__main__":
    main()
