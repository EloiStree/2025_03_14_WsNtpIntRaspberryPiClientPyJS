

# http://apint-home.ddns.net:8080/services
# http://apint-home.ddns.net:8080/client
# http://apint-home.ddns.net:8080/ntp

# http://raspberrypi:8080/services
# http://raspberrypi:8080/client
# http://raspberrypi:8080/ntp


import os
import sys

if sys.stdout.isatty():
    print("Running in a terminal.")
    stop_service_script ="""
    sudo systemctl stop apint_flask.service
    sudo systemctl stop apint_flask.timer
    """

    # run code to stop current service
    os.system(stop_service_script)

else:
    print("Not running in a terminal.")



from flask import Flask, jsonify, render_template, request
import subprocess
import os
import ntplib
from datetime import datetime, timezone
import time

app = Flask(__name__,template_folder=os.path.dirname(os.path.abspath(__file__)))

# List of services and timers to check
services = [
    "ntp",
    "apint_push_iid.service",
    "apint_push_iid.timer",
    "apint_flask.service",
    "apint_flask.timer",
    "apint_client_pyjs.service",
    "apint_client_pyjs.timer"
]

def get_service_status(service):
    try:
        result = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        status = result.stdout.strip()
        return status
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def home():
    return """
Hello, World!
- raspberrypi.local:8080/client
- raspberrypi.local:8080/services
"""

def replace_body_in_default_html(body):
    html_page_to_load= "WWW/insert_body_here.html"
    html_template = open(html_page_to_load).read()
    html_template = html_template.replace("BODY", body)
    return html_template

@app.route('/services')
def services_route():
    service_statuses = {service: get_service_status(service) for service in services}
    #unpack  the json to make it more readyable in html
    html_services = """
    <table border="1" style="width:100%; text-align:left;">
        <thead>
            <tr>
                <th>Service</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
    """
    for service, status in service_statuses.items():
        color = "green" if status == "active" else "red"
        html_services += f"<tr><td>{service}</td><td style='color:{color};'>{status}</td></tr>"
    html_services += """
        </tbody>
    </table>
    """
    return replace_body_in_default_html(html_services)

@app.route('/client')
def client_page():
    return render_template('RunClient.html')


@app.route('/ntp')
def ntp_page():
    return render_template('WWW/client_ntp_page.html')


@app.route('/ntp-offset', methods=['POST'])
def ntp_post_offset():
    data = request.get_json()

    # Extract the timestamp from the request
    client_timestamp = data.get('timestamp')

    if client_timestamp is None:
        return jsonify({'error': 'Timestamp not provided'}), 400

    # Get the current server timestamp in milliseconds
    server_timestamp = int(time.time() * 1000)

    # Calculate the offset (server time minus client time)
    offset = server_timestamp - client_timestamp

    # Return the offset result
    return jsonify({'offset': offset})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
