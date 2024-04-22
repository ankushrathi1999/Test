import configparser
import pathlib
import os

config_directory = pathlib.Path(__file__).parent.resolve()
config_files = [
    os.path.join(config_directory, 'app.config'),
    os.path.join(config_directory, 'app.priv.config'),
]

config = configparser.ConfigParser()
config.read(config_files)