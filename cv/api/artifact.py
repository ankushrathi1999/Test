from config.models import ModelConfig

part_success_threshold = 2

class Artifact:

    def __init__(self):
        self.psn = "8407-00"
        self.chassis = "MA3BNC62SRC775663"
        self.vehicle_model = "YHB4ED23P7400000"
        self.part_list = [p for p in [
            *ModelConfig.top_cam.class_names,
            *ModelConfig.bottom_cam.class_names,
        ] if p is not None]
        self.part_counts = {p: 0 for p in self.part_list}
        self.part_ok_count = 0

        # Snapshot
        self.max_results_top = -1
        self.max_results_bottom = -1
        self.top_snapsot = None
        self.bottom_snapsot = None

    def update(self, results, frame_top, frame_bottom):
        result_top_count = 0
        result_bottom_count = 0
        
        for result in results:
            if result['name'] not in self.part_counts:
                continue
            if result['result_type'] == "top":
                result_top_count += 1
            elif result['result_type'] == "bottom":
                result_bottom_count += 1
            self.part_counts[result['name']] += 1
            if self.part_counts[result['name']] == part_success_threshold:
                self.part_ok_count += 1

        if result_top_count > self.max_results_top:
            self.max_results_top = result_top_count
            self.top_snapsot = frame_top
        if result_bottom_count > self.max_results_bottom:
            self.max_results_bottom = result_bottom_count
            self.bottom_snapsot_snapsot = frame_bottom
