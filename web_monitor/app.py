from flask import Flask, render_template, jsonify, send_from_directory
import subprocess
import re
import psutil # Import psutil
import os # Import os for path manipulation
import datetime # Import datetime for uptime calculation
import sys # Import sys

# Determine the base directory of the Flask app
# This assumes app.py is directly in home_ai_project/web_monitor/
basedir = os.path.abspath(os.path.dirname(__file__))

# Configure Flask to serve React build by pointing to the 'dist' directory of the frontend.
# This ensures that when the Flask app runs, it can deliver the compiled
# React application (HTML, CSS, JavaScript) to the client's browser.
app = Flask(
    __name__,
    static_folder=os.path.join(basedir, 'frontend', 'dist', 'assets'), # Serve static assets (JS, CSS, images) from React's build output
    static_url_path='/assets', # Map these assets to the /assets URL path
    template_folder=os.path.join(basedir, 'frontend', 'dist') # Serve index.html from React's build output
)

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/api/network_status')
def get_network_status():
    """
    Retrieves and returns network status information, specifically a list of
    connected devices (IP, MAC, Interface) by parsing the 'arp -a' command output.
    It also attempts to include the Jetson's own IP and MAC address, or handles Windows.
    """
    devices = []
    try:
        if sys.platform.startswith('win'):
            # Windows specific 'arp -a' command and parsing
            # On Windows, 'arp -a' output format is different.
            # Example:
            #   Interface: 192.168.1.10 --- 0x1
            #     Internet Address      Physical Address      Type
            #     192.168.1.1           00-11-22-33-44-55     dynamic
            #     192.168.1.100         AA-BB-CC-DD-EE-FF     static
            
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
            output_lines = result.stdout.splitlines()

            # Regex for Windows arp -a output: IP Address, MAC Address, Type
            # IP: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
            # MAC: ([0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2})
            # Type: (dynamic|static)
            # Need to handle potential leading/trailing spaces and the structure.
            arp_pattern_win = re.compile(r'\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*([0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2})\s*(dynamic|static)')

            for line in output_lines:
                match = arp_pattern_win.search(line)
                if match:
                    ip, mac, _type = match.groups()
                    devices.append({'ip': ip, 'mac': mac.replace('-', ':'), 'interface': 'unknown (Windows)'}) # Interface retrieval is complex on Windows with `arp -a`; defaulting to 'unknown'.
        else: # Linux/Jetson specific logic
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
            output_lines = result.stdout.splitlines()

            # Regex to parse 'arp -a' output on Linux: '? (IP_ADDRESS) at MAC_ADDRESS [ether] on INTERFACE'
            arp_pattern_linux = re.compile(r'\? \((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\) at ([0-9a-fA-F:]+) \[ether\] on (\w+)')

            for line in output_lines:
                match = arp_pattern_linux.search(line)
                if match:
                    ip, mac, interface = match.groups()
                    devices.append({'ip': ip, 'mac': mac, 'interface': interface})
            
            # Attempt to add the Jetson device's own IP and MAC address to the list.
            try:
                jetson_ip_result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, check=True)
                jetson_ip = jetson_ip_result.stdout.split()[0]
                jetson_mac_result = subprocess.run(['cat', '/sys/class/net/eth0/address'], capture_output=True, text=True, check=True)
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
    """
    Retrieves and returns various system performance metrics such as CPU usage,
    memory usage, disk usage, and system uptime.
    Utilizes the psutil library for cross-platform system information retrieval.
    """
    try:
        # psutil.cpu_percent returns a system-wide CPU utilization as a percentage.
        # interval=1 makes it a blocking call for 1 second to get a meaningful sample.
        cpu_percent = psutil.cpu_percent(interval=1) 
        virtual_memory = psutil.virtual_memory() # Get system memory usage statistics
        disk_usage = psutil.disk_usage('/') # Get disk usage for the root partition ('/')
        boot_time_timestamp = psutil.boot_time() # Get the system boot time as a Unix timestamp
        # Calculate uptime by subtracting boot time from current time
        uptime_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_time_timestamp)).total_seconds()
        
        mem_percent = virtual_memory.percent
        mem_total_gb = round(virtual_memory.total / (1024**3), 2)
        mem_used_gb = round(virtual_memory.used / (1024**3), 2)

        disk_percent = disk_usage.percent
        disk_total_gb = round(disk_usage.total / (1024**3), 2)
        disk_used_gb = round(disk_usage.used / (1024**3), 2)

        # Format uptime from seconds into a more human-readable string (days, hours, minutes)
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
    """
    Placeholder endpoint for handling deployment actions.
    In a production scenario, this endpoint would trigger specific deployment
    scripts or commands based on the 'action_name'.
    
    Security Note: Any real deployment action should involve robust authentication,
    authorization, and validation to prevent unauthorized or malicious operations.
    Direct execution of arbitrary commands based on user input is highly discouraged.
    """
    app.logger.info(f"Received request to deploy action: {action_name}")
    return jsonify({'status': 'success', 'message': f'Deployment action "{action_name}" received and will be processed.'})


if __name__ == '__main__':
    # When this script is executed directly, run the Flask development server.
    # host='0.0.0.0' makes the server externally accessible from any IP address.
    # port=5000 sets the port on which the server listens for incoming requests.
    # debug=True enables debug mode, providing detailed error messages and auto-reloading
    # upon code changes. This should be set to False in production environments.
    app.run(host='0.0.0.0', port=5000, debug=True)