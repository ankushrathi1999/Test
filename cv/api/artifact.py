import os
import time
from datetime import datetime
import pymysql
import cv2

from config.db_config import db_params
from config.models import ModelConfig
from config.config import config
from utils.db import insert_datafilter, insert_integer_metric, insert_string_metric
from utils.shift_utils import get_current_shift

api_config = config['api_artifact']
part_success_threshold = api_config.getint('part_success_threshold')
snapshot_interval_secs = api_config.getfloat('snapshot_interval_secs')
snapshots_dir = api_config.get('snapshots_dir')

class Artifact:

    def __init__(self, psn, chassis, vehicle_model, data):
        self.data = data
        self.inspection_flag = int(f'vehicle_model_{vehicle_model}' in self.data.entity_lookup)
        self.shift = get_current_shift()

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
        self._last_snapshot_time = time.time()
        self._n_snapshots_saved = 0

        # Time
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update(self, results, frame_top, frame_bottom, frame_up): 
        for result in results:
            if result['name'] not in self.part_counts:
                continue
            self.part_counts[result['name']] += 1
            if self.part_counts[result['name']] == part_success_threshold:
                self.part_ok_count += 1

        cur_time = time.time()
        if cur_time - self._last_snapshot_time > snapshot_interval_secs:
            print("Saving snapshots", self._n_snapshots_saved+1)
            for img, img_type in zip([frame_top, frame_bottom, frame_up], ["top", "bottom", "up"]):
                # img_name = f"{self.start_time.replace('-', '').replace(' ', '_')}_{self.psn}_{self.chassis}_{self.vehicle_model}_{img_type}_{self._n_snapshots_saved+1}.jpg"
                img_name = f"{self.chassis}_{self.vehicle_model}_{img_type}_{self._n_snapshots_saved+1}.jpg"
                img_path = os.path.join(snapshots_dir, img_name)
                print(img_path)
                height, width = img.shape[0], img.shape[1]
                img = cv2.resize(img, (1000, round(height * (1000 / width))))
                cv2.imwrite(img_path, img)
            self._last_snapshot_time = time.time()
            self._n_snapshots_saved += 1

    def save(self):
        result_ok_flag = int(self.part_ok_count >= len(self.part_list))

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
            for part_number in self.part_list:
                integer_metrics.append([
                    f'part_{part_number}',
                    int(self.part_counts[part_number] >= part_success_threshold)
                ])

        connection  = None
        try:
            connection = pymysql.connect(host=db_params['host'],
                                        user=db_params['user'],
                                        password=db_params['password'],
                                        database=db_params['database'])
            with connection.cursor() as cursor:
                insert_record_query = '''
                insert into record
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