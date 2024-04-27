from .state import State
from .artifact import Artifact
from utils.db import get_entity_lookup

class Data:

    def __init__(self):
        self.entity_lookup = get_entity_lookup()
        self.state = State()
        self.artifact = None