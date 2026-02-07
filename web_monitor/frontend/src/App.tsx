import React, { useState } from 'react'; // Added useState
import NetworkStatusCard from './components/NetworkStatusCard';
import SystemInfoCard from './components/SystemInfoCard';
import { useSystemInfo } from './hooks/useSystemInfo'; // Import the updated hook
import { useNetworkStatus } from './hooks/useNetworkStatus'; // Import the updated hook
import { useConfig } from './hooks/useConfig'; // Import the new config hook
import FaviconChanger from './components/FaviconChanger'; // Import the new FaviconChanger component
import ChatCard from './components/ChatCard'; // Import the new ChatCard component
import './index.css'; // Tailwind CSS directives

// Import the SVG logos
import DesktopIcon from '/desktop_icon.svg'; 
import NvidiaLogo from '/nvidia_logo.svg';

function App() {
  const { local: localSystem, remote: remoteSystem } = useSystemInfo();
  const { local: localNetwork, remote: remoteNetwork } = useNetworkStatus();
  const { monitor_target_host_set, monitorTargetHost, loading: configLoading, error: configError } = useConfig(); // Destructure monitorTargetHost
  const [rebootMessage, setRebootMessage] = useState<string | null>(null);

  // Determine header content based on configuration
  const isJetsonApp = !monitor_target_host_set; // If MONITOR_TARGET_HOST is not set, this is the Jetson's local app

  const handleReboot = async () => {
    if (!window.confirm("Are you sure you want to reboot the remote host? This action cannot be undone.")) {
      return;
    }

    if (!monitorTargetHost) {
      setRebootMessage("Reboot failed: Remote host IP is not configured.");
      return;
    }

    setRebootMessage(`Attempting to reboot remote host (${monitorTargetHost})...`);
    try {
      const response = await fetch(`http://${monitorTargetHost}:5000/api/command/reboot`, { method: 'POST' }); // Use absolute URL
      const data = await response.json();

      if (response.ok) {
        setRebootMessage(`Reboot initiated: ${data.message}`);
      } else {
        setRebootMessage(`Reboot failed: ${data.message || response.statusText}`);
      }
    } catch (error: any) {
      setRebootMessage(`Reboot request failed: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-4">
      <FaviconChanger isJetsonApp={isJetsonApp} configLoading={configLoading} /> {/* Render FaviconChanger */}

      <header className="py-6 border-b border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4 flex items-center justify-center space-x-4">
          {isJetsonApp ? (
            <img src={NvidiaLogo} alt="Nvidia Logo" style={{ height: '3rem', width: 'auto' }} />
          ) : (
            <img src={DesktopIcon} alt="Desktop Icon" style={{ height: '3rem', width: 'auto' }} />
          )}
          <div>
            <h1 className="text-3xl font-bold text-center">
              {isJetsonApp ? "Jetson Dashboard" : "PC Dashboard"}
            </h1>
            <p className="text-center text-gray-600 dark:text-gray-400">
              {isJetsonApp ? "Monitor your Jetson." : "Monitor your local PC and a remote host."}
            </p>
          </div>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        {configLoading && <p className="text-center">Loading configuration...</p>}
        {configError && <p className="text-center text-red-500">Error loading configuration: {configError}</p>}
        
        {!configLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Local System Info */}
            <SystemInfoCard 
              title={isJetsonApp ? "Jetson System Status" : "Local PC System Status"} 
              systemInfo={localSystem.info} 
              error={localSystem.error} 
              loading={localSystem.loading} 
            />

            {/* Remote System Info (conditionally rendered) */}
            {monitor_target_host_set ? (
              <>
                <SystemInfoCard 
                  title="Remote Host System Status" 
                  systemInfo={remoteSystem.info} 
                  error={remoteSystem.error} 
                  loading={remoteSystem.loading} 
                  onRebootClick={handleReboot} // Pass the reboot handler
                />
                {rebootMessage && (
                  <p className={`text-center text-sm ${rebootMessage.includes("failed") ? "text-red-500" : "text-green-500"} mt-2`}>
                    {rebootMessage}
                  </p>
                )}
              </>
            ) : (
              // Only display 'Not Configured' message if we're on the PC app AND remote is not configured
              !remoteSystem.loading && remoteSystem.error && (
                <SystemInfoCard 
                  title="Remote Host System Status (Not Configured)" 
                  systemInfo={null} 
                  error={remoteSystem.error} 
                  loading={remoteSystem.loading} 
                />
              )
            )}
          </div>
        )}

        {!configLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Local Network Status */}
            <NetworkStatusCard 
              title={isJetsonApp ? "Jetson Network Devices" : "Local PC Network Devices"} 
              networkStatus={localNetwork.devices} 
              error={localNetwork.error} 
              loading={localNetwork.loading} 
            />

            {/* Remote Network Status (conditionally rendered) */}
            {monitor_target_host_set ? (
              <NetworkStatusCard 
                title="Remote Host Network Devices" 
                networkStatus={remoteNetwork.devices} 
                error={remoteNetwork.error} 
                loading={remoteNetwork.loading} 
              />
            ) : (
              // Only display 'Not Configured' message if we're on the PC app AND remote is not configured
              !remoteNetwork.loading && remoteNetwork.error && (
                <NetworkStatusCard 
                  title="Remote Host Network Devices (Not Configured)" 
                  networkStatus={[]} 
                  error={remoteNetwork.error} 
                  loading={remoteNetwork.loading} 
                />
              )
            )}
          </div>
        )}

        {/* Chat with Ollama */}
        {monitor_target_host_set && (
          <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
            <ChatCard />
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