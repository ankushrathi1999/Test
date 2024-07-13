import time
import traceback


### 1/3 Prevent duplicate executions

from config.config import config
from utils.generic_utils import is_port_in_use

process_config = config['process_health_server']
health_port = process_config.getint('port')
print("Checking port availability:", health_port)
if is_port_in_use(health_port):
    raise Exception(f'Application port {health_port} is already in use.')


### 2/3 Build vehicle master

from utils.build_vehicle_master import build_vehicle_master

print("Building vehcile master")
try:
    build_vehicle_master()
except Exception as ex:
    print("Failed to build latest vehicle master from database.", ex)
    traceback.print_exc()


### 3/3 Start Application

from api.data import Data
from api.state import SYSTEM_STATES
from actions.actions import register_actions
from processes.processes import get_processes

def run():
    print("Initializing.")
    # Data
    data = Data()
    data.state.update_state(SYSTEM_STATES.INSPECTION_START)
    
    # Register state actions
    print("Registering state actions")
    register_actions(data.state)
    
    # Start processes
    print("Starting processes")
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
        print("Keyboard Interrupt")
    finally:
        print("Stopping porcesses")
        for process in processes:
            process.stop()

    # Wait of processes to end
    print("Waiting for processes to stop")
    for process in processes:
        process.wait()

    print("Exiting.")


if __name__ == '__main__':
    run()
