import time

from config.models import ModelConfig

part_success_threshold = 2
snapshot_interval_secs = 5

class Artifact:

    def __init__(self, psn, chassis, vehicle_model):
        self.psn = psn
        self.chassis = chassis
        self.vehicle_model = vehicle_model
        self.part_list = [p for p in [
            *ModelConfig.top_cam.class_names,
            *ModelConfig.bottom_cam.class_names,
        ] if p is not None]
        self.part_counts = {p: 0 for p in self.part_list}
        self.part_ok_count = 0

        # Snapshots
        self.top_snapsots = []
        self.bottom_snapsots = []
        self._last_snapshot_time = time.time()

    def update(self, results, frame_top, frame_bottom):        
        for result in results:
            if result['name'] not in self.part_counts:
                continue
            self.part_counts[result['name']] += 1
            if self.part_counts[result['name']] == part_success_threshold:
                self.part_ok_count += 1


    def save(self):
        print("Saving data. TODO")
        pass