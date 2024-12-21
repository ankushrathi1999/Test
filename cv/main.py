import time
import yaml
import logging
import logging.config

### 1/4 Configure Logging

with open('logging.yaml', 'r') as f:
    logging.config.dictConfig(yaml.safe_load(f.read()))
logger = logging.getLogger(__name__)


### 2/4 Prevent duplicate executions

from config.config import config
from utils.generic_utils import is_port_in_use

process_config = config['process_health_server']
health_port = process_config.getint('port')
logger.info("Checking port availability: %s", health_port)
if is_port_in_use(health_port):
    message = f'Application port {health_port} is already in use.'
    logger.critical(message)
    raise Exception(message)


### 3/4 Build vehicle master

from utils.build_vehicle_master import build_all_vehicle_master
from config.config import load_vehicle_parts_lookup

logger.info("Building vehcile master")
try:
    build_all_vehicle_master()
    load_vehicle_parts_lookup()
except Exception as ex:
    logger.exception("Failed to build latest vehicle master from database.")


### 4/4 Start Application

from api.data import Data
from api.state import SYSTEM_STATES
from actions.actions import register_actions
from processes.processes import get_processes

def run():
    logger.info("Initializing.")
    # Data
    data = Data()
    data.state.update_state(SYSTEM_STATES.INSPECTION_START)
    
    # Register state actions
    logger.info("Registering state actions")
    register_actions(data.state)
    
    # Start processes
    logger.info("Starting processes")
    processes = get_processes(data)
    for process in processes:
        process.start()

    try:
        is_terminated = False
        while not is_terminated:
            for process in processes:
                if process.is_terminated:
                    is_terminated = True
                    break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.error("Keyboard interrupt")
    finally:
        logger.info("Stopping rocesses")
        for process in processes:
            process.stop()

    # Wait of processes to end
    logger.info("Waiting for processes to stop")
    for process in processes:
        process.wait()

    logger.info("Exiting.")


if __name__ == '__main__':
    run()
