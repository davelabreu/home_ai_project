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
    import docker
    DOCKER_AVAILABLE = True
    docker_client = docker.from_env()
except Exception as e:
    DOCKER_AVAILABLE = False
    app_logger.warning(f"Docker client could not be initialized: {e}")

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

CORS(app, origins=["http://localhost:5000", "http://192.168.1.21:5000"]) # Enable CORS for all routes

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

def load_device_names():
    """Loads device names from a JSON file and ensures MACs are uppercase."""
    names_path = os.path.join(basedir, 'device_names.json')
    if os.path.exists(names_path):
        try:
            with open(names_path, 'r') as f:
                data = json.load(f)
                # Convert all keys to uppercase for consistent lookup
                return {k.upper(): v for k, v in data.items()}
        except Exception as e:
            app_logger.error(f"Error loading device names: {e}")
    return {}

import socket # Import socket for hostname resolution

def resolve_hostname(ip):
    """Attempts to resolve an IP address to a hostname."""
    try:
        # gethostbyaddr returns a triple (hostname, aliaslist, ipaddrlist)
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, socket.timeout):
        return None

def run_stats_script():
    """
    Helper function to execute scripts/get_stats.py and return parsed JSON.
    Returns (data, error_message).
    """
    script_path = os.path.join(basedir, 'scripts', 'get_stats.py')
    if not os.path.exists(script_path):
        script_path = os.path.abspath(os.path.join(basedir, '..', 'scripts', 'get_stats.py'))
    
    if not os.path.exists(script_path):
        return None, f"Stats script not found at {script_path}"
    
    try:
        # We specify the full path to python3 to be safe
        result = subprocess.run(['python3', script_path], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return None, f"Script failed (code {result.returncode}): {result.stderr}"
        
        if not result.stdout.strip():
            return None, f"Empty output from stats script. Stderr: {result.stderr}"
        
        return json.loads(result.stdout), None
    except subprocess.TimeoutExpired:
        return None, "Stats script timed out"
    except Exception as e:
        return None, f"Exception running stats script: {str(e)}"

@app.route('/api/local_network_status')
def get_local_network_status():
    """
    Retrieves and returns network status information from the local machine quickly.
    Uses 'arp -a' which is near-instant as it reads the system cache.
    """
    devices = []
    device_names = load_device_names()
    try:
        if sys.platform.startswith('win'):
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
            output_lines = result.stdout.splitlines()
            arp_pattern_win = re.compile(r'\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*([0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2})\s*(dynamic|static)')

            for line in output_lines:
                match = arp_pattern_win.search(line)
                if match:
                    ip, mac_win, _type = match.groups()
                    mac = mac_win.replace('-', ':').upper()
                    devices.append({
                        'ip': ip, 
                        'mac': mac, 
                        'interface': 'arp cache',
                        'name': device_names.get(mac) # Removed slow resolve_hostname
                    })
        else: # Linux/Jetson
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
            output_lines = result.stdout.splitlines()
            arp_pattern_linux = re.compile(r'(\S+) \((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\) at ([0-9a-fA-F:]+) \[ether\] on (\w+)')

            for line in output_lines:
                match = arp_pattern_linux.search(line)
                if match:
                    hostname, ip, mac, interface = match.groups()
                    mac = mac.upper()
                    name = device_names.get(mac)
                    if not name and hostname != '?':
                        name = hostname
                    
                    devices.append({
                        'ip': ip, 
                        'mac': mac, 
                        'interface': interface,
                        'name': name # Removed slow resolve_hostname
                    })
            
            # Add self
            try:
                jetson_ip = subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout.split()[0]
                interfaces = os.listdir('/sys/class/net/')
                primary_iface = next((i for i in interfaces if i not in ['lo'] and not i.startswith(('br-', 'docker'))), 'eth0')
                jetson_mac = subprocess.run(['cat', f'/sys/class/net/{primary_iface}/address'], capture_output=True, text=True).stdout.strip().upper()
                devices.append({
                    'ip': jetson_ip, 
                    'mac': jetson_mac, 
                    'interface': f'self ({primary_iface})',
                    'name': device_names.get(jetson_mac, "Jetson Nano")
                })
            except: pass

        return jsonify(devices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/local_network_scan')
def get_local_network_scan():
    """
    Performs a deeper network scan using nmap or reverse DNS.
    """
    devices = []
    device_names = load_device_names()

    if sys.platform.startswith('win'):
        # On Windows, try reverse DNS for items in ARP cache as a "deep scan"
        try:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
            output_lines = result.stdout.splitlines()
            arp_pattern_win = re.compile(r'\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*([0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2})')

            for line in output_lines:
                match = arp_pattern_win.search(line)
                if match:
                    ip, mac_win = match.groups()
                    mac = mac_win.replace('-', ':').upper()
                    name = device_names.get(mac) or resolve_hostname(ip)
                    if name:
                        devices.append({'ip': ip, 'mac': mac, 'name': name, 'interface': 'dns lookup'})
            return jsonify(devices)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Linux/Jetson Nmap Scan
    try:
        result = subprocess.run(['nmap', '-sn', '192.168.1.0/24'], capture_output=True, text=True, timeout=15)
        nmap_output = result.stdout
        nmap_pattern = re.compile(r'Nmap scan report for ([^(\s]+)?\s*\(?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\)?.*?MAC Address: ([0-9a-fA-F:]+) \(([^)]+)\)', re.DOTALL)
        
        matches = nmap_pattern.findall(nmap_output)
        for hostname, ip, mac, vendor in matches:
            mac = mac.upper()
            name = device_names.get(mac)
            if not name:
                if hostname and hostname != '_gateway':
                    name = hostname
                elif vendor and vendor != 'Unknown':
                    name = vendor
            
            devices.append({
                'ip': ip,
                'mac': mac,
                'interface': 'nmap scan',
                'name': name
            })
        return jsonify(devices)
    except Exception as e:
        app_logger.error(f"Deep scan failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/remote_network_status')
def get_remote_network_status():
    if not MONITOR_TARGET_HOST:
        return jsonify({'error': 'MONITOR_TARGET_HOST is not set.'}), 400
    try:
        remote_url = f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/local_network_status"
        response = requests.get(remote_url, timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': f"Remote error: {e}"}), 500

@app.route('/api/remote_network_scan')
def get_remote_network_scan():
    if not MONITOR_TARGET_HOST:
        return jsonify({'error': 'MONITOR_TARGET_HOST is not set.'}), 400
    try:
        remote_url = f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/local_network_scan"
        response = requests.get(remote_url, timeout=20)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': f"Remote error: {e}"}), 500

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
    """
    if sys.platform.startswith('win'):
        if not MONITOR_TARGET_HOST:
            return jsonify({'error': 'MONITOR_TARGET_HOST is not set.'}), 400
        try:
            remote_url = f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/jetson_gpu_info"
            response = requests.get(remote_url)
            response.raise_for_status()
            return jsonify(response.json())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    try:
        raw_data, error = run_stats_script()
        if error:
            return jsonify({'error': error}), 500
        
        stats = raw_data.get('stats', {})
        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        
        response_data = {
            'gpu_usage_percent': stats.get('GPU', 0),
            'gpu_clock_mhz': stats.get('GR3D_FREQ', 0),
            'gpu_percent': stats.get('GPU', 0),
            'emc_percent': stats.get('EMC', 0),
            'gpu_temp_c': stats.get('Temp gpu', 0),
            'power_mw': stats.get('Power TOT', 0),
            'ram_usage_mb': round(stats.get('RAM', 0) * total_ram_gb * 1024, 2),
            'ram_total_mb': round(total_ram_gb * 1024, 2),
            'jtop_active': True,
            'raw_stats': stats
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hardware_sentinel')
def get_hardware_sentinel():
    """
    Aggregates thermal zones, fan status, and swap pressure for Hardware Sentinel.
    """
    if sys.platform.startswith('win'):
        if not MONITOR_TARGET_HOST:
            return jsonify({'error': 'MONITOR_TARGET_HOST is not set.'}), 400
        try:
            remote_url = f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/hardware_sentinel"
            response = requests.get(remote_url)
            response.raise_for_status()
            return jsonify(response.json())
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    try:
        raw_data, error = run_stats_script()
        if error:
            return jsonify({'error': error}), 500
        
        # Extract specific data for Sentinel
        stats = raw_data.get('stats', {})
        fan = raw_data.get('fan', {})
        clocks = raw_data.get('clocks', {})
        temp = raw_data.get('temperature', {})
        
        # Safety Logic: Auto-throttle if > 82°C
        # Extract numerical temp values from nested dicts: {"cpu": {"temp": 53.4, "online": True}}
        temp_values = [v['temp'] for v in temp.values() if isinstance(v, dict) and 'temp' in v]
        max_temp = max(temp_values) if temp_values else 0
        if max_temp > 82:
            app_logger.warning(f"CRITICAL TEMPERATURE DETECTED: {max_temp}°C. Triggering safety guardrails.")
            try:
                if JTOP_AVAILABLE:
                    with jtop() as jetson:
                        jetson.jetson_clocks = False
                        jetson.fan.profile = 'cool'
                else:
                    subprocess.run(['jetson_clocks', '--restore'], capture_output=True)
                    subprocess.run(['jtop', '--fan', 'cool'], capture_output=True)
            except Exception as e:
                app_logger.error(f"Failed to trigger safety guardrails: {e}")

        return jsonify({
            'thermals': temp,
            'fan': fan,
            'clocks': clocks,
            'swap': {
                'usage': stats.get('SWAP', 0),
                'total_gb': round(psutil.swap_memory().total / (1024**3), 2),
                'used_gb': round(psutil.swap_memory().used / (1024**3), 2)
            },
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hardware_sentinel/turbo', methods=['POST'])
def set_turbo_mode():
    """
    Toggles jetson_clocks (Turbo Mode).
    """
    if sys.platform.startswith('win'):
        if not MONITOR_TARGET_HOST:
            return jsonify({'error': 'MONITOR_TARGET_HOST is not set.'}), 400
        try:
            response = requests.post(f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/hardware_sentinel/turbo", json=request.json)
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    data = request.json
    enabled = data.get('enabled', False)
    try:
        if JTOP_AVAILABLE:
            with jtop() as jetson:
                jetson.jetson_clocks = enabled
        else:
            # Fallback to command line
            if enabled:
                subprocess.run(['jetson_clocks'], check=True)
            else:
                subprocess.run(['jetson_clocks', '--restore'], check=True)
        
        app_logger.info(f"Turbo Mode (jetson_clocks) set to: {enabled}")
        return jsonify({'status': 'success', 'enabled': enabled})
    except Exception as e:
        app_logger.error(f"Failed to set Turbo Mode: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/hardware_sentinel/fan', methods=['POST'])
def set_fan_mode():
    """
    Sets fan profiles (Quiet, Cool, Manual).
    """
    if sys.platform.startswith('win'):
        if not MONITOR_TARGET_HOST:
            return jsonify({'error': 'MONITOR_TARGET_HOST is not set.'}), 400
        try:
            response = requests.post(f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/hardware_sentinel/fan", json=request.json)
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    data = request.json
    mode = data.get('mode', 'quiet').lower()
    speed = data.get('speed', 50)

    try:
        if JTOP_AVAILABLE:
            with jtop() as jetson:
                if mode == 'manual':
                    jetson.fan.mode = 'manual'
                    jetson.fan.speed = speed
                else:
                    jetson.fan.profile = mode
        else:
            # Fallback to command line if available
            if mode == 'manual':
                subprocess.run(['jtop', '--fan', 'manual', 'speed', str(speed)], check=True)
            else:
                subprocess.run(['jtop', '--fan', mode], check=True)

        app_logger.info(f"Fan mode set to: {mode} (speed: {speed if mode == 'manual' else 'N/A'})")
        return jsonify({'status': 'success', 'mode': mode})
    except Exception as e:
        app_logger.error(f"Failed to set Fan mode: {e}")
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

@app.route('/api/docker_services', methods=['GET'])
def get_docker_services():
    """
    Returns a list of running Docker containers and their status.
    Active only on non-Windows (Jetson) hosts.
    """
    if sys.platform.startswith('win'):
        if not MONITOR_TARGET_HOST:
            return jsonify({'error': 'MONITOR_TARGET_HOST not set'}), 400
        try:
            response = requests.get(f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/docker_services")
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    if not DOCKER_AVAILABLE:
        return jsonify({'error': 'Docker integration not available in this container.'}), 500

    try:
        containers = docker_client.containers.list(all=True)
        # We only care about containers related to our project
        # We'll filter for common names or just show everything to be safe
        services = []
        for container in containers:
            services.append({
                'name': container.name,
                'status': container.status,
                'image': container.image.tags[0] if container.image.tags else 'unknown',
                'id': container.short_id
            })
        return jsonify(services)
    except Exception as e:
        app_logger.error(f"Error fetching docker services: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/docker_services/restart', methods=['POST'])
def restart_docker_service():
    """
    Restarts a specific Docker container by name.
    """
    data = request.json
    service_name = data.get('name')

    if not service_name:
        return jsonify({'error': 'Service name required'}), 400

    if sys.platform.startswith('win'):
        try:
            response = requests.post(f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/docker_services/restart", json={'name': service_name})
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    try:
        container = docker_client.containers.get(service_name)
        
        # Check if the container is restarting itself (the dashboard)
        # We look for 'dashboard' in the name or check if the container ID matches ours
        is_self_restart = 'dashboard' in service_name.lower() or 'web_monitor' in service_name.lower()

        if is_self_restart:
            import threading
            def delayed_restart():
                time.sleep(1) # Give Flask time to send the response
                container.restart()
            
            thread = threading.Thread(target=delayed_restart)
            thread.start()
            app_logger.info(f"Initiating self-restart for: {service_name}")
            return jsonify({'message': f"Dashboard service {service_name} is restarting. The connection will momentarily drop."})
        else:
            container.restart()
            app_logger.info(f"Restarted container: {service_name}")
            return jsonify({'message': f"Service {service_name} restarted successfully."})
            
    except Exception as e:
        app_logger.error(f"Failed to restart container {service_name}: {e}")
        return jsonify({'error': str(e)}), 500

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






@app.route('/api/power_mode', methods=['GET'])
def get_power_mode():
    """
    Returns the current NVPModel power mode and all available modes.
    On Windows, forwards the request to the Jetson.
    """
    if sys.platform.startswith('win'):
        if not MONITOR_TARGET_HOST:
            return jsonify({'error': 'MONITOR_TARGET_HOST is not set.'}), 400
        try:
            response = requests.get(f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/power_mode")
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    try:
        # Get current power mode
        result = subprocess.run(['nvpmodel', '-q'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return jsonify({'error': f'nvpmodel query failed: {result.stderr}'}), 500

        current_name = None
        current_id = None
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith('NV Power Mode:'):
                current_name = line.split(':', 1)[1].strip()
            elif line.isdigit():
                current_id = int(line)

        # Parse available modes from /etc/nvpmodel.conf
        modes = []
        conf_path = '/etc/nvpmodel.conf'
        if os.path.exists(conf_path):
            with open(conf_path, 'r') as f:
                for conf_line in f:
                    conf_line = conf_line.strip()
                    if conf_line.startswith('< POWER_MODEL'):
                        # Parse: < POWER_MODEL ID=0 NAME=15W >
                        id_match = re.search(r'ID=(\d+)', conf_line)
                        name_match = re.search(r'NAME=(\S+)', conf_line)
                        if id_match and name_match:
                            modes.append({
                                'id': int(id_match.group(1)),
                                'name': name_match.group(1)
                            })

        return jsonify({
            'current_id': current_id,
            'current_name': current_name,
            'modes': modes
        })
    except Exception as e:
        app_logger.error(f"Failed to get power mode: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/power_mode', methods=['POST'])
def set_power_mode():
    """
    Sets the NVPModel power mode.
    Expects JSON body: { "mode_id": <int> }
    """
    if sys.platform.startswith('win'):
        if not MONITOR_TARGET_HOST:
            return jsonify({'error': 'MONITOR_TARGET_HOST is not set.'}), 400
        try:
            response = requests.post(
                f"http://{MONITOR_TARGET_HOST}:{MONITOR_TARGET_PORT}/api/power_mode",
                json=request.json
            )
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    data = request.json
    mode_id = data.get('mode_id')

    if mode_id is None:
        return jsonify({'error': 'mode_id is required'}), 400

    try:
        # nvpmodel -m may prompt for reboot confirmation on certain modes,
        # which blocks on stdin. We pipe "no" to decline and detect from
        # stderr whether a reboot is required.
        result = subprocess.run(
            ['nvpmodel', '-m', str(mode_id)],
            capture_output=True, text=True, input='no\n', timeout=15
        )

        combined_output = (result.stdout + result.stderr).lower()
        if 'reboot required' in combined_output:
            app_logger.info(f"Power mode {mode_id} requires a system reboot.")
            return jsonify({
                'error': f'Mode {mode_id} requires a full system reboot to activate. Use the Hard Reboot button after switching.',
                'requires_reboot': True
            }), 409

        if result.returncode != 0:
            app_logger.error(f"nvpmodel set failed: {result.stderr}")
            return jsonify({'error': f'Failed to set power mode: {result.stderr}'}), 500

        # Verify the change
        verify = subprocess.run(['nvpmodel', '-q'], capture_output=True, text=True, timeout=5)
        new_name = None
        new_id = None
        for line in verify.stdout.splitlines():
            line = line.strip()
            if line.startswith('NV Power Mode:'):
                new_name = line.split(':', 1)[1].strip()
            elif line.isdigit():
                new_id = int(line)

        app_logger.info(f"Power mode changed to: {new_name} (ID: {new_id})")
        return jsonify({
            'message': f'Power mode set to {new_name}',
            'current_id': new_id,
            'current_name': new_name
        })
    except Exception as e:
        app_logger.error(f"Failed to set power mode: {e}")
        return jsonify({'error': str(e)}), 500


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