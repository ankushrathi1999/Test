import subprocess
import logging
import logging.handlers
import sys
import os

# Check if the command line arguments are provided
if len(sys.argv) < 2:
    print("Usage: python log_wrapper.py [command_to_run]")
    sys.exit(1)

# Command to run is taken from the command line arguments
command = sys.argv[1:]

# Configure logging
log_folder = 'logs'
log_file = os.path.join(log_folder, 'application.log')
log_backup_count = 90  # Keep N days of logs

# Create the log folder if it does not exist
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

logger = logging.getLogger('ApplicationLogger')
logger.setLevel(logging.INFO)

# File handler with timestamp in the format
file_handler = logging.handlers.TimedRotatingFileHandler(log_file, when='midnight', backupCount=log_backup_count)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console handler with only the message
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

RUN_IN_LOOP = False

while True:
    # Run the command and capture its output
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
        for line in proc.stdout:
            logger.info(line.strip())

    # Check for any error if the program exits
    if proc.returncode and proc.returncode != 0:
        logger.error(f"The command exited with error code {proc.returncode}")

    # Check for any error if the program exits
    if proc.returncode and proc.returncode == 42:
        logger.info("Ending execution loop")
        break

    if not RUN_IN_LOOP:
        break
