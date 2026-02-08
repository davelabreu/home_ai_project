import React from 'react';
import { NetworkDevice } from '../hooks/useNetworkStatus'; // Import NetworkDevice interface

interface NetworkStatusCardProps {
  title: string;
  networkStatus: NetworkDevice[];
  error: string | null;
  loading: boolean;
}

const NetworkStatusCard: React.FC<NetworkStatusCardProps> = ({ title, networkStatus, error, loading }) => {
  return (
    <div className="p-4 border rounded-lg shadow-sm bg-card text-card-foreground min-h-[150px]">
      <div className="flex justify-between items-center mb-3 border-b pb-2">
        <h2 className="text-sm font-semibold">{title}</h2>
        {loading && <span className="animate-pulse text-[10px] text-muted-foreground italic">Updating...</span>}
      </div>
      
      {error && !networkStatus.length && (
        <p className="text-xs text-destructive">Error: {error}</p>
      )}
      
      {!loading && !error && networkStatus.length === 0 && (
        <p className="text-xs text-muted-foreground">No devices found in ARP cache.</p>
      )}
      
      {networkStatus.length > 0 && (
        <div className="space-y-1.5 max-h-[200px] overflow-y-auto pr-1">
          {networkStatus.map((device, index) => (
            <div key={index} className="flex justify-between items-start border-b border-border/50 last:border-0 py-1.5">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <p className="text-xs font-semibold leading-none">{device.name || device.ip}</p>
                  {device.name && <p className="text-[10px] text-muted-foreground italic">({device.ip})</p>}
                </div>
                <p className="text-[10px] text-muted-foreground font-mono">{device.mac}</p>
              </div>
              <p className="text-[10px] italic text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                {device.interface}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NetworkStatusCard;
