import threading
from main.main import SystemJarvis
from flask import Flask, send_from_directory
import webbrowser
import time
import os
import sys
import logging
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
WEB_PORT = 5000
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "www")
HTML_FILE = "index.html"

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_jarvis():
    try:
        assistant = SystemJarvis()
        assistant.run()
    except KeyboardInterrupt:
        logger.info("Jarvis stopped by user.")
    except Exception as e:
        logger.error(f"Jarvis error: {e}")

def run_web_server():
    app = Flask(__name__, static_folder=ASSETS_DIR)

    @app.route('/')
    def serve_html():
        return send_from_directory(ASSETS_DIR, HTML_FILE)

    @app.route('/<path:filename>')
    def serve_static(filename):
        return send_from_directory(ASSETS_DIR, filename)

    if not is_port_in_use(WEB_PORT):
        app.run(host='0.0.0.0', port=WEB_PORT)
    else:
        logger.error(f"Port {WEB_PORT} is already in use!")

if __name__ == "__main__":
    try:
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()
        time.sleep(1)  # Wait for server to initialize
        webbrowser.open(f'http://localhost:{WEB_PORT}')
        run_jarvis()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")