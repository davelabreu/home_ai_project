import { useState, useEffect, useCallback } from 'react';
import { useConfig } from './useConfig';

interface PowerMode {
  id: number;
  name: string;
}

interface PowerModeState {
  current_id: number | null;
  current_name: string | null;
  modes: PowerMode[];
}

interface UsePowerModeResult {
  powerMode: PowerModeState | null;
  loading: boolean;
  error: string | null;
  switching: boolean;
  switchMode: (modeId: number) => Promise<{ success: boolean; message: string }>;
}

export const usePowerMode = (): UsePowerModeResult => {
  const [powerMode, setPowerMode] = useState<PowerModeState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [switching, setSwitching] = useState<boolean>(false);
  const { monitorTargetHost, monitorTargetPort, loading: configLoading, error: configError } = useConfig();

  const fetchPowerMode = useCallback(async () => {
    try {
      const url = monitorTargetHost
        ? `http://${monitorTargetHost}:${monitorTargetPort}/api/power_mode`
        : '/api/power_mode';

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      setPowerMode(data);
      setError(null);
    } catch (e: any) {
      setError(`Failed to fetch power mode: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }, [monitorTargetHost, monitorTargetPort]);

  useEffect(() => {
    if (configLoading) return;
    if (configError) {
      setError(`Configuration error: ${configError}`);
      setLoading(false);
      return;
    }

    fetchPowerMode();
    const interval = setInterval(fetchPowerMode, 30000); // Poll every 30s (mode rarely changes)
    return () => clearInterval(interval);
  }, [configLoading, configError, fetchPowerMode]);

  const switchMode = useCallback(async (modeId: number): Promise<{ success: boolean; message: string }> => {
    setSwitching(true);
    try {
      const url = monitorTargetHost
        ? `http://${monitorTargetHost}:${monitorTargetPort}/api/power_mode`
        : '/api/power_mode';

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode_id: modeId }),
      });
      const data = await response.json();

      if (!response.ok) {
        return { success: false, message: data.error || 'Failed to set power mode' };
      }

      // Refresh current state
      await fetchPowerMode();
      return { success: true, message: data.message };
    } catch (e: any) {
      return { success: false, message: e.message };
    } finally {
      setSwitching(false);
    }
  }, [monitorTargetHost, monitorTargetPort, fetchPowerMode]);

  return { powerMode, loading, error, switching, switchMode };
};
