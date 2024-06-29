import sys
sys.path.append('..')

import pandas as pd
import pymysql
import pymysql.cursors

from config.db_config import db_params

entity_hierarchy_csv_path = '../../../hypervise-api-server/MasterDatabase/TABLE_DATA_CSV_FILES/EntityHierarchy.csv'
entity_hierarchy_metric_csv_path = '../../../hypervise-api-server/MasterDatabase/TABLE_DATA_CSV_FILES/EntityHierarchyMetricTable.csv'

def insert_hierarchy_row(cursor, id, parent_id, child_id):
    # print(id, parent_id, child_id)
    cursor.execute("insert into EntityHierarchy (id, parent_id, child_id) values (%s, %s, %s)", [id, parent_id, child_id])

def insert_metric_row(cursor, id, entity_hierarchy_id,value,metadata_name):
    # print(id, entity_hierarchy_id,value,metadata_name)
    cursor.execute("insert into EntityHierarchyMetricTable (id, entity_hierarchy_id,value,metadata_name) values (%s, %s, %s, %s)", [id,entity_hierarchy_id,value,metadata_name])

def run():
    hierarchy = pd.read_csv(entity_hierarchy_csv_path)
    metrics = pd.read_csv(entity_hierarchy_metric_csv_path)
    connection = None
    try:
        connection = pymysql.connect(host=db_params['host'],
                                    user=db_params['user'],
                                    password=db_params['password'],
                                    database=db_params['database'],
                                    cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute('delete from EntityHierarchyMetricTable')
            cursor.execute('delete from EntityHierarchy')
            for _, row in hierarchy.iterrows():
                insert_hierarchy_row(cursor, row.id, row.parent_id, row.child_id)
            for _, row in metrics.iterrows():
                insert_metric_row(cursor, row.id, row.entity_hierarchy_id, row.value, row.metadata_name)
        connection.commit()
    except Exception as ex:
        print("Error", ex)
        raise ex
    finally:
        if connection is not None:
            connection.close()
    

if __name__ == '__main__':
    run()
