from api.state import SYSTEM_STATES
from .inspection_start_pre import inspection_start_pre_actions
from .inspection_halt import inspection_halt_actions
from .inspection_start import inspection_start_actions
from .inspection_running import inspection_running_actions
from .inspection_end import inspection_end_actions

def register_actions(state):
    state.register_action(inspection_start_pre_actions, to_states={SYSTEM_STATES.INSPECTION_START_PRE})
    state.register_action(inspection_halt_actions, to_states={SYSTEM_STATES.INSPECTION_HALT})
    state.register_action(inspection_start_actions, to_states={SYSTEM_STATES.INSPECTION_START})
    state.register_action(inspection_running_actions, to_states={SYSTEM_STATES.INSPECTION_RUNNING})
    state.register_action(inspection_end_actions, to_states={SYSTEM_STATES.INSPECTION_END})