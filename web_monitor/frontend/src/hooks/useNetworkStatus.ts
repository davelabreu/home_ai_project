import { useState, useEffect } from 'react';

interface NetworkDevice {
  ip: string;
  mac: string;
  interface: string;
}

interface NetworkStatus {
  devices: NetworkDevice[];
  error: string | null;
  loading: boolean;
}

export const useNetworkStatus = () => {
  const [status, setStatus] = useState<NetworkStatus>({
    devices: [],
    error: null,
    loading: true,
  });

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/network_status');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.error) {
          setStatus({ devices: [], error: data.error, loading: false });
        } else {
          setStatus({ devices: data, error: null, loading: false });
        }
      } catch (e: any) {
        setStatus({ devices: [], error: e.message, loading: false });
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return status;
};
