import pymysql
import pymysql.cursors
from collections import defaultdict
import logging

from config.db_config import db_params

logger = logging.getLogger(__name__)

def test_conection():
    query = 'select 1 from Entity;'
    connection  = None
    try:
        connection = pymysql.connect(host=db_params['host'],
                                    user=db_params['user'],
                                    password=db_params['password'],
                                    database=db_params['database'])
        with connection.cursor() as cursor:
            cursor.execute(query)
            return True
    except Exception:
        logger.exception("Error connecting to database")
        return False
    finally:
        if connection is not None:
            connection.close()

def get_entity_lookup():
    query = """
        select m.code as type, e.code as code, e.id as id from Entity e join EntityTypeMaster m on e.entity_type_id = m.id;
    """
    connection  = None
    lookup = {}
    try:
        connection = pymysql.connect(host=db_params['host'],
                                    user=db_params['user'],
                                    password=db_params['password'],
                                    database=db_params['database'],
                                    cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                lookup_key = f"{row['type']}_{row['code']}"
                lookup[lookup_key] = row["id"]
        return lookup
    except Exception as ex:
        logger.exception("Error fetching enetity metadata.")
        raise ex
    finally:
        if connection is not None:
            connection.close()


def insert_datafilter(cursor, record_id, entity_id, metric_id):
    insert_data_query = '''
    insert into DataFilter
    (record_id, entity_id, metric_id)
    values
    (%s, %s, %s)
    '''
    cursor.execute(insert_data_query, (record_id, entity_id, metric_id))

def insert_string_metric(cursor, record_id, entity_id, value, metric_id):
    insert_data_query = '''
    insert into DataStringMetric
    (record_id, entity_id, value, metric_id)
    values
    (%s, %s, %s, %s)
    '''
    cursor.execute(insert_data_query, (record_id, entity_id, value, metric_id))

def insert_integer_metric(cursor, record_id, entity_id, value, metric_id):
    insert_data_query = '''
    insert into DataIntegerMetric
    (record_id, entity_id, value, metric_id)
    values
    (%s, %s, %s, %s)
    '''
    cursor.execute(insert_data_query, (record_id, entity_id, value, metric_id))

def get_vehicle_models():
    query = """
        select code as vehicle_model from Entity where entity_type_id = 2 and activeFlag = 1
    """
    connection  = None
    rows = []
    try:
        connection = pymysql.connect(host=db_params['host'],
                                    user=db_params['user'],
                                    password=db_params['password'],
                                    database=db_params['database'],
                                    cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                rows.append(row['vehicle_model'])
        return rows
    except Exception as ex:
        logger.exception("Error fetching vehicle part mapping.")
        raise ex
    finally:
        if connection is not None:
            connection.close()

def get_vehicle_part_mapping(vehicle_models, keep_inactive_parts=False):
    query = f"""
        select EP.code as vehicle_model, EC.code as part_number, EC.name as part_name, HM.value as part_position
        from EntityHierarchy H join Entity EP on H.parent_id = EP.id
        join Entity EC on H.child_id = EC.id
        left join EntityHierarchyMetricTable HM on HM.entity_hierarchy_id = H.id
        {"" if keep_inactive_parts else "where EC.activeFlag = 1"}
    """
    connection  = None
    mapping = defaultdict(list)
    try:
        connection = pymysql.connect(host=db_params['host'],
                                    user=db_params['user'],
                                    password=db_params['password'],
                                    database=db_params['database'],
                                    cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                if row['vehicle_model'] in vehicle_models:
                    mapping[row['vehicle_model']].append(row)
        return mapping
    except Exception as ex:
        logger.exception("Error fetching vehicle part mapping.")
        raise ex
    finally:
        if connection is not None:
            connection.close()