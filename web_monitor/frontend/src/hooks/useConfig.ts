import { useState, useEffect } from 'react';

interface ConfigStatus {
  monitor_target_host_set: boolean;
  loading: boolean;
  error: string | null;
}

export const useConfig = () => {
  const [config, setConfig] = useState<ConfigStatus>({
    monitor_target_host_set: false,
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
          loading: false,
          error: null,
        });
      } catch (e: any) {
        setConfig({
          monitor_target_host_set: false, // Default to false on error
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
