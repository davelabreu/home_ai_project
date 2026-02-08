import { useState, useEffect, useRef } from 'react';
import { useConfig } from './useConfig';

export interface DockerService {
  name: string;
  status: string;
  image: string;
  id: string;
}

export const useDockerServices = () => {
  const [services, setServices] = useState<DockerService[]>([]);
  const [restartingServices, setRestartingServices] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { monitorTargetHost, monitorTargetPort, monitor_target_host_set, loading: configLoading } = useConfig();
  
  // Ref to track services we are waiting for, to avoid closure issues in setInterval
  const pendingRestartsRef = useRef<Set<string>>(new Set());

  const fetchServices = async () => {
    if (configLoading) return;
    
    try {
      const baseUrl = monitor_target_host_set 
        ? `http://${monitorTargetHost}:${monitorTargetPort}` 
        : '';
      const response = await fetch(`${baseUrl}/api/docker_services`);
      if (!response.ok) throw new Error('Failed to fetch services');
      const data: DockerService[] = await response.json();
      
      // Update our restarting set: if a service we were waiting for is now 'running', remove it
      const newRestarting = new Set(pendingRestartsRef.current);
      data.forEach(service => {
        if (service.status.toLowerCase() === 'running' && newRestarting.has(service.name)) {
          newRestarting.delete(service.name);
        }
      });
      
      if (newRestarting.size !== pendingRestartsRef.current.size) {
        pendingRestartsRef.current = newRestarting;
        setRestartingServices(new Set(newRestarting));
      }

      setServices(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const restartService = async (name: string) => {
    // Add to restarting set immediately
    const newRestarting = new Set(pendingRestartsRef.current);
    newRestarting.add(name);
    pendingRestartsRef.current = newRestarting;
    setRestartingServices(new Set(newRestarting));

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
      
      // Don't fetch immediately, wait for the poll to pick up the status change
    } catch (err: any) {
      if (name.includes('dashboard') || name.includes('web_monitor')) {
        console.log("Self-restart initiated, ignoring fetch error.");
        return;
      }
      // On error, remove from restarting set
      const newRestarting = new Set(pendingRestartsRef.current);
      newRestarting.delete(name);
      pendingRestartsRef.current = newRestarting;
      setRestartingServices(new Set(newRestarting));
      alert(`Restart failed: ${err.message}`);
    }
  };

  useEffect(() => {
    fetchServices();
    const interval = setInterval(fetchServices, 3000); // Poll more frequently (3s) when managing services
    return () => clearInterval(interval);
  }, [monitorTargetHost, monitorTargetPort, monitor_target_host_set, configLoading]);

  return { services, restartingServices, loading, error, restartService, refresh: fetchServices };
};
