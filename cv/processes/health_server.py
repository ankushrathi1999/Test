import threading
import logging
from werkzeug.serving import make_server
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

from utils.plc import send_signal
from config.plc_db import SIG_SEND_HEART_BIT
from config.config import config
from api.state import PLC_STATES
from utils.db import test_conection
from utils.build_vehicle_master import validate_vehicle_part_data

logger  = logging.getLogger(__name__)

process_config = config['process_health_server']
port = process_config.getint('port')

server = None
app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

def _run_health_server(thread):
    data = thread.data

    @app.route('/health')
    def health():
        health = {
            'inspection': True,
            'plc': data.state.plc_state == PLC_STATES.HEALTHY,
            'database': test_conection(),
        }
        logger.debug("Health endpoint: %s", health)
        return jsonify(health), 200
    
    @app.route('/validate/<vehicle_model>')
    @cross_origin()
    def validate(vehicle_model):
        if not vehicle_model:
            return jsonify({'error': 'vehicle_model parameter is missing.'}), 400
        is_valid, errors = validate_vehicle_part_data(vehicle_model)
        validate_data = {
            "is_valid": is_valid,
            "errors": errors,
        }
        logger.debug("Validate endpoint: %s", validate_data)
        return jsonify(validate_data), 200

    try:
        global server
        logger.info("Starting health server at http://localhost:%s", port)
        server = make_server('localhost', port, app)
        server.serve_forever()
    except Exception as ex:
        logger.exception("Health server error.")
    finally:
        thread.is_terminated = True
    logger.info("End of health server thread.")

class HealthServer:

    def __init__(self, data):
        self.data = data
        self.is_terminated = False
        self.runner = None

    def start(self):
        self.runner = threading.Thread(target=_run_health_server, args=(self,))
        self.runner.start()

    def stop(self):
        global server
        server.shutdown()

    def wait(self):
        self.runner.join()
