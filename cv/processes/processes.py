from .state_actions import StateActions
from .inference import InferenceLoop
from .plc_io import PLCIO
from .video_buffer_handler import VideoBufferHandler
# from .heartbeat_get import HeartbeatGet
# from .heartbeat_send import HeartbeatSend

def get_processes(data):
    return [
        StateActions(data),
        InferenceLoop(data),
        PLCIO(),
        VideoBufferHandler(),
        # HeartbeatSend(),
        # HeartbeatGet(),
    ]
