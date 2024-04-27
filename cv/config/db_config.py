from .config import config

mysql_config = config['mysql']

db_params = {
    'host': mysql_config.get('host'),
    'port': mysql_config.getint('port'),
    'user': mysql_config.get('user'),
    'password': mysql_config.get('password'),
    'database': mysql_config.get('database'),
}