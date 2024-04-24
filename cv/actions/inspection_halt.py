import time

from api.state import SYSTEM_STATES

def inspection_halt_actions(data):
    time.sleep(5)
    next_state = SYSTEM_STATES.INSPECTION_START_PRE
    data.state.update_state(next_state)