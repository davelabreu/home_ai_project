import { useState, useEffect } from 'react';

interface SystemInfo {
  cpu_percent: number;
  memory_percent: number;
  memory_total_gb: number;
  memory_used_gb: number;
  disk_percent: number; // Added
  disk_total_gb: number; // Added
  disk_used_gb: number; // Added
  uptime: string; // Added
}

interface SystemStatus {
  info: SystemInfo | null;
  error: string | null;
  loading: boolean;
}

export const useSystemInfo = () => {
  const [status, setStatus] = useState<SystemStatus>({
    info: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const response = await fetch('/api/system_info');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.error) {
          setStatus({ info: null, error: data.error, loading: false });
        } else {
          setStatus({ info: data, error: null, loading: false });
        }
      } catch (e: any) {
        setStatus({ info: null, error: e.message, loading: false });
      }
    };

    fetchInfo();
    const interval = setInterval(fetchInfo, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return status;
};