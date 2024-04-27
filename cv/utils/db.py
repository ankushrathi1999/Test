import pymysql
import pymysql.cursors

from config.db_config import db_params

def get_entity_lookup():
    query = """
        select m.code as type, e.code as code, e.id as id from entity e join entitytypemaster m on e.entity_type_id = m.id;
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
        print("Error fetching enetity metadata.", ex)
        raise ex
    finally:
        if connection is not None:
            connection.close()


def insert_datafilter(cursor, record_id, entity_id):
    insert_data_query = '''
    insert into datafilter
    (record_id, entity_id)
    values
    (%s, %s)
    '''
    cursor.execute(insert_data_query, (record_id, entity_id))

def insert_string_metric(cursor, record_id, entity_id, value):
    insert_data_query = '''
    insert into datastringmetric
    (record_id, entity_id, value)
    values
    (%s, %s, %s)
    '''
    cursor.execute(insert_data_query, (record_id, entity_id, value))

def insert_integer_metric(cursor, record_id, entity_id, value):
    insert_data_query = '''
    insert into dataintegermetric
    (record_id, entity_id, value)
    values
    (%s, %s, %s)
    '''
    cursor.execute(insert_data_query, (record_id, entity_id, value))