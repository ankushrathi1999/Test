import sys
sys.path.append('..')

import pandas as pd
import pymysql
import pymysql.cursors

from config.db_config import db_params

entity_csv_path = '../../../hypervise-api-server/MasterDatabase/TABLE_DATA_CSV_FILES/Entity.csv'

def update_entity_name(cursor, entity_id, entity_name):
    # print("update Entity set name = %s where id = %s", entity_name, entity_id)
    cursor.execute("update Entity set name = %s where id = %s", [entity_name, entity_id])

def run():
    entities = pd.read_csv(entity_csv_path)
    connection = None
    try:
        connection = pymysql.connect(host=db_params['host'],
                                    user=db_params['user'],
                                    password=db_params['password'],
                                    database=db_params['database'],
                                    cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            for _, row in entities.iterrows():
                update_entity_name(cursor, row.id, row['name'])
        connection.commit()
    except Exception as ex:
        print("Error", ex)
        raise ex
    finally:
        if connection is not None:
            connection.close()
    

if __name__ == '__main__':
    run()
