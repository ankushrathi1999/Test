import logging

from .state import State
from .artifact import Artifact
from utils.db import get_entity_lookup
from config.config import config
from utils.artifact_utils import artifacts_config, get_artifact_videos

logger = logging.getLogger(__name__)

api_config = config['api_artifact']
debug_mode = api_config.getboolean('debug_mode')
debug_vehicle_model = api_config.get('debug_vehicle_model')

class Data:

    def __init__(self):
        self.is_active = True # inspection active
        self.state = State()
        if debug_mode:
            logger.info("Runnig in DEBUG mode.")
            self.entity_lookup = {}
            self.artifacts = [
                Artifact(artifact, 1260, 'MA3BNC22S00795581', debug_vehicle_model, 'CLR', self)
                for artifact in artifacts_config['artifacts']
            ]
        else:
            logger.info("Loading entities")
            self.entity_lookup = {
                artifact['code']: get_entity_lookup(artifact['database'])
                for artifact in artifacts_config['artifacts']
            }
            for artifact in artifacts_config['artifacts']:
                logger.info("Loaded entities: %s", len(self.entity_lookup[artifact['code']]))
                logger.debug("Entity Lookup: %s", self.entity_lookup[artifact['code']])
            self.artifacts = []
        self.frames = {}
        self.video_config = get_artifact_videos()
        self.vehicle_psn_lookup = {}
