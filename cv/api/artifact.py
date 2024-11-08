import os
import time
from datetime import datetime
import pymysql
import cv2
import json
import logging
import json

from config.db_config import db_params
from config.config import config, get_vehicle_parts_lookup, part_order_plc
from utils.db import insert_datafilter, insert_integer_metric, insert_string_metric
from utils.shift_utils import get_current_shift
from .classification_part import ClassificationPart
from .detection_part import DetectionPart
from .detection import DetectionResult
from config.models import PartDetectionOutModel, PartDetectionInTopModel, PartDetectionInBottomModel

logger = logging.getLogger(__name__)

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

class Artifact:

    def __init__(self, artifact_config, psn, chassis, vehicle_model, data):
        vehicle_parts_lookup = get_vehicle_parts_lookup()
        print("D1:", len(vehicle_parts_lookup), vehicle_model, vehicle_model in vehicle_parts_lookup)
        
        # Artifact code, database, etc..
        self.artifact_config = artifact_config

        self.data = data
        self.inspection_flag = int(f'vehicle_model_{vehicle_model}' in data.entity_lookup[artifact_config['code']])
        self.shift = get_current_shift()

        self.psn = psn
        self.chassis = chassis
        self.vehicle_model = vehicle_model
        self.vehicle_category = vehicle_model[:3] if (vehicle_model and len(vehicle_model) >= 3) else None
        self.vehicle_type = vehicle_parts_lookup.get(vehicle_model, {}).get('vehicle_type', 'RHD')

        # Parts
        classification_targets = {}

        self.parts = {}
        for detection_class in [
            *PartDetectionInBottomModel.ordered_class_list,
            *PartDetectionInTopModel.ordered_class_list,
            *PartDetectionOutModel.ordered_class_list,
        ]:
            if detection_class is None:
                continue
            if detection_class not in classification_targets:
                self.parts[detection_class] = DetectionPart(vehicle_model, detection_class)
            else:
                self.parts[detection_class] = ClassificationPart(vehicle_model, detection_class, self)

        # Snapshots
        self._last_snapshot_time = time.time()
        self._n_snapshots_saved = 0

        # Results
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.end_time = None
        self.is_ended = False
        self.part_results = []
        self.overall_result = None

        logger.info("Artifact created: %s", {
            'code': self.artifact_config['code'],
            'start_time': self.start_time,
            'inspection_flag': self.inspection_flag,
            'shift': self.shift,
            'psn': self.psn,
            'chassis': self.chassis,
            'vehicle_model': self.vehicle_model,
            'vehicle_category': self.vehicle_category,
            'vehicle_type': self.vehicle_type,
        })

    def update(self, detection_groups, frames):
        if self.is_ended:
            return

        # Parts Update - classification and detection
        logger.debug("Updating parts")
        for detection_class, part in self.parts.items():
            if detection_class in detection_groups:
                part.update(detection_groups[detection_class], detection_groups)

        cur_time = time.time()
        if (cur_time - self._last_snapshot_time > snapshot_interval_secs) and (self._n_snapshots_saved < n_snapshots_max):
            logger.info("Saving snapshots: %s/%s", self._n_snapshots_saved+1, n_snapshots_max)
            date_folder_name = datetime.now().strftime('%Y%m%d')
            for img_type, img in frames.items():
                snapshots_dir_cur = os.path.join(snapshots_dir, date_folder_name, self.vehicle_model, img_type)
                metadata_dir_cur = os.path.join(metadata_dir, date_folder_name, self.vehicle_model, img_type)
                os.makedirs(snapshots_dir_cur, exist_ok=True)
                os.makedirs(metadata_dir_cur, exist_ok=True)
                img_name = f"{self.chassis}_{self.vehicle_model}_{img_type}_{self._n_snapshots_saved+1}.jpg"
                img_path = os.path.join(snapshots_dir_cur, img_name)
                metadata_path = os.path.join(metadata_dir_cur, img_name.replace('.jpg', '.json'))
                height, width = img.shape[0], img.shape[1]
                img = cv2.resize(img, (1000, round(height * (1000 / width))))
                if cv2.imwrite(img_path, img):
                    logger.info("Snapshot saved to: %s", img_path)
                else:
                    logger.error("Failed to save snapshot to: %s", img_path)
                detections = [d.to_dict() for dl in detection_groups.values() for d in dl if d.cam_type == img_type]
                with open(metadata_path, 'w') as f:
                    json.dump(detections, f)
                logger.info("Metadata saved to: %s", metadata_path)
            self._last_snapshot_time = time.time()
            self._n_snapshots_saved += 1

        if debug_mode:
            metadata_path_debug = os.path.join(metadata_dir_debug, f'debug_{self.psn}_{self.vehicle_model}_{time.time()}.json')
            detections = [d.to_dict() for dl in detection_groups.values() for d in dl]
            with open(metadata_path_debug, 'w') as f:
                json.dump(detections, f, indent=2)

    def end_inspection(self):
        if self.is_ended:
            logger.wanr('Inspection is already ended.')
            return
        self.is_ended = True
        self.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.part_results, self.overall_result = self.get_part_results()
        logger.info("Inspection ended. end_time=%s overall_result=%s", self.end_time, self.overall_result)
        logger.info("Part results:")
        for result in self.part_results:
            logger.info(result)

    def get_part_results(self):
        part_results = [p for p in [part.get_part_result() for part in self.parts.values()] if p is not None]
        all_part_results = [*part_results]
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
        logger.info("PLC Write flags: inspection_flag=%s plc_write_enabled=%s",self.inspection_flag ,plc_write_enabled)
        # if self.inspection_flag == 1 and plc_write_enabled:
        #     part_results_lookup = {p['part_name']: p['result'] for p in parts}
        #     results = []
        #     for part_name in part_order_plc:
        #         if part_name.startswith('BZ_'):
        #             results.append(self.bezel_group.get_result_by_part_name(parts, part_name))
        #         elif part_name in part_results_lookup:
        #             results.append(part_results_lookup[part_name])
        #         else:
        #             logger.warn("RESULT UNAVAILABLE FOR: %s", (part_name, self.vehicle_model, self.psn))
        #             results.append(None)
        #         logger.info("PART RESULT: %s=%s", part_name, results[-1])
        #     for i, part_result in enumerate(results):
        #         plc_array = plc_array_1
        #         if i >= 22: # Switch to Array 2
        #             plc_array = plc_array_2
        #             i = i - 22
        #         if i >= 9: # Skip position 10, reserved for overall result
        #             i += 1
        #         if part_result is not None:
        #             plc_array[i] = OK_VAL if (part_result == DetectionResult.OK) else NG_VAL
        #     plc_array_1[9] = NG_VAL if any([res == NG_VAL for i, res in enumerate(plc_array_1) if i != 9]) else OK_VAL
        #     plc_array_2[9] = NG_VAL if any([res == NG_VAL for i, res in enumerate(plc_array_2) if i != 9]) else OK_VAL
        return [plc_array_1, plc_array_2]

    def save(self):
        assert self.is_ended

        entity_lookup = self.data.entity_lookup[self.artifact_config['code']]

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
                                        database=self.artifact_config['database'])
            with connection.cursor() as cursor:
                insert_record_query = '''
                insert into Record
                (record_type_id, created_on)
                values
                (%s, %s)
                '''
                cursor.execute(insert_record_query, (1, self.start_time))
                record_id = cursor.lastrowid

                insert_integer_metric(cursor, record_id, entity_lookup['result_metadata_inspectionFlag'], self.inspection_flag, 1)
                insert_integer_metric(cursor, record_id, entity_lookup['result_metadata_inspectionImage'], self._n_snapshots_saved, 1)
                logger.info("Inspection Flag = %s", self.inspection_flag)
                logger.info("Inspection Image = %s", self._n_snapshots_saved)
                if self.inspection_flag == 1:
                    insert_integer_metric(cursor, record_id, entity_lookup['result_metadata_resultOKFlag'], result_ok_flag, 1)
                    logger.info("Result OK Flag = %s", result_ok_flag)
                for entity_key, metric_id in data_filters:
                    if entity_key not in entity_lookup:
                        logger.warn("Part not in Database: %s", entity_key)
                        continue
                    entity_id = entity_lookup[entity_key]
                    insert_datafilter(cursor, record_id, entity_id, metric_id)
                    logger.info("Filter: record_id=%s entity_id=%s", record_id, entity_id)
                for entity_key, value, metric_id in integer_metrics:
                    if entity_key not in entity_lookup:
                        logger.warn("Part not in Database: %s", entity_key)
                        continue
                    entity_id = entity_lookup[entity_key]
                    insert_integer_metric(cursor, record_id, entity_id, value, metric_id)
                    logger.info("Integer Metric: record_id=%s entity_id=%s value=%s", record_id, entity_id, value)
                for entity_key, value, metric_id in string_metrics:
                    if entity_key not in entity_lookup:
                        logger.warn("Part not in Database: %s", entity_key)
                        continue
                    entity_id = entity_lookup[entity_key]
                    insert_string_metric(cursor, record_id, entity_id, value, metric_id)
                    logger.info("String Metric: record_id=%s entity_id=%s value=%s", record_id, entity_id, value)
                connection.commit()
        except Exception as ex:
            logger.exception("Failed to save artifact")
        finally:
            if connection is not None:
                connection.close()