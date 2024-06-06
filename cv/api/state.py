import time
from types import SimpleNamespace
import traceback

SYSTEM_STATES = SimpleNamespace(
    INSPECTION_START_PRE = "INSPECTION_START_PRE", # Check PLC healthy
    INSPECTION_HALT = "INSPECTION_HALT", # PLC unhealthy
    INSPECTION_START = "INSPECTION_START", # Part data recd
    INSPECTION_RUNNING = "INSPECTION_RUNNING", # Evaluation
    INSPECTION_END = "INSPECTION_END", # Save results and reset cycle
)

PLC_STATES = SimpleNamespace(
    EMERGENCY = "EMERGENCY",
    HEALTHY = "HEALTHY",
    UNHEALTHY = "UNHEALTHY"
)

def get_state_name(state):
    return {
        SYSTEM_STATES.INSPECTION_START_PRE: "Initializing",
        SYSTEM_STATES.INSPECTION_HALT: "Halted",
        SYSTEM_STATES.INSPECTION_START: "Awaiting Data",
        SYSTEM_STATES.INSPECTION_RUNNING: "Running",
        SYSTEM_STATES.INSPECTION_END: "Saving Results",
    }[state]

def get_plc_state_name(state):
    return {
        PLC_STATES.EMERGENCY: "Emergency",
        PLC_STATES.HEALTHY: "Healthy",
        PLC_STATES.UNHEALTHY: "Unreachable",
    }[state]

class State:

    def __init__(self):
        self.state = None
        self.plc_state = PLC_STATES.UNHEALTHY
        self._actions = []
        self._state_history = []

    def update_state(self, new_state, force=False):
        if not force and self.state == new_state:
            return
        old_state = self.state
        self.state = new_state
        self._state_history.append([old_state, new_state])

    def register_action(self, action_fn, from_states=None, to_states=None):
        self._actions.append((action_fn, from_states, to_states))

    def run_actions(self, data):
        if len(self._state_history) == 0:
            return
        old_state, new_state = self._state_history[0]
        for (action_fn, from_states, to_states) in self._actions:
            from_check = from_states is None or old_state in from_states
            to_check = to_states is None or new_state in to_states
            if from_check and to_check:
                # print("Running action:", action_fn.__name__)
                try:
                    action_fn(data)
                    self._state_history.pop(0)
                except Exception as ex:
                    print("Error running action:", ex)
                    traceback.print_exc()
                    time.sleep(1)
                break
        else:
            print("No handlers found for action:", old_state, new_state)
            self._state_history.pop(0)
