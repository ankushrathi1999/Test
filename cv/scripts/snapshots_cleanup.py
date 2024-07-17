import os
from datetime import datetime, timedelta
import pymysql
import pymysql.cursors
import logging
import logging.config
import yaml

if __name__ == '__main__':
    with open('logging.yaml', 'r') as f:
        logging_config = yaml.safe_load(f.read())
        logging_config['handlers']['file']['filename'] = 'logs/snapshots_cleanup.log'
        logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

from config.config import config
from config.db_config import db_params

api_config = config['api_artifact']
snapshots_dir = api_config.get('snapshots_dir')
metadata_dir = api_config.get('metadata_dir')

script_config = config['script_snapshot_cleanup']
n_backup_days = script_config.getint('n_backup_days')
n_chassis_backup = script_config.getint('n_chassis_backup')

def get_chassis_list_to_keep():
    date_filter = (datetime.now() - timedelta(days=n_backup_days)).strftime("%Y-%m-%d")
    query = """
        WITH RankedChassis AS (
            SELECT
                e.code AS vehicle_model,
                value AS chassis_no,
                r.created_on,
                ROW_NUMBER() OVER (PARTITION BY e.code ORDER BY r.created_on DESC) AS chassis_rank
            FROM Record r
            JOIN DataStringMetric c ON c.record_id = r.id
            JOIN DataFilter df ON df.record_id = r.id
            JOIN Entity e ON df.entity_id = e.id
            WHERE e.entity_type_id = 2
            AND c.entity_id = 4002
            AND r.created_on <= %s
        )
        SELECT distinct(chassis_no)
        FROM RankedChassis
        WHERE chassis_rank <= %s;
    """
    connection  = None
    chassis = set()
    try:
        connection = pymysql.connect(host=db_params['host'],
                                    user=db_params['user'],
                                    password=db_params['password'],
                                    database=db_params['database'])
        with connection.cursor() as cursor:
            cursor.execute(query, (date_filter, n_chassis_backup))
            for row in cursor.fetchall():
                chassis.add(row[0])
    except Exception as ex:
        logger.exception("Error fetching chassis list.")
    finally:
        if connection is not None:
            connection.close()
    return chassis

def get_folders_to_backup(base_dir):
    date_filter = (datetime.now() - timedelta(days=n_backup_days)).strftime("%Y%m%d")
    folders_to_backup = []

    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if not os.path.isdir(folder_path):
            continue
        try:
            datetime.strptime(folder, "%Y%m%d").date() # validation
            if folder < date_filter:
                folders_to_backup.append(folder_path)
        except ValueError:
            logger.warning("Failed to parse folder name: %s", folder)

    return folders_to_backup


def delete_old_snapshots():
    logger.info("Initializing snapshots deletion.")
    chassis_keep = get_chassis_list_to_keep()
    logger.info("Num chassis to keep: %s", len(chassis_keep))
    for target_dir in [snapshots_dir, metadata_dir]:
        logger.info("Deleting in target dir: %s", target_dir)
        backup_folders = get_folders_to_backup(target_dir)
        logger.info("Num backup folders: %s", len(backup_folders))
        for folder in backup_folders:
            logger.info("Deleting in folder: %s", folder)
            for root, _, files in os.walk(folder):
                for file in files:
                    try:
                        chassis_no, vehicle_model = file.split('_')[:2]
                    except Exception as ex:
                        logger.warning("Failed to parse file: %s. Err: %s", file, ex)
                    if chassis_no in chassis_keep:
                        continue
                    file_path = os.path.join(root, file)
                    logger.info("Deleting: %s", file_path)
                    os.remove(file_path)

if __name__ == '__main__':
    delete_old_snapshots()