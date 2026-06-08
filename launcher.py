import subprocess
import socket
import os
import signal
import time

from Engine.logging_engine import (
    log_info
)

# -----------------------------
# CONFIG
# -----------------------------

from Engine.config import STREAMLIT_PORT

APP_FILE = "app_v2.py"

# -----------------------------
# CHECK PORT
# -----------------------------

def is_port_in_use(port):

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as sock:

        return (
            sock.connect_ex(
                ("localhost", port)
            ) == 0
        )

# -----------------------------
# FIND PROCESS USING PORT
# -----------------------------

def find_port_processes(port):

    result = subprocess.run(

        ["lsof", "-t", f"-i:{port}"],

        capture_output=True,

        text=True
    )

    pid_list = result.stdout.strip().splitlines()

    return [

        int(pid)

        for pid in pid_list

        if pid.strip()
    ]

# -----------------------------
# KILL EXISTING PROCESS
# -----------------------------

def kill_existing_processes(port):

    pids = find_port_processes(port)

    for pid in pids:

        log_info(
            f"Stopping existing process: {pid}"
        )

        os.kill(pid, signal.SIGKILL)

    time.sleep(2)

# -----------------------------
# START STREAMLIT
# -----------------------------

def launch_streamlit():

    log_info(
        f"Starting Streamlit on port {STREAMLIT_PORT}"
    )

    subprocess.run(

        [
            "streamlit",
            "run",
            APP_FILE,
            "--server.port",
            str(STREAMLIT_PORT)
        ]
    )

# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    if is_port_in_use(STREAMLIT_PORT):

        kill_existing_processes(
            STREAMLIT_PORT
        )

    launch_streamlit()