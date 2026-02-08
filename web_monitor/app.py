import logging # Import logging
from flask import Flask, render_template, jsonify, send_from_directory
import subprocess
import re
import psutil # Import psutil
import os # Import os for path manipulation
import datetime # Import datetime for uptime calculation
import sys # Import sys
import requests # Import requests
import time # Import time for sleep
import json # Import json
from dotenv import load_dotenv # Import load_dotenv
from flask_cors import CORS # Import CORS
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app_logger = logging.getLogger(__name__)

try:
    from jtop import jtop
    JTOP_AVAILABLE = True
except ImportError:
    JTOP_AVAILABLE = False
    app_logger.info("jtop not found. Falling back to tegrastats for Jetson metrics.")

# paramiko import and SSH related functions removed as dbus-send is used for host reboot.
# Load environment variables from .env file
# This should be called as early as possible.
load_dotenv()

# Determine the base directory of the Flask app
# This assumes app.py is directly in home_ai_project/web_monitor/
basedir = os.path.abspath(os.path.dirname(__file__))

# Read the MONITOR_TARGET_HOST environment variable.
# If set, the app will attempt to fetch data from this remote host.
# Otherwise, it will fetch data from the local machine.
MONITOR_TARGET_HOST = os.environ.get('MONITOR_TARGET_HOST')
MONITOR_TARGET_PORT = os.environ.get('MONITOR_TARGET_PORT', '5000') # New line

# Configure Flask to serve React build by pointing to the 'dist' directory of the frontend.
# This ensures that when the Flask app runs, it can deliver the compiled
# React application (HTML, CSS, JavaScript) to the client's browser.
app = Flask(
    __name__,
    static_folder=os.path.join(basedir, 'frontend', 'dist', 'assets'), # Serve static assets (JS, CSS, images) from React's build output
    static_url_path='/assets', # Map these assets to the /assets URL path
    template_folder=os.path.join(basedir, 'frontend', 'dist') # Serve index.html from React's build output
)

CORS(app, origins=["http://localhost:5000", "http://192.168.1.16:5000"]) # Enable CORS for all routes

# execute_ssh_command function removed.

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static_root_files(filename):
    """
    Serve static files that are in the root of the 'frontend/dist' directory.
    This is necessary for assets like 'favicon.ico' or directly referenced SVGs
    that Vite places in the root of the build output.
    """
    return send_from_directory(app.template_folder, filename)

@app.route('/api/local_network_status')
def get_local_network_status():
    """
    Retrieves and returns network status information from the local machine.
    This function processes 'arp -a' command output to list connected devices.
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
                
                # Dynamically find the first non-lo network interface for MAC retrieval
                interfaces = os.listdir('/sys/class/net/')
                primary_iface = 'eth0' # Default
                for iface in interfaces:
                    if iface != 'lo' and not iface.startswith('br-') and not iface.startswith('docker'):
                        primary_iface = iface
                        break
                
                jetson_mac_result = subprocess.run(['cat', f'/sys/class/net/{primary_iface}/address'], capture_output=True, text=True, check=True)
                jetson_mac = jetson_mac_result.stdout.strip()
                devices.append({'ip': jetson_ip, 'mac': jetson_mac, 'interface': f'self (Jetson - {primary_iface})'})
            except Exception as e:
                app.logger.warning(f"Could not determine Jetson's own IP/MAC: {e}")


        return jsonify(devices)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f"Command failed: {e.cmd} - {e.stderr}"}), 500
    except FileNotFoundError:
        return jsonify({'error': "'arp' command not found. Is it installed and in PATH?"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/remote_network_status')
def get_remote_network_status():
    """
    Fetches network status information from a remote host specified by MONITOR_TARGET_HOST.
    This endpoint is active only if MONITOR_TARGET_HOST environment variable is set.
    It expects the remote host to be running a compatible web_monitor Flask application
    that exposes a /api/local_network_status endpoint.
    """
    if not MONITOR_TARGET_HOST:
        return jsonify({'error': 'MONITOR_TARGET_HOST is not set for remote network status.'}), 400
    
    try:
        # Construct the URL for the remote API endpoint
        remote_url = f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/local_network_status"
        app.logger.info(f"Fetching remote network status from: {remote_url}")
        response = requests.get(remote_url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching remote network status from {MONITOR_TARGET_HOST}: {e}")
        return jsonify({'error': f"Could not connect to remote host {MONITOR_TARGET_HOST} for network status: {e}"}), 500

@app.route('/api/local_system_info')
def get_local_system_info():
    """
    Retrieves and returns various system performance metrics from the local machine.
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

@app.route('/api/jetson_gpu_info')
def get_jetson_gpu_info():
    """
    Retrieves and returns GPU and system information from the Jetson.
    Uses the scripts/get_stats.py helper script for reliable data collection.
    """
    if sys.platform.startswith('win'):
        # On Windows, forward the request to the Jetson
        if not MONITOR_TARGET_HOST:
            return jsonify({'error': 'MONITOR_TARGET_HOST is not set for remote GPU info.'}), 400
        
        try:
            remote_url = f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/jetson_gpu_info"
            app_logger.info(f"Forwarding GPU info request to Jetson: {remote_url}")
            response = requests.get(remote_url)
            response.raise_for_status()
            return jsonify(response.json())
        except requests.exceptions.RequestException as e:
            app_logger.error(f"Error forwarding GPU info request to {MONITOR_TARGET_HOST}: {e}")
            return jsonify({'error': f"Could not connect to remote host {MONITOR_TARGET_HOST} for GPU info: {e}"}), 500
    
    # Running on Jetson - use the helper script
    try:
        # Resolve path to the script.
        # Inside Docker: /app/scripts/get_stats.py
        # Local Windows: ../scripts/get_stats.py (relative to basedir)
        script_path = os.path.join(basedir, 'scripts', 'get_stats.py')
        
        if not os.path.exists(script_path):
            # Try project root (one level up from web_monitor)
            script_path = os.path.abspath(os.path.join(basedir, '..', 'scripts', 'get_stats.py'))
        
        app_logger.info(f"Executing stats helper script: {script_path}")
        result = subprocess.run(['python3', script_path], capture_output=True, text=True, check=True)
        stats = json.loads(result.stdout)
        
        # Map the helper script's output to the frontend's expected format
        # RAM usage from script is a fraction (e.g. 0.62), we need to handle total ram separately
        # We'll use psutil for total ram to calculate the MB usage correctly
        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        
        response_data = {
            'gpu_usage_percent': stats.get('GPU', 0),
            'gpu_clock_mhz': stats.get('GR3D_FREQ', 0), # Note: If your script doesn't output this yet, it's 0
            'gpu_percent': stats.get('GPU', 0),
            'emc_percent': stats.get('EMC', 0),
            'gpu_temp_c': stats.get('Temp gpu', 0),
            'power_mw': stats.get('Power TOT', 0),
            'ram_usage_mb': round(stats.get('RAM', 0) * total_ram_gb * 1024, 2),
            'ram_total_mb': round(total_ram_gb * 1024, 2),
            'jtop_active': True,
            'raw_stats': stats # Optional: include for debugging
        }
        
        return jsonify(response_data)

    except Exception as e:
        app_logger.error(f"Failed to retrieve GPU info via helper script: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/remote_system_info')
def get_remote_system_info():
    """
    Fetches system performance metrics from a remote host specified by MONITOR_TARGET_HOST.
    This endpoint is active only if MONITOR_TARGET_HOST environment variable is set.
    It expects the remote host to be running a compatible web_monitor Flask application
    that exposes a /api/local_system_info endpoint.
    """
    if not MONITOR_TARGET_HOST:
        return jsonify({'error': 'MONITOR_TARGET_HOST is not set for remote system info.'}), 400
    
    try:
        # Construct the URL for the remote API endpoint
        remote_url = f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/local_system_info"
        app.logger.info(f"Fetching remote system info from: {remote_url}")
        response = requests.get(remote_url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching remote system info from {MONITOR_TARGET_HOST}: {e}")
        return jsonify({'error': f"Could not connect to remote host {MONITOR_TARGET_HOST} for system info: {e}"}), 500

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

@app.route('/api/config')
def get_config():
    """
    Returns configuration information to the frontend,
    specifically whether MONITOR_TARGET_HOST is set and its value.
    """
    return jsonify({
        'monitor_target_host_set': bool(MONITOR_TARGET_HOST),
        'monitor_target_host': MONITOR_TARGET_HOST, # Return the actual value
        'monitor_target_port': MONITOR_TARGET_PORT # New line: Return the configured port
    })

from flask import request # Import request for handling POST data

@app.route('/api/command/reboot', methods=['POST'])
def command_reboot():
    app_logger.info("Received request to reboot system.")
    data = request.json
    reboot_type = data.get('type', 'soft').lower() # Default to soft reboot

    if sys.platform.startswith('win'):
        app_logger.info(f"Running on Windows. Forwarding '{reboot_type}' reboot request to Jetson.")
        if not MONITOR_TARGET_HOST:
            return jsonify({'status': 'error', 'message': 'MONITOR_TARGET_HOST is not set for forwarding reboot request.'}), 400
        
        try:
            remote_url = f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/command/reboot"
            headers = {"Content-Type": "application/json"}
            response = requests.post(remote_url, headers=headers, data=json.dumps({'type': reboot_type}))
            response.raise_for_status()
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            app_logger.error(f"Error forwarding reboot request to Jetson at {remote_url}: {e}")
            return jsonify({'status': 'error', 'message': f"Failed to forward reboot request to Jetson: {e}"}), 500
    else: # Running on non-Windows (Jetson)
        if reboot_type == 'soft':
            try:
                # Command to restart the Docker container itself
                # This assumes the container has access to the Docker daemon (e.g., /var/run/docker.sock is mounted)
                container_name = os.environ.get('HOSTNAME') # Gets the container's hostname, often its name
                if not container_name:
                    app_logger.warning("Could not determine container name from HOSTNAME environment variable. Defaulting to 'home_ai_dashboard'.")
                    container_name = "home_ai_dashboard"
                
                # Using subprocess.Popen for non-blocking execution, similar to dbus-send
                subprocess.Popen(['docker', 'restart', container_name],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                
                app_logger.info(f"Initiated soft reboot (restart) of Docker container '{container_name}'.")
                return jsonify({'status': 'success', 'message': f"Docker container '{container_name}' is initiating a restart."}), 200
            except Exception as e:
                app_logger.error(f"An unexpected error occurred while initiating soft reboot of container: {e}")
                return jsonify({'status': 'error', 'message': f'An unexpected error occurred during container soft reboot: {str(e)}'}), 500
        elif reboot_type == 'hard':
            try:
                # Sends a signal to the host systemd via the mounted D-Bus
                # This is a graceful system reboot
                cmd = [
                    "dbus-send", "--system", "--print-reply", 
                    "--dest=org.freedesktop.login1", 
                    "/org/freedesktop/login1", 
                    "org.freedesktop.login1.Manager.Reboot", 
                    "boolean:true"
                ]
                subprocess.Popen(cmd,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                
                app_logger.info("Initiated hard reboot via dbus-send.")
                return jsonify({'status': 'success', 'message': 'System is initiating a hard reboot.'}), 200
            except Exception as e:
                app_logger.error(f"An unexpected error occurred while initiating hard reboot: {e}")
                return jsonify({'status': 'error', 'message': f'An unexpected error occurred during hard reboot: {str(e)}'}), 500
        else:
            app_logger.warning(f"Invalid reboot type received: {reboot_type}")
            return jsonify({'status': 'error', 'message': f'Invalid reboot type specified: {reboot_type}. Must be "soft" or "hard".'}), 400






@app.route('/api/chat', methods=['POST'])

def chat_with_ollama():

    """

    Handles chat requests, forwarding them to the local Ollama server

    and returning its response.

    """

    data = request.json

    prompt = data.get("prompt")

    model_name = data.get("model", "qwen:1.8b") # Default model



    if not prompt:

        return jsonify({"error": "No prompt provided"}), 400



    ollama_host = os.environ.get("OLLAMA_HOST", "http://ollama:11434")

    url = f"{ollama_host}/api/generate"

    headers = {"Content-Type": "application/json"}

    ollama_data = {

        "model": model_name,

        "prompt": prompt,

        "stream": False,

    }



    try:

        app.logger.info(f"Sending prompt to Ollama: {prompt} (model: {model_name})")

        response = requests.post(url, headers=headers, data=json.dumps(ollama_data))

        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        

        ollama_result = response.json()

        if "response" in ollama_result:

            return jsonify({"response": ollama_result["response"]}), 200

        elif "error" in ollama_result:

            app.logger.error(f"Error from Ollama: {ollama_result['error']}")

            return jsonify({"error": f"Ollama Error: {ollama_result['error']}"}), 500

        else:

            app.logger.error(f"Unexpected Ollama response format: {ollama_result}")

            return jsonify({"error": "Unexpected Ollama response format."}), 500



    except requests.exceptions.ConnectionError:

        app.logger.error("Connection Error: Is Ollama running? Check `ollama ps` and `ollama serve`.")

        return jsonify({"error": "Connection Error: Ollama server not reachable. Is it running?"}), 500

    except requests.exceptions.RequestException as e:

        app.logger.error(f"Request to Ollama failed: {e}")

        return jsonify({"error": f"Request to Ollama failed: {e}"}), 500

    except Exception as e:

        app.logger.error(f"An unexpected error occurred during Ollama chat: {e}")

        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500





if __name__ == '__main__':
    # When this script is executed directly, run the Flask development server.
    # host='0.0.0.0' makes the server externally accessible from any IP address.
    # port=5000 sets the port on which the server listens for incoming requests.
    # debug=True enables debug mode, providing detailed error messages and auto-reloading
    # upon code changes. This should be set to False in production environments.
    app.run(host='0.0.0.0', port=5000, debug=True)