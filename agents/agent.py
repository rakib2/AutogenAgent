import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from prometheus_client import start_http_server, Summary, Counter
from pathlib import Path

# Import your cloud-specific agent modules
import agent_aws
import agent_azure

# Initialize Flask app
app = Flask(__name__)

# Prometheus metrics
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
ERROR_COUNTER = Counter('error_count', 'Count of errors')

# Initialize logging
logging.basicConfig(level=logging.INFO)

@app.route('/aws', methods=['POST'])
@REQUEST_TIME.time()
def handle_aws():
    try:
        message = request.json.get('message')
        response = agent_aws.process_message(message)
        return jsonify({'status': 'success', 'response': response}), 200
    except Exception as e:
        ERROR_COUNTER.inc()
        logging.error(f"Error handling AWS task: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/azure', methods=['POST'])
@REQUEST_TIME.time()
def handle_azure():
    try:
        message = request.json.get('message')
        response = agent_azure.process_message(message)
        return jsonify({'status': 'success', 'response': response}), 200
    except Exception as e:
        ERROR_COUNTER.inc()
        logging.error(f"Error handling Azure task: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/alerts', methods=['POST'])
def receive_alerts():
    alert = request.json
    logging.info(f"Received alert: {alert}")
    # Process the alert and take necessary action
    # Example: Forward alert to the appropriate agent
    if 'aws' in alert['description'].lower():
        response = agent_aws.handle_alert(alert)
    elif 'azure' in alert['description'].lower():
        response = agent_azure.handle_alert(alert)
    else:
        response = "Unknown alert type"
    return jsonify({'status': 'received', 'alert': alert, 'response': response}), 200

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # This can be an endpoint to serve your custom dashboard for alerts
    return "This is the custom alert dashboard."

if __name__ == '__main__':
    start_http_server(8000)  # Prometheus metrics will be available on port 8000
    app.run(host='0.0.0.0', port=5000)
