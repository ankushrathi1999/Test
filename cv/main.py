import time

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
    register_actions(data.state)
    
    # Start processes
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
        for process in processes:
            process.stop()

    # Wait of processes to end
    for process in processes:
        process.wait()

    print("Exiting.")


if __name__ == '__main__':
    run()
