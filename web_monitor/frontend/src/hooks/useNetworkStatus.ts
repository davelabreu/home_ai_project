import { useState, useEffect } from 'react';
import { useConfig } from './useConfig'; // Import useConfig

interface NetworkDevice {
  ip: string;
  mac: string;
  interface: string;
  name?: string;
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
  const { monitorTargetHost, monitor_target_host_set, monitorTargetPort } = useConfig();

  useEffect(() => {
    const fetchFastStatus = async () => {
      // Local Fast
      try {
        const res = await fetch('/api/local_network_status');
        const data = await res.json();
        if (!data.error) setStatus(prev => ({ ...prev, local: { devices: data, error: null, loading: false } }));
      } catch (e: any) {
        setStatus(prev => ({ ...prev, local: { ...prev.local, error: e.message, loading: false } }));
      }

      // Remote Fast
      if (monitor_target_host_set && monitorTargetHost && monitorTargetPort) {
        try {
          const res = await fetch(`http://${monitorTargetHost}:${monitorTargetPort}/api/local_network_status`);
          const data = await res.json();
          if (!data.error) setStatus(prev => ({ ...prev, remote: { devices: data, error: null, loading: false } }));
        } catch (e: any) {
          setStatus(prev => ({ ...prev, remote: { ...prev.remote, error: e.message, loading: false } }));
        }
      } else {
        setStatus(prev => ({ ...prev, remote: { devices: [], error: "Not configured", loading: false } }));
      }
    };

    const fetchDeepScan = async () => {
      const mergeDevices = (prev: NetworkDevice[], deep: NetworkDevice[]) => {
        const merged = [...prev];
        deep.forEach(d => {
          const idx = merged.findIndex(m => m.mac === d.mac || m.ip === d.ip);
          if (idx !== -1) {
            merged[idx] = { ...merged[idx], ...d, interface: merged[idx].interface === 'arp cache' ? d.interface : merged[idx].interface };
          } else {
            merged.push(d);
          }
        });
        return merged;
      };

      // Local Deep
      try {
        const res = await fetch('/api/local_network_scan');
        const data = await res.json();
        if (Array.isArray(data)) {
          setStatus(prev => ({ ...prev, local: { ...prev.local, devices: mergeDevices(prev.local.devices, data) } }));
        }
      } catch (e) { /* ignore deep errors */ }

      // Remote Deep
      if (monitor_target_host_set && monitorTargetHost && monitorTargetPort) {
        try {
          const res = await fetch(`http://${monitorTargetHost}:${monitorTargetPort}/api/local_network_scan`);
          const data = await res.json();
          if (Array.isArray(data)) {
            setStatus(prev => ({ ...prev, remote: { ...prev.remote, devices: mergeDevices(prev.remote.devices, data) } }));
          }
        } catch (e) { /* ignore deep errors */ }
      }
    };

    const run = async () => {
      await fetchFastStatus();
      await fetchDeepScan();
    };

    run();
    const interval = setInterval(run, 60000); // Slower refresh for deep scans

    return () => clearInterval(interval);
  }, [monitorTargetHost, monitor_target_host_set, monitorTargetPort]);

  return status;
};
