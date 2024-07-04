import time
import traceback

from utils.build_vehicle_master import build_vehicle_master

# Build vehicle master
try:
    build_vehicle_master()
except Exception as ex:
    print("Failed to build latest vehicle master from database.", ex)
    traceback.print_exc()

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
