import { useState, useEffect } from 'react';
import { useConfig } from './useConfig'; // Assuming useConfig exists to get MONITOR_TARGET_HOST

interface GpuInfo {
  gpu_usage_percent: number | null;
  gpu_clock_mhz: number | null;
  gpu_percent: number | null; // Clock speed or usage as proxy
  emc_percent: number | null; // Memory Controller usage %
  gpu_temp_c: number | null; // GPU temperature in Celsius
  power_mw: number | null; // Power consumption in mW
  ram_usage_mb: number | null;
  ram_total_mb: number | null;
}

interface UseGpuInfoResult {
  gpuInfo: GpuInfo | null;
  loading: boolean;
  error: string | null;
}

export const useGpuInfo = (): UseGpuInfoResult => {
  const [gpuInfo, setGpuInfo] = useState<GpuInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { monitorTargetHost, monitorTargetPort, loading: configLoading, error: configError } = useConfig();

  useEffect(() => {
    if (configLoading) {
      return; // Wait for config to load
    }
    if (configError) {
      setError(`Configuration error: ${configError}`);
      setLoading(false);
      return;
    }

    const fetchGpuInfo = async () => {
      setLoading(true);
      setError(null);
      try {
        const url = monitorTargetHost 
          ? `http://${monitorTargetHost}:${monitorTargetPort}/api/jetson_gpu_info`
          : '/api/jetson_gpu_info'; // Assuming local if no remote host configured

        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setGpuInfo(data);
      } catch (e: any) {
        setError(`Failed to fetch GPU info: ${e.message}`);
        setGpuInfo(null);
      } finally {
        setLoading(false);
      }
    };

    fetchGpuInfo(); // Initial fetch

    const interval = setInterval(fetchGpuInfo, 5000); // Poll every 5 seconds

    return () => clearInterval(interval); // Cleanup on unmount
  }, [monitorTargetHost, monitorTargetPort, configLoading, configError]);

  return { gpuInfo, loading, error };
};
