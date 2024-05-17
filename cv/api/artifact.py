import os
import time
from datetime import datetime
import pymysql
import cv2
import json

from config.db_config import db_params
from config.config import config
from utils.db import insert_datafilter, insert_integer_metric, insert_string_metric
from utils.shift_utils import get_current_shift
from .bezel_group import BezelGroup
from .detection import DetectionResult
from config.models.bezel_group_detection import BezelGroupDetectionModel

api_config = config['api_artifact']
part_success_threshold = api_config.getint('part_success_threshold')
snapshot_interval_secs = api_config.getfloat('snapshot_interval_secs')
snapshots_dir = api_config.get('snapshots_dir')
metadata_dir = api_config.get('metadata_dir')
metadata_dir_debug = os.path.join(metadata_dir, 'debug')
debug_mode = api_config.getboolean('debug_mode')

# Create data directories
os.makedirs(snapshots_dir, exist_ok=True)
os.makedirs(metadata_dir, exist_ok=True)
debug_mode and os.makedirs(metadata_dir_debug, exist_ok=True)

class Artifact:

    def __init__(self, psn, chassis, vehicle_model, data):
        self.data = data
        self.inspection_flag = int(f'vehicle_model_{vehicle_model}' in self.data.entity_lookup)
        self.shift = get_current_shift()

        self.psn = psn
        self.chassis = chassis
        self.vehicle_model = vehicle_model

        # Parts
        self.bezel_group = BezelGroup(vehicle_model)
        self.inspection_enabled = self.bezel_group.inspection_enabled

        # Snapshots
        self._last_snapshot_time = time.time()
        self._n_snapshots_saved = 0

        # Time
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update(self, detection_groups, frame_top, frame_bottom, frame_up):
        bezel_detections = detection_groups.get(BezelGroupDetectionModel.CLASS_CONTAINER, [])
        bezel_switch_detections = detection_groups.get(BezelGroupDetectionModel.CLASS_SWITCH, [])
        for cam_type in ('top', 'bottom'):
            bezel_detections_cur = [d for d in bezel_detections if d.cam_type == cam_type]
            bezel_switch_detections_cur = [d for d in bezel_switch_detections if d.cam_type == cam_type]
            self.bezel_group.update(bezel_detections_cur, bezel_switch_detections_cur)

        cur_time = time.time()
        if (cur_time - self._last_snapshot_time > snapshot_interval_secs) and (self._n_snapshots_saved < 8):
            print("Saving snapshots", self._n_snapshots_saved+1)
            for img, img_type in zip([frame_top, frame_bottom, frame_up], ["top", "bottom", "up"]):
                # img_name = f"{self.start_time.replace('-', '').replace(' ', '_')}_{self.psn}_{self.chassis}_{self.vehicle_model}_{img_type}_{self._n_snapshots_saved+1}.jpg"
                img_name = f"{self.chassis}_{self.vehicle_model}_{img_type}_{self._n_snapshots_saved+1}.jpg"
                img_path = os.path.join(snapshots_dir, img_name)
                metadata_path = os.path.join(metadata_dir, img_name.replace('.jpg', '.json'))
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

    def get_part_results(self):
        parts = []
        if self.bezel_group.inspection_enabled:
            parts.append({
                'part_id': self.bezel_group.bezel_part_id,
                'part_name': self.bezel_group.bezel_part_name,
                'result': self.bezel_group.bezel_result,
            })
            for part_id, part_name, result in zip(self.bezel_group.switch_part_ids, self.bezel_group.switch_part_names, self.bezel_group.switch_results):
                parts.append({
                    'part_id': part_id,
                    'part_name': part_name,
                    'result': result,
                })
        overall_ok = self.inspection_enabled and all([part['result'] == DetectionResult.OK for part in parts])
        return parts, overall_ok

    def save(self):
        parts, overall_ok = self.get_part_results()
        result_ok_flag = int(overall_ok)

        data_filters = [
            f'shift_{self.shift}',
        ]

        string_metrics = [
            ('vehicle_metadata_psn', self.psn),
            ('vehicle_metadata_chassis', self.chassis),
        ]

        if self.inspection_flag == 1:
            data_filters.append(f'vehicle_model_{self.vehicle_model}')
        else:
            string_metrics.append(['vehicle_metadata_vehicle_model', self.vehicle_model])

        integer_metrics = []
        if self.inspection_flag == 1:
            for part in parts:
                integer_metrics.append([
                    f'part_{part["part_id"]}',
                    part['result']
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

                insert_integer_metric(cursor, record_id, self.data.entity_lookup['result_metadata_inspectionFlag'], self.inspection_flag)
                print("Inspection Flag", self.inspection_flag)
                if self.inspection_flag == 1:
                    insert_integer_metric(cursor, record_id, self.data.entity_lookup['result_metadata_resultOKFlag'], result_ok_flag)
                    print("Result OK Flag", result_ok_flag)
                for entity_key in data_filters:
                    entity_id = self.data.entity_lookup[entity_key]
                    insert_datafilter(cursor, record_id, entity_id)
                    print("Filter:", record_id, entity_id)
                for entity_key, value in integer_metrics:
                    entity_id = self.data.entity_lookup[entity_key]
                    insert_integer_metric(cursor, record_id, entity_id, value)
                    print("Integer Metric:", record_id, entity_id, value)
                for entity_key, value in string_metrics:
                    entity_id = self.data.entity_lookup[entity_key]
                    insert_string_metric(cursor, record_id, entity_id, value)
                    print("String Metric:", record_id, entity_id, value)
                connection.commit()
        except Exception as ex:
            print("Failed to save artifact.", ex)
        finally:
            if connection is not None:
                connection.close()