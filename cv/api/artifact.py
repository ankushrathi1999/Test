import os
import time
from datetime import datetime
import pymysql
import cv2
import json
import traceback
import json
import yaml

from config.db_config import db_params
from config.config import config
from utils.db import insert_datafilter, insert_integer_metric, insert_string_metric
from utils.shift_utils import get_current_shift
from .bezel_group import BezelGroup
from .usb_aux_group import UsbAuxGroup
from .classification_part import ClassificationPart
from .steering_cover import SteeringCover
from .detection_part import DetectionPart
from .detection import DetectionResult
from config.models import BezelGroupDetectionModel, PartDetectionModel
from config.models import (
    PartClassificationModel, ACControlClassificationModel, SensorClassificationModel, LightsClassificationModel,
    WiperClassificationModel, LowerPanelClassificationModel, OrnClassificationModel
)

api_config = config['api_artifact']
part_success_threshold = api_config.getint('part_success_threshold')
snapshot_interval_secs = api_config.getfloat('snapshot_interval_secs')
n_snapshots_max = api_config.getint('n_snapshots_max')
snapshots_dir = api_config.get('snapshots_dir')
metadata_dir = api_config.get('metadata_dir')
metadata_dir_debug = os.path.join(metadata_dir, 'debug')
debug_mode = api_config.getboolean('debug_mode')
plc_write_enabled = api_config.getboolean('plc_write_enabled')

# Create data directories
os.makedirs(snapshots_dir, exist_ok=True)
os.makedirs(metadata_dir, exist_ok=True)
debug_mode and os.makedirs(metadata_dir_debug, exist_ok=True)

with open('./config/vehicle_parts.yaml') as x:
    vehicle_parts_lookup = yaml.safe_load(x)

with open('./config/part_order_plc.csv') as f:
    part_order_plc = [x.strip() for x in f]

class Artifact:

    def __init__(self, psn, chassis, vehicle_model, data):
        self.data = data
        self.inspection_flag = int(f'vehicle_model_{vehicle_model}' in self.data.entity_lookup)
        self.shift = get_current_shift()

        self.psn = psn
        self.chassis = chassis
        self.vehicle_model = vehicle_model
        self.vehicle_category = vehicle_model[:3] if (vehicle_model and len(vehicle_model) >= 3) else None
        self.vehicle_type = vehicle_parts_lookup.get(vehicle_model, {}).get('vehicle_type', 'RHD')

        # Parts
        self.bezel_group = BezelGroup(vehicle_model)
        self.usb_aux_group = UsbAuxGroup(vehicle_model)
        classification_targets = {
             *PartClassificationModel.target_detections,
             *ACControlClassificationModel.target_detections,
             *SensorClassificationModel.target_detections,
             *LightsClassificationModel.target_detections,
             *WiperClassificationModel.target_detections,
             *LowerPanelClassificationModel.target_detections,
             *OrnClassificationModel.target_detections
        }

        self.parts = {}
        for detection_class in PartDetectionModel.ordered_class_list:
            if detection_class is None:
                continue
            detection_class = PartDetectionModel.get_processed_class(detection_class, self.vehicle_category, self.vehicle_type)
            if detection_class not in classification_targets:
                self.parts[detection_class] = DetectionPart(vehicle_model, detection_class)
            elif detection_class == PartDetectionModel.CLASS_steering_cover:
                self.parts[detection_class] = SteeringCover(vehicle_model, detection_class, self)
            else:
                self.parts[detection_class] = ClassificationPart(vehicle_model, detection_class, self)

        # self.parts = {
        #     detection_class:
        #     ClassificationPart(vehicle_model, detection_class, self) if detection_class in classification_targets
        #     else DetectionPart(vehicle_model, detection_class)
        #     for detection_class in
        #     [PartDetectionModel.get_processed_class(dc, self.vehicle_category, self.vehicle_type)
        #      for dc in PartDetectionModel.ordered_class_list if dc is not None]
        # }

        # Snapshots
        self._last_snapshot_time = time.time()
        self._n_snapshots_saved = 0

        # Results
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.end_time = None
        self.is_ended = False
        self.part_results = []
        self.overall_result = None

    def update(self, detection_groups, frame_top, frame_bottom, frame_up):
        if self.is_ended:
            return

        # Bezel update
        bezel_detections = detection_groups.get(BezelGroupDetectionModel.CLASS_CONTAINER, [])
        bezel_switch_detections = detection_groups.get(BezelGroupDetectionModel.CLASS_SWITCH, [])
        for cam_type in ('top', 'bottom'):
            bezel_detections_cur = [d for d in bezel_detections if d.cam_type == cam_type]
            bezel_switch_detections_cur = [d for d in bezel_switch_detections if d.cam_type == cam_type]
            self.bezel_group.update(bezel_detections_cur, bezel_switch_detections_cur)

        # USB Aux Update
        usb_aux_container_detections = detection_groups.get(PartDetectionModel.CLASS_usb_aux_container, [])
        usb_aux_detections = detection_groups.get(PartDetectionModel.CLASS_usb_aux, [])
        self.usb_aux_group.update(usb_aux_container_detections, usb_aux_detections) # Only bottom cam
        
        # Parts Update - classification and detection
        for detection_class, part in self.parts.items():
            if detection_class in detection_groups:
                part.update(detection_groups[detection_class], detection_groups)

        cur_time = time.time()
        if (cur_time - self._last_snapshot_time > snapshot_interval_secs) and (self._n_snapshots_saved < n_snapshots_max):
            print("Saving snapshots", self._n_snapshots_saved+1)
            date_folder_name = datetime.now().strftime('%Y%m%d')
            for img, img_type in zip([frame_top, frame_bottom, frame_up], ["top", "bottom", "up"]):
                snapshots_dir_cur = os.path.join(snapshots_dir, date_folder_name, self.vehicle_model, img_type)
                metadata_dir_cur = os.path.join(metadata_dir, date_folder_name, self.vehicle_model, img_type)
                os.makedirs(snapshots_dir_cur, exist_ok=True)
                os.makedirs(metadata_dir_cur, exist_ok=True)
                img_name = f"{self.chassis}_{self.vehicle_model}_{img_type}_{self._n_snapshots_saved+1}.jpg"
                img_path = os.path.join(snapshots_dir_cur, img_name)
                metadata_path = os.path.join(metadata_dir_cur, img_name.replace('.jpg', '.json'))
                height, width = img.shape[0], img.shape[1]
                img = cv2.resize(img, (1000, round(height * (1000 / width))))
                cv2.imwrite(img_path, img)
                detections = [d.to_dict() for dl in detection_groups.values() for d in dl if d.cam_type == img_type]
                with open(metadata_path, 'w') as f:
                    json.dump(detections, f)
            self._last_snapshot_time = time.time()
            self._n_snapshots_saved += 1

        if debug_mode:
            metadata_path_debug = os.path.join(metadata_dir_debug, f'debug_{self.psn}_{self.vehicle_model}_{time.time()}.json')
            detections = [d.to_dict() for dl in detection_groups.values() for d in dl]
            with open(metadata_path_debug, 'w') as f:
                json.dump(detections, f, indent=2)

    def end_inspection(self):
        if self.is_ended:
            return
        self.is_ended = True
        self.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.part_results, self.overall_result = self.get_part_results()

    def get_part_results(self):
        bezel_part_results = self.bezel_group.get_part_results()
        usb_aux_results = self.usb_aux_group.get_part_results()
        part_results = [p for p in [part.get_part_result() for part in self.parts.values()] if p is not None]
        all_part_results = [*bezel_part_results, *usb_aux_results, *part_results]
        overall_ok = (
            self.inspection_flag == 1 and
            len(all_part_results) > 0 and
            all([part['result'] == DetectionResult.OK for part in all_part_results])
        )
        return all_part_results, overall_ok
    
    def get_part_results_plc(self):
        OK_VAL = 48 + 1 # ascii 
        NG_VAL = 48 + 0
        NA_VAL = 48 + 9

        assert self.is_ended
        parts, overall_ok = self.part_results, self.overall_result

        plc_array_1 = [NA_VAL for i in range(23)] # Hardcoded for 23 parameters
        plc_array_2 = [NA_VAL for i in range(23)]
        if self.inspection_flag == 1 and plc_write_enabled:
            part_results_lookup = {p['part_name']: p['result'] for p in parts}
            results = []
            for part_name in part_order_plc:
                if part_name.startswith('BZ_'):
                    results.append(self.bezel_group.get_result_by_part_name(parts, part_name))
                elif part_name in part_results_lookup:
                    results.append(part_results_lookup[part_name])
                else:
                    print("RESULT UNAVAILABLE FOR", part_name, self.vehicle_model, self.psn)
                    results.append(None)
                print("PART RESULT:", part_name, results[-1])
            for i, part_result in enumerate(results):
                plc_array = plc_array_1
                if i >= 22: # Switch to Array 2
                    plc_array = plc_array_2
                    i = i - 22
                if i >= 9: # Skip position 10, reserved for overall result
                    i += 1
                if part_result is not None:
                    plc_array[i] = OK_VAL if (part_result == DetectionResult.OK) else NG_VAL
            plc_array_1[9] = NG_VAL if any([res == NG_VAL for i, res in enumerate(plc_array_1) if i != 9]) else OK_VAL
            plc_array_2[9] = NG_VAL if any([res == NG_VAL for i, res in enumerate(plc_array_2) if i != 9]) else OK_VAL
        print("PLC Array 1")
        print(plc_array_1)
        print("PLC Array 2")
        print(plc_array_2)
        return [plc_array_1, plc_array_2]

    def save(self):
        assert self.is_ended
        parts, overall_ok = self.part_results, self.overall_result
        result_ok_flag = int(overall_ok)

        data_filters = [
            (f'shift_{self.shift}', 1),
        ]

        string_metrics = [
            ('vehicle_metadata_psn', self.psn, 1),
            ('vehicle_metadata_chassis', self.chassis, 1),
        ]

        if self.inspection_flag == 1:
            data_filters.append((f'vehicle_model_{self.vehicle_model}', 1))
        else:
            string_metrics.append(['vehicle_metadata_vehicle_model', self.vehicle_model, 1])

        integer_metrics = []
        if self.inspection_flag == 1:
            for part in parts:
                # Add Part Result
                integer_metrics.append([
                    f'part_{part["part_id"]}',
                    part['result'],
                    1
                ])
            string_metrics.append([
                f'result_metadata_inspectionDetails',
                json.dumps(parts),
                2
            ])


        connection  = None
        try:
            connection = pymysql.connect(host=db_params['host'],
                                        user=db_params['user'],
                                        password=db_params['password'],
                                        database=db_params['database'])
            with connection.cursor() as cursor:
                insert_record_query = '''
                insert into Record
                (record_type_id, created_on)
                values
                (%s, %s)
                '''
                cursor.execute(insert_record_query, (1, self.start_time))
                record_id = cursor.lastrowid

                insert_integer_metric(cursor, record_id, self.data.entity_lookup['result_metadata_inspectionFlag'], self.inspection_flag, 1)
                insert_integer_metric(cursor, record_id, self.data.entity_lookup['result_metadata_inspectionImage'], self._n_snapshots_saved, 1)
                print("Inspection Flag", self.inspection_flag)
                if self.inspection_flag == 1:
                    insert_integer_metric(cursor, record_id, self.data.entity_lookup['result_metadata_resultOKFlag'], result_ok_flag, 1)
                    print("Result OK Flag", result_ok_flag)
                for entity_key, metric_id in data_filters:
                    if entity_key not in self.data.entity_lookup:
                        print("WARNING: Part not in Database:", entity_key)
                        continue
                    entity_id = self.data.entity_lookup[entity_key]
                    insert_datafilter(cursor, record_id, entity_id, metric_id)
                    print("Filter:", record_id, entity_id)
                for entity_key, value, metric_id in integer_metrics:
                    if entity_key not in self.data.entity_lookup:
                        print("WARNING: Part not in Database:", entity_key)
                        continue
                    entity_id = self.data.entity_lookup[entity_key]
                    insert_integer_metric(cursor, record_id, entity_id, value, metric_id)
                    print("Integer Metric:", record_id, entity_id, value)
                for entity_key, value, metric_id in string_metrics:
                    if entity_key not in self.data.entity_lookup:
                        print("WARNING: Part not in Database:", entity_key)
                        continue
                    entity_id = self.data.entity_lookup[entity_key]
                    insert_string_metric(cursor, record_id, entity_id, value, metric_id)
                    print("String Metric:", record_id, entity_id, value)
                connection.commit()
        except Exception as ex:
            print("Failed to save artifact.", ex)
            traceback.print_exc()
        finally:
            if connection is not None:
                connection.close()