import { useState, useEffect } from 'react';

interface ConfigStatus {
  monitor_target_host_set: boolean;
  monitorTargetHost: string | null; // Added to store the actual host
  monitorTargetPort: string | null; // New: To store the actual port
  loading: boolean;
  error: string | null;
}

export const useConfig = () => {
  const [config, setConfig] = useState<ConfigStatus>({
    monitor_target_host_set: false,
    monitorTargetHost: null, // Initialize as null
    monitorTargetPort: null, // Initialize as null
    loading: true,
    error: null,
  });

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch('/api/config');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setConfig({
          monitor_target_host_set: data.monitor_target_host_set,
          monitorTargetHost: data.monitor_target_host, // Store the actual host
          monitorTargetPort: data.monitor_target_port, // Store the actual port
          loading: false,
          error: null,
        });
      } catch (e: any) {
        setConfig({
          monitor_target_host_set: false, // Default to false on error
          monitorTargetHost: null, // Default to null on error
          monitorTargetPort: null, // Default to null on error
          loading: false,
          error: e.message,
        });
      }
    };

    fetchConfig();
    // Refresh config periodically in case environment variable changes
    const interval = setInterval(fetchConfig, 60000); // Check every minute

    return () => clearInterval(interval);
  }, []);

  return config;
};
