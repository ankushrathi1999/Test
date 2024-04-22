from .state import State
from .artifact import Artifact

class Data:

    def __init__(self):
        self.state = State()
        self.artifact = Artifact()