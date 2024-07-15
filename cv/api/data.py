import logging

from .state import State
from .artifact import Artifact
from utils.db import get_entity_lookup
from config.config import config

logger = logging.getLogger(__name__)

api_config = config['api_artifact']
debug_mode = api_config.getboolean('debug_mode')
debug_vehicle_model = api_config.get('debug_vehicle_model')

class Data:

    def __init__(self):
        self.is_active = False # inspection active
        self.state = State()
        if debug_mode:
            logger.info("Runnig in DEBUG mode.")
            self.entity_lookup = {}
            self.artifact = Artifact(1260, 'MA3BNC22S00795581', debug_vehicle_model, self)
        else:
            logger.info("Loading entities")
            self.entity_lookup = get_entity_lookup()
            logger.info("Loaded entities: %s", len(self.entity_lookup))
            logger.debug("Entity Lookup: %s", self.entity_lookup)
            self.artifact = None
        self.frames = {}
        self.video_paths = []