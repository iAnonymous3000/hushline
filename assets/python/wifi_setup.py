from flask import Flask, render_template, request, redirect, url_for, flash
import json
import subprocess
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'a default secret key'

@app.route('/')
def index():
    return render_template('wifi-setup.html')

@app.route('/wifi-setup', methods=['POST'])
def setup_wifi():
    ssid = request.form['ssid']
    password = request.form['password']
    
    # Validate the SSID and password
    if not ssid or not password:
        flash('SSID and password are required!')
        return redirect(url_for('index'))
    if len(password) < 8:
        flash('Password must be at least 8 characters long!')
        return redirect(url_for('index'))

    # Configure Wi-Fi with the validated credentials
    configure_wifi(ssid, password)

    # Save the details to a file, or do whatever you need with them
    with open('/tmp/wifi_setup.json', 'w') as f:
        json.dump({'ssid': ssid, 'password': password}, f)

    return redirect(url_for('success'))

@app.route('/success')
def success():
    return "Wi-Fi setup was successful!"

def configure_wifi(ssid, password):
    # Example of how you might configure Wi-Fi on a Raspberry Pi
    config_lines = [
        '\n',
        'network={\n',
        '    ssid="%s"\n' % ssid,
        '    psk="%s"\n' % password,
        '}\n'
    ]
    
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as wifi:
        wifi.writelines(config_lines)
    
    # Restart the Wi-Fi interface
    subprocess.run(['wpa_cli', '-i', 'wlan0', 'reconfigure'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)