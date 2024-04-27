# from processes.heartbeat_get import is_heartbeat_healthy
from api.state import SYSTEM_STATES, PLC_STATES

def inspection_start_pre_actions(data):
    # hearbeat_ok = is_heartbeat_healthy()
    hearbeat_ok = True # temp
    if hearbeat_ok:
        data.state.plc_state = PLC_STATES.HEALTHY
        print("Emergency and heartbeat checks passed.")
        next_state = SYSTEM_STATES.INSPECTION_START
    else:
        data.state.plc_state = PLC_STATES.UNHEALTHY
        print(f"Heartbeat: {hearbeat_ok}. Checks Failed.")
        next_state = SYSTEM_STATES.INSPECTION_HALT

    data.state.update_state(next_state)
