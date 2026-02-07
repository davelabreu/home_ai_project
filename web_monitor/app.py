from flask import Flask, render_template, jsonify, send_from_directory
import subprocess
import re
import psutil # Import psutil
import os # Import os for path manipulation
import datetime # Import datetime for uptime calculation

# Determine the base directory of the Flask app
# This assumes app.py is directly in home_ai_project/web_monitor/
basedir = os.path.abspath(os.path.dirname(__file__))

# Configure Flask to serve React build
app = Flask(
    __name__,
    static_folder=os.path.join(basedir, 'frontend', 'dist', 'assets'),
    static_url_path='/assets', # React's build often puts assets in /assets
    template_folder=os.path.join(basedir, 'frontend', 'dist')
)

@app.route('/')
def serve_react_app():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/api/network_status')
def get_network_status():
    try:
        # Execute 'arp -a' to get connected devices
        # This command is common on Linux systems to show the ARP cache
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
        output_lines = result.stdout.splitlines()

        devices = []
        # Regex to parse 'arp -a' output: '? (IP_ADDRESS) at MAC_ADDRESS) at MAC_ADDRESS [ether] on INTERFACE'
        # Example: ? (192.168.1.1) at 00:11:22:33:44:55 [ether] on eth0
        arp_pattern = re.compile(r'\? \((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\) at ([0-9a-fA-F:]+) \[ether\] on (\w+)')

        for line in output_lines:
            match = arp_pattern.search(line)
            if match:
                ip, mac, interface = match.groups()
                devices.append({'ip': ip, 'mac': mac, 'interface': interface})
        
        # Add Jetson's own IP/MAC (this assumes the Jetson is the one running the Flask app)
        # You might need a more robust way to get the Jetson's own IP/MAC
        try:
            jetson_ip_result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, check=True)
            jetson_ip = jetson_ip_result.stdout.split()[0]
            jetson_mac_result = subprocess.run(['cat', '/sys/class/net/eth0/address'], capture_output=True, text=True, check=True) # Assumes eth0
            jetson_mac = jetson_mac_result.stdout.strip()
            devices.append({'ip': jetson_ip, 'mac': jetson_mac, 'interface': 'self (Jetson)'})
        except Exception as e:
            app.logger.warning(f"Could not determine Jetson's own IP/MAC: {e}")


        return jsonify(devices)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f"Command failed: {e.cmd} - {e.stderr}"}), 500
    except FileNotFoundError:
        return jsonify({'error': "'arp' command not found. Is it installed and in PATH?"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system_info')
def get_system_info():
    try:
        cpu_percent = psutil.cpu_percent(interval=1) # interval for a non-blocking call
        virtual_memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/') # Get disk usage for the root partition
        boot_time_timestamp = psutil.boot_time()
        uptime_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_time_timestamp)).total_seconds()
        
        mem_percent = virtual_memory.percent
        mem_total_gb = round(virtual_memory.total / (1024**3), 2)
        mem_used_gb = round(virtual_memory.used / (1024**3), 2)

        disk_percent = disk_usage.percent
        disk_total_gb = round(disk_usage.total / (1024**3), 2)
        disk_used_gb = round(disk_usage.used / (1024**3), 2)

        # Format uptime for better readability
        days, remainder = divmod(int(uptime_seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_formatted = f"{days}d {hours}h {minutes}m"


        return jsonify({
            'cpu_percent': cpu_percent,
            'memory_percent': mem_percent,
            'memory_total_gb': mem_total_gb,
            'memory_used_gb': mem_used_gb,
            'disk_percent': disk_percent,
            'disk_total_gb': disk_total_gb,
            'disk_used_gb': disk_used_gb,
            'uptime': uptime_formatted
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deploy/<action_name>')
def deploy_action(action_name):
    # This is a placeholder. In a real scenario, you'd add logic here
    # to perform deployment tasks based on action_name.
    app.logger.info(f"Received request to deploy action: {action_name}")
    return jsonify({'status': 'success', 'message': f'Deployment action "{action_name}" received and will be processed.'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)