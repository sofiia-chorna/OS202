import subprocess
import re
import matplotlib.pyplot as plt


def execute_script(num_processes, timeout=60):
    command = f"mpiexec -n {num_processes} python3 main_mpi.py"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, _ = process.communicate(timeout=timeout)
        output = stdout.decode('utf-8')
        print(f"Output for {num_processes} processes:")
        print("Standard Output:", output)
        # Match FPS mean values in the output
        fps_mean_values = re.findall(r"FPS\s*mean:\s*(\d+\.\d+)", output, re.IGNORECASE)
        return [float(value) for value in fps_mean_values]
    except subprocess.TimeoutExpired:
        print(f"Execution with {num_processes} processes timed out.")
        process.terminate()
        return None


def calculate_speedup(processes, fps_means):
    speedup = []
    for i in range(len(processes)):
        speedup.append(fps_means[0] / fps_means[i] * 100 if fps_means[i] != 0 else 0)  # Handle division by zero
    return speedup


def plot_results(processes, fps_means, speedup):
    plt.plot(processes, fps_means, marker='o', label='FPS Mean')
    plt.plot(processes, speedup, marker='o', label='Speedup')
    plt.title('FPS Mean and Speedup vs Number of Processes')
    plt.xlabel('Number of Processes')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.show()


def generate_readme(processes, fps_means, speedup):
    with open("README.md", "w") as readme:
        readme.write("# Results\n")
        readme.write("## FPS Mean and Speedup vs Number of Processes\n\n")
        readme.write("| Number of Processes | FPS Mean | Speedup |\n")
        readme.write("|---------------------|----------|---------|\n")
        for i in range(len(processes)):
            readme.write(f"| {processes[i]} | {fps_means[i]:.2f} | {speedup[i]:.2f} |\n")


if __name__ == "__main__":
    num_processes_list = [2, 3, 4]
    fps_means = []
    for num_processes in num_processes_list:
        fps_mean_values = execute_script(num_processes)
        print(fps_mean_values)
        if fps_mean_values is not None:
            fps_mean = sum(fps_mean_values) / len(fps_mean_values) if len(
                fps_mean_values) > 0 else 0  # Handle division by zero
            fps_means.append(fps_mean)

    speedup = calculate_speedup(num_processes_list, fps_means)

    print("FPS Mean values:", fps_means)
    print("Speedup values:", speedup)

    plot_results(num_processes_list, fps_means, speedup)
    generate_readme(num_processes_list, fps_means, speedup)
