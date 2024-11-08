from .state_actions import StateActions
from .inference import InferenceLoop
from .plc_io import PLCIO
from .video_manager import VideoManager
from .heartbeat_get import HeartbeatGet
from .heartbeat_send import HeartbeatSend
from .health_server import HealthServer
from .rebuild_vehicle_master import RebuildVehicleMaster
from utils.artifact_utils import get_artifact_videos

def get_processes(data):

    videos = get_artifact_videos()
    video_managers = [VideoManager(data, video_config) for video_config in videos]

    return [
        StateActions(data),
        InferenceLoop(data),
        PLCIO(),
        *video_managers,
        HeartbeatSend(),
        HeartbeatGet(),
        HealthServer(data),
        RebuildVehicleMaster(),
    ]
