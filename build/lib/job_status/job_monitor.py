import os
import time
import subprocess
import signal
import sys
import threading
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from .database import init_db, store_job_info
import yaml
import argparse
import pkg_resources

console = Console()

# Load configuration from config.yaml
def load_config():
    config_path = pkg_resources.resource_filename(__name__, 'config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config, config_path

# Save updated configuration back to config.yaml
def save_config(config, config_path):
    with open(config_path, 'w') as file:
        yaml.dump(config, file)

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Monitor job status and log files.")
    
    # Add options for updating the config file
    parser.add_argument("--log_out_file", type=str, help="New log.out file name")
    parser.add_argument("--log_err_file", type=str, help="New log.err file name")
    parser.add_argument("--username", type=str, help="New username")

    return parser.parse_args()

def update_config_if_needed(args, config, config_path):
    updated = False
    
    # Update config if command-line options are provided
    if args.log_out_file:
        config['log_out_file'] = args.log_out_file
        updated = True
    if args.log_err_file:
        config['log_err_file'] = args.log_err_file
        updated = True
    if args.username:
        config['username'] = args.username
        updated = True
    
    # Save the updated config file if any changes were made
    if updated:
        console.print("[yellow]Updating configuration file...[/yellow]")
        save_config(config, config_path)
        console.print("[green]Configuration file updated successfully![/green]")


# Fetch job information from the system
def get_job_info(username):
    command = f"squeue -u {username} -h -o '%A|%j|%T|%M|%D|%C'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    job_info_lines = result.stdout.strip().split('\n')

    jobs = []
    for line in job_info_lines:
        if line:
            job_id, job_name, job_status, run_time, nodes, cpus = line.split('|')
            jobs.append((job_id, job_name, job_status, run_time, nodes, cpus))
    return jobs

# Get directory where job logs are stored
def get_job_directory(job_id):
    scontrol_command = f"scontrol show job {job_id} | grep 'WorkDir='"
    scontrol_result = subprocess.run(scontrol_command, shell=True, capture_output=True, text=True)

    directory_line = scontrol_result.stdout.strip()
    if directory_line:
        return directory_line.split('=')[1]
    return None

# Check the sizes of log.err and log.out files
def get_file_size_in_kb(file_path):
    """Returns the size of the file in KB."""
    if os.path.exists(file_path):
        file_size_in_bytes = os.path.getsize(file_path)
        file_size_in_kb = file_size_in_bytes / 1024  # Convert bytes to KB
        return f"{file_size_in_kb:.2f} KB"
    return "N/A"

def check_log_file_sizes(directory, log_err_file, log_out_file):
    """Check the sizes of the log.err and log.out files in KB."""
    if directory:
        log_err_path = os.path.join(directory, log_err_file)
        log_out_path = os.path.join(directory, log_out_file)

        err_file_size = get_file_size_in_kb(log_err_path)
        out_file_size = get_file_size_in_kb(log_out_path)

        return err_file_size, out_file_size
    return "N/A", "N/A"


# Display job information in a table
def display_job_table(username, log_err_file, log_out_file):
    conn, cursor = init_db()  # Initialize database connection
    global keep_running
    while keep_running:
        jobs = get_job_info(username)
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("JOBID")
        table.add_column("JOBNAME")
        table.add_column("JOB STATUS")
        table.add_column("RUN TIME")
        table.add_column("NODES")
        table.add_column("CPUS")
        table.add_column("LOG.ERR SIZE (KB)")
        table.add_column("LOG.OUT SIZE (KB)")

        if jobs:
            for job_id, job_name, job_status, run_time, nodes, cpus in jobs:
                directory = get_job_directory(job_id)
                err_file_size, out_file_size = check_log_file_sizes(directory, log_err_file, log_out_file)

                # Store the job info in SQLite
                store_job_info(job_id, job_name, job_status, run_time, nodes, cpus, err_file_size, out_file_size)
                
                table.add_row(job_id, job_name, job_status, run_time, nodes, cpus, err_file_size, out_file_size)
                
            console.clear()
            console.print(table)
            console.print("\n[green]Type 'q' to quit or enter a JOBID to see more details.[/green]\n")
        else:
            console.clear()
            console.print("[yellow]No active jobs. Displaying finished jobs:[/yellow]\n")

            cursor.execute("SELECT * FROM job_status ORDER BY timestamp DESC")
            finished_jobs = cursor.fetchall()

            for job in finished_jobs:
                job_id, job_name, job_status, run_time, nodes, cpus, err_file_size, out_file_size, timestamp = job
                table.add_row(job_id, job_name, job_status, run_time, nodes, cpus, err_file_size, out_file_size)
            
            console.print(table)

        time.sleep(5)

# Handle program exit
def handle_exit_signal(signum, frame):
    global keep_running
    print("\nExiting...")
    keep_running = False
    sys.exit(0)

# Main function to start job monitoring
def check_job_status(username, log_err_file, log_out_file):
    global keep_running
    keep_running = True

    # Register signal handler for keyboard interrupt
    signal.signal(signal.SIGINT, handle_exit_signal)

    update_thread = threading.Thread(target=display_job_table, args=(username, log_err_file, log_out_file))
    update_thread.daemon = True
    update_thread.start()

    while keep_running:
        job_id_input = Prompt.ask("\nEnter JOBID to expand for more info or 'q' to quit", default="q")
        
        if job_id_input == "q":
            console.print("Exiting...")
            keep_running = False
            break


def main():
    # Load config and parse arguments
    config, config_path = load_config()
    args = parse_arguments()

    # Update config if new options are provided
    update_config_if_needed(args, config, config_path)

    # Use the updated config values
    username = config['username']
    log_out_file = config['log_out_file']
    log_err_file = config['log_err_file']

    check_job_status(username, log_err_file, log_out_file)
