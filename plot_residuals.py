import re
import matplotlib.pyplot as plt
from collections import defaultdict
import time
import os

# Function to parse the Elmer log file and extract RELC values and steady state iterations
def parse_elmer_log(log_file, last_position):
    # Dictionary to store RELC values for each solver
    solvers = defaultdict(list)
    steady_state_iterations = []

    # Regular expression pattern to match RELC values and solver names
    relc_pattern = re.compile(r"ComputeChange: NS \(ITER=\d+\) \(NRM,RELC\): \(\s*[\d\.E+-]+\s+([\d\.E+-]+)\s*\)\s+::\s+(.+)")
    # Pattern to match steady state iterations
    steady_state_pattern = re.compile(r"Steady state iteration:\s+(\d+)")

    with open(log_file, 'r') as file:
        # Seek to the last position read in the file
        file.seek(last_position)
        for line in file:
            # Search for RELC values and corresponding solver names
            relc_match = relc_pattern.search(line)
            if relc_match:
                relc_value = float(relc_match.group(1))  # Extract the RELC value
                solver_name = relc_match.group(2)  # Extract the solver name
                solvers[solver_name].append(relc_value)

            # Search for steady state iteration numbers
            steady_state_match = steady_state_pattern.search(line)
            if steady_state_match:
                iteration = int(steady_state_match.group(1))
                steady_state_iterations.append(iteration)
        
        # Get the new last position after reading new lines
        new_position = file.tell()
    
    return solvers, steady_state_iterations, new_position

# Function to continuously update and refresh subplots for RELC and steady-state iterations
def plot_residuals_and_iterations(solvers, steady_state_iterations, ax1, ax2):
    ax1.cla()  # Clear the current plot for RELC values
    ax2.cla()  # Clear the current plot for steady-state iterations

    # Plot RELC values in the first subplot
    for solver_name, relcs in solvers.items():
        iterations = range(1, len(relcs) + 1)
        ax1.plot(iterations, relcs, marker='o', linestyle='-', label=solver_name)
    
    ax1.set_yscale('log')  # Use a logarithmic scale for RELC values
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('RELC (Relative Change)')
    ax1.set_title('Residuals (RELC) vs Iterations for Each Solver')
    ax1.legend()
    ax1.grid(True)

    # Plot steady-state iterations in the second subplot
    if steady_state_iterations:
        ax2.plot(range(1, len(steady_state_iterations) + 1), steady_state_iterations, marker='o', linestyle='-', color='r')
    
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Steady State Iteration')
    ax2.set_title('Steady State Iterations')
    ax2.grid(True)

    plt.pause(1)  # Pause to allow real-time updating

# Main execution
if __name__ == "__main__":
    # Provide the path to your ElmerFEM log file
    log_file = 'simdata/elmersolver.log'  # Adjusted to your provided path
    
    # Initialize last position to 0 (start of file)
    last_position = 0
    
    # Keep running until interrupted or the window is closed
    plt.ion()  # Turn interactive mode on for live updates
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))  # Create two side-by-side subplots
    all_solvers = defaultdict(list)  # Store cumulative data for each solver
    all_steady_state_iterations = []  # Store steady-state iteration data

    try:
        while True:
            # Check if the figure still exists, if not, exit the loop
            if not plt.fignum_exists(fig.number):
                print("Plot window closed. Exiting.")
                break

            if os.path.exists(log_file):
                # Parse the log file from the last position
                new_solvers, new_iterations, last_position = parse_elmer_log(log_file, last_position)
                
                # Merge new_solvers into all_solvers (accumulating data)
                for solver_name, relcs in new_solvers.items():
                    all_solvers[solver_name].extend(relcs)
                
                # Append new steady-state iterations to the list
                all_steady_state_iterations.extend(new_iterations)
                
                # Plot the cumulative RELC values and steady-state iterations
                if all_solvers or all_steady_state_iterations:
                    plot_residuals_and_iterations(all_solvers, all_steady_state_iterations, ax1, ax2)
                
            # Sleep for a short interval before checking for new data
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("Live plotting stopped by user.")
