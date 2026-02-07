import React from 'react';
import { useNetworkStatus } from '../hooks/useNetworkStatus';

const NetworkStatusCard: React.FC = () => {
  const { devices, error, loading } = useNetworkStatus();

  return (
    <div className="p-4 border rounded-lg shadow-sm bg-white dark:bg-gray-800">
      <h2 className="text-xl font-semibold mb-4 border-b pb-2">Local Network Devices</h2>
      {loading && <p>Loading network status...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}
      {!loading && !error && devices.length === 0 && (
        <p>No devices found in ARP cache.</p>
      )}
      {!loading && !error && devices.length > 0 && (
        <div className="space-y-2">
          {devices.map((device, index) => (
            <div key={index} className="flex justify-between items-center border-b last:border-b-0 py-1">
              <div>
                <p className="font-medium">{device.ip}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{device.mac}</p>
              </div>
              <p className="text-sm italic text-gray-600 dark:text-gray-300">on {device.interface}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NetworkStatusCard;
