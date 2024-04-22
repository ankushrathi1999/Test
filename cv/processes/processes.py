from .state_actions import StateActions
from .inference import InferenceLoop

def get_processes(data):
    return [
        StateActions(data),
        InferenceLoop(data),
    ]
