import { useState, useEffect, useCallback } from 'react';

export interface HardwareSentinelData {
  thermals: Record<string, number>;
  fan: {
    speed: number;
    profile: string;
    mode: string;
  };
  clocks: boolean | string;
  swap: {
    usage: number;
    total_gb: number;
    used_gb: number;
  };
  timestamp: string;
}

export const useHardwareSentinel = () => {
  const [data, setData] = useState<HardwareSentinelData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/hardware_sentinel');
      if (!response.ok) throw new Error('Failed to fetch hardware sentinel data');
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleTurbo = async (enabled: boolean) => {
    try {
      const response = await fetch('/api/hardware_sentinel/turbo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled }),
      });
      if (!response.ok) throw new Error('Failed to toggle turbo mode');
      // Refresh data after update
      fetchData();
      return true;
    } catch (err: any) {
      setError(err.message);
      return false;
    }
  };

  const updateFan = async (mode: string, speed?: number) => {
    try {
      const response = await fetch('/api/hardware_sentinel/fan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode, speed }),
      });
      if (!response.ok) throw new Error('Failed to update fan settings');
      // Refresh data after update
      fetchData();
      return true;
    } catch (err: any) {
      setError(err.message);
      return false;
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return { data, loading, error, toggleTurbo, updateFan, refresh: fetchData };
};
