# Job Status Monitor

The **Job Status Monitor** is a Python package that monitors job statuses on SLURM-based systems, displaying job details such as runtime, status, and log file sizes using the `Rich` library for console output. Additionally, it can store job details in an SQLite database and allows dynamic updates to configuration settings via command-line arguments. This is helpful when one is running many jobs together and want to monitor the status of jobs including whether there are any errors or not.

## Features

- Display active job statuses (job ID, name, status, runtime, nodes, CPUs) in a rich, styled table.
- Check and display the sizes of job log files (`log.out` and `log.err`).
- Automatically store job details in an SQLite database.
- Dynamically update configuration settings (such as log file paths and username) through command-line arguments.
- Automatically handle user input, allowing users to expand job details or quit the program.

## Requirements

- Python 3.6+
- SLURM Workload Manager
- SQLite
- Required Python libraries:
  - `rich`
  - `pyyaml`

## Installation

1. Clone the repository or download the package:

   ```bash
   git clone https://github.com/earthinversion/job_status_hpc
   cd job_status_hpc
   ```
2. Install the package locally:
    ```bash
    pip install .
    ```
3. Verify the installation:
    ```bash
    job-status --help
    ```

## Usage
Run the package by using the following command:
```bash
job-status
```
This will display job statuses in a table format, pulling information from SLURM.

## Command-Line Arguments
You can also dynamically update the configuration by passing arguments directly to the job-status command:

- Change the log output file:
```bash
job-status --log_out_file new_log_out.log
```
- Change the log error file:
```bash
job-status --log_err_file new_log_err.err
```
- Change the username:
```bash
job-status --username new_username
```

These changes will be reflected in the config.yaml file, and the new settings will be used in future runs.

```bash
job-status --log_out_file my_log_out.log --log_err_file my_log_err.err --username user123
```

This will update the configuration to use my_log_out.log, my_log_err.err, and user123 for the job monitoring process.

## Configuration
The package uses a config.yaml file to store settings such as the username, log output file, and log error file. You can modify these values either by editing the file manually or by using the command-line options described above.

Default `config.yaml`:
```
username: your_username
log_out_file: "log.out"
log_err_file: "log.err"
```

### Location of config.yaml
The config.yaml file is stored in the package directory. You can find and edit it there if necessary.

## Logging and Data Storage
- Job Details Storage: The job status details are stored in an SQLite database (job_status.db), which keeps track of jobs that have finished or are still running.
- Log File Sizes: The sizes of the log.out and log.err files are dynamically calculated and displayed in the job table.