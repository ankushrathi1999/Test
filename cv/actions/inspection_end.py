from api.state import SYSTEM_STATES

def inspection_end_actions(data):
    # Save engine
    data.artifact.save()

    # Reset Cycle
    data.artifact = None
    next_state = SYSTEM_STATES.INSPECTION_START_PRE
    data.state.update_state(next_state)
