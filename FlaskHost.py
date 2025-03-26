"""
sudo nano /etc/systemd/system/apint_flask.service
"""


"""
[Unit]
Description=APINT Flask Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /git/apint_client/FlaskHost.py
WorkingDirectory=/git/apint_client
Restart=always
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target

"""

"""
sudo nano /etc/systemd/system/apint_flask.timer

"""

"""
[Unit]
Description=Check APINT Flask Service every 5 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Unit=apint_flask.service

[Install]
WantedBy=timers.target
"""


from flask import Flask, render_template
import subprocess
import os
import ntplib
from datetime import datetime

app = Flask(__name__,template_folder=os.path.dirname(os.path.abspath(__file__)))

# List of services and timers to check
services = [
    "ntp",
    "apintio_push_iid.service",
    "apintio_push_iid.timer",
    "apintio_flask.service",
    "apintio_flask.timer",
    "apintio_client_pyjs.service",
    "apintio_client_pyjs.timer"
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
def ntp_status():
    try:

        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('raspberrypi.local', port=123)

        local_time = datetime.now()
        ntp_time = datetime.fromtimestamp(response.tx_time, datetime.timezone.utc)
        offset = response.offset
        ntp_html = f"""
        <h1>NTP Status</h1>
        <p>Local Time: {local_time}</p>
        <p>NTP Time: {ntp_time}</p>
        <p>Offset: {offset} seconds</p>
        """
        return replace_body_in_default_html(ntp_html)
    except Exception as e:
        return replace_body_in_default_html(f"<h1>Error</h1><p>{e}</p>")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
