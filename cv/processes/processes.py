from .state_actions import StateActions
from .inference import InferenceLoop
from .heartbeat_get import HeartbeatGet
from .heartbeat_send import HeartbeatSend

def get_processes(data):
    return [
        StateActions(data),
        InferenceLoop(data),
        HeartbeatSend(),
        HeartbeatGet(),
    ]
