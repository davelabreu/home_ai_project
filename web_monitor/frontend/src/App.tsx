import React from 'react';
import NetworkStatusCard from './components/NetworkStatusCard';
import SystemInfoCard from './components/SystemInfoCard';
import { useSystemInfo } from './hooks/useSystemInfo'; // Import the updated hook
import { useNetworkStatus } from './hooks/useNetworkStatus'; // Import the updated hook
import { useConfig } from './hooks/useConfig'; // Import the new config hook
import './index.css'; // Tailwind CSS directives

function App() {
  const { local: localSystem, remote: remoteSystem } = useSystemInfo();
  const { local: localNetwork, remote: remoteNetwork } = useNetworkStatus();
  const { monitor_target_host_set, loading: configLoading, error: configError } = useConfig();

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-4">
      <header className="py-6 border-b border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold text-center">Home AI Monitor Dashboard</h1>
          <p className="text-center text-gray-600 dark:text-gray-400">
            Monitor your local machine and, if configured, a remote host (e.g., Jetson).
          </p>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        {configLoading && <p className="text-center">Loading configuration...</p>}
        {configError && <p className="text-center text-red-500">Error loading configuration: {configError}</p>}
        
        {!configLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Local System Info */}
            <SystemInfoCard 
              title="Local Machine System Status" 
              systemInfo={localSystem.info} 
              error={localSystem.error} 
              loading={localSystem.loading} 
            />

            {/* Remote System Info (conditionally rendered) */}
            {monitor_target_host_set && (
              <SystemInfoCard 
                title="Remote Host System Status" 
                systemInfo={remoteSystem.info} 
                error={remoteSystem.error} 
                loading={remoteSystem.loading} 
              />
            )}
             {!monitor_target_host_set && remoteSystem.error && !remoteSystem.loading && (
              <SystemInfoCard 
                title="Remote Host System Status (Not Configured)" 
                systemInfo={null} 
                error={remoteSystem.error} 
                loading={remoteSystem.loading} 
              />
            )}
          </div>
        )}

        {!configLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Local Network Status */}
            <NetworkStatusCard 
              title="Local Machine Network Devices" 
              networkStatus={localNetwork.devices} 
              error={localNetwork.error} 
              loading={localNetwork.loading} 
            />

            {/* Remote Network Status (conditionally rendered) */}
            {monitor_target_host_set && (
              <NetworkStatusCard 
                title="Remote Host Network Devices" 
                networkStatus={remoteNetwork.devices} 
                error={remoteNetwork.error} 
                loading={remoteNetwork.loading} 
              />
            )}
            {!monitor_target_host_set && remoteNetwork.error && !remoteNetwork.loading && (
              <NetworkStatusCard 
                title="Remote Host Network Devices (Not Configured)" 
                networkStatus={[]} 
                error={remoteNetwork.error} 
                loading={remoteNetwork.loading} 
              />
            )}
          </div>
        )}

        {/* Placeholder for future features */}
        <section className="mt-8 p-4 border rounded-lg shadow-sm bg-white dark:bg-gray-800">
          <h2 className="text-xl font-semibold mb-4">Other Features (Coming Soon!)</h2>
          <p className="text-gray-600 dark:text-gray-400">
            {/* Deployment tools link to /api/deploy in Flask backend */}
            Deployment tools, 
            {/* Qwen chat interface links to scripts/ollama_chat.py */}
            Qwen chat interface...
          </p>
        </section>
      </main>
    </div>
  );
}

export default App;