import { useState, useEffect } from 'react';
import { useConfig } from './useConfig';

export interface DockerService {
  name: string;
  status: string;
  image: string;
  id: string;
}

export const useDockerServices = () => {
  const [services, setServices] = useState<DockerService[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { monitorTargetHost, monitorTargetPort, monitor_target_host_set, loading: configLoading } = useConfig();

  const fetchServices = async () => {
    if (configLoading) return;
    
    try {
      const baseUrl = monitor_target_host_set 
        ? `http://${monitorTargetHost}:${monitorTargetPort}` 
        : '';
      const response = await fetch(`${baseUrl}/api/docker_services`);
      if (!response.ok) throw new Error('Failed to fetch services');
      const data = await response.json();
      setServices(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const restartService = async (name: string) => {
    try {
      const baseUrl = monitor_target_host_set 
        ? `http://${monitorTargetHost}:${monitorTargetPort}` 
        : '';
      const response = await fetch(`${baseUrl}/api/docker_services/restart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      if (!response.ok) throw new Error('Failed to restart service');
      fetchServices(); // Refresh after restart
    } catch (err: any) {
      alert(`Restart failed: ${err.message}`);
    }
  };

  useEffect(() => {
    fetchServices();
    const interval = setInterval(fetchServices, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, [monitorTargetHost, monitorTargetPort, monitor_target_host_set, configLoading]);

  return { services, loading, error, restartService, refresh: fetchServices };
};
