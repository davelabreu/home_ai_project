import { useState, useEffect } from 'react';
import { useConfig } from './useConfig'; // Import useConfig

interface NetworkDevice {
  ip: string;
  mac: string;
  interface: string;
}

interface DualNetworkStatus {
  local: {
    devices: NetworkDevice[];
    error: string | null;
    loading: boolean;
  };
  remote: {
    devices: NetworkDevice[];
    error: string | null;
    loading: boolean;
  };
}

export const useNetworkStatus = () => {
  const [status, setStatus] = useState<DualNetworkStatus>({
    local: { devices: [], error: null, loading: true },
    remote: { devices: [], error: null, loading: true },
  });
  const { monitorTargetHost, monitor_target_host_set } = useConfig(); // Get monitorTargetHost and set status

  useEffect(() => {
    const fetchLocalStatus = async () => {
      try {
        const response = await fetch('/api/local_network_status');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.error) {
          setStatus((prev) => ({ ...prev, local: { devices: [], error: data.error, loading: false } }));
        } else {
          setStatus((prev) => ({ ...prev, local: { devices: data, error: null, loading: false } }));
        }
      } catch (e: any) {
        setStatus((prev) => ({ ...prev, local: { devices: [], error: e.message, loading: false } }));
      }
    };

    const fetchRemoteStatus = async () => {
      if (!monitor_target_host_set || !monitorTargetHost) {
        setStatus((prev) => ({ ...prev, remote: { devices: [], error: "Remote host not configured.", loading: false } }));
        return;
      }
      try {
        const response = await fetch(`http://${monitorTargetHost}:5000/api/local_network_status`); // Use local_network_status on remote host, port 5000
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.error) {
          setStatus((prev) => ({ ...prev, remote: { devices: [], error: data.error, loading: false } }));
        } else {
          setStatus((prev) => ({ ...prev, remote: { devices: data, error: null, loading: false } }));
        }
      } catch (e: any) {
        setStatus((prev) => ({ ...prev, remote: { devices: [], error: e.message, loading: false } }));
      }
    };

    fetchLocalStatus();
    fetchRemoteStatus();
    const interval = setInterval(() => {
      fetchLocalStatus();
      fetchRemoteStatus();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [monitorTargetHost, monitor_target_host_set]); // Add monitorTargetHost to dependency array

  return status;
};
