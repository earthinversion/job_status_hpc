import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('job_status.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS job_status (
                        job_id TEXT PRIMARY KEY,
                        job_name TEXT,
                        job_status TEXT,
                        run_time TEXT,
                        nodes TEXT,
                        cpus TEXT,
                        log_err_size TEXT,
                        log_out_size TEXT,
                        timestamp TEXT
                    )''')
    conn.commit()
    return conn, cursor

def store_job_info(job_id, job_name, job_status, run_time, nodes, cpus, log_err_size, log_out_size):
    conn, cursor = init_db()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''INSERT OR REPLACE INTO job_status
                      (job_id, job_name, job_status, run_time, nodes, cpus, log_err_size, log_out_size, timestamp)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (job_id, job_name, job_status, run_time, nodes, cpus, log_err_size, log_out_size, timestamp))
    conn.commit()
    conn.close()
