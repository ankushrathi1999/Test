import time
import threading
import traceback
from werkzeug.serving import make_server
from flask import Flask, jsonify

from utils.plc import send_signal
from config.plc_db import SIG_SEND_HEART_BIT
from config.config import config
from api.state import PLC_STATES
from utils.db import test_conection

process_config = config['process_health_server']
port = process_config.getint('port')

server = None
app = Flask(__name__)

def _run_health_server(thread):
    data = thread.data

    @app.route('/health')
    def health():
        health = {
            'inspection': True,
            'plc': data.state.plc_state == PLC_STATES.HEALTHY,
            'database': test_conection(),
        }
        print("Health endpoint:", health)
        return jsonify(health), 200

    try:
        global server
        server = make_server('localhost', port, app)
        server.serve_forever()
    except Exception as ex:
        print("Health server error:", ex)
    finally:
        thread.is_terminated = True
    print("End of health server thread")

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
