import { useState, useEffect } from 'react';

interface SystemInfo {
  cpu_percent: number;
  memory_percent: number;
  memory_total_gb: number;
  memory_used_gb: number;
  disk_percent: number;
  disk_total_gb: number;
  disk_used_gb: number;
  uptime: string;
}

interface DualSystemStatus {
  local: {
    info: SystemInfo | null;
    error: string | null;
    loading: boolean;
  };
  remote: {
    info: SystemInfo | null;
    error: string | null;
    loading: boolean;
  };
}

export const useSystemInfo = () => {
  const [status, setStatus] = useState<DualSystemStatus>({
    local: { info: null, error: null, loading: true },
    remote: { info: null, error: null, loading: true },
  });

  useEffect(() => {
    const fetchLocalInfo = async () => {
      try {
        const response = await fetch('/api/local_system_info');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.error) {
          setStatus((prev) => ({ ...prev, local: { info: null, error: data.error, loading: false } }));
        } else {
          setStatus((prev) => ({ ...prev, local: { info: data, error: null, loading: false } }));
        }
      } catch (e: any) {
        setStatus((prev) => ({ ...prev, local: { info: null, error: e.message, loading: false } }));
      }
    };

    const fetchRemoteInfo = async () => {
      try {
        const response = await fetch('/api/remote_system_info');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.error) {
          setStatus((prev) => ({ ...prev, remote: { info: null, error: data.error, loading: false } }));
        } else {
          setStatus((prev) => ({ ...prev, remote: { info: data, error: null, loading: false } }));
        }
      } catch (e: any) {
        setStatus((prev) => ({ ...prev, remote: { info: null, error: e.message, loading: false } }));
      }
    };

    fetchLocalInfo();
    fetchRemoteInfo();
    const interval = setInterval(() => {
      fetchLocalInfo();
      fetchRemoteInfo();
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return status;
};