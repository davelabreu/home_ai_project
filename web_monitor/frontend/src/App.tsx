import React, { useState } from 'react';
import NetworkStatusCard from './components/NetworkStatusCard';
import SystemInfoCard from './components/SystemInfoCard';
import { useSystemInfo } from './hooks/useSystemInfo';
import { useNetworkStatus } from './hooks/useNetworkStatus';
import { useConfig } from './hooks/useConfig';
import FaviconChanger from './components/FaviconChanger';
import ChatCard from './components/ChatCard';
import GpuInfoCard from './components/GpuInfoCard'; // Import GpuInfoCard
import { useGpuInfo } from './hooks/useGpuInfo'; // Import useGpuInfo
import { ThemeProvider } from './components/theme-provider'; // Import ThemeProvider
import './index.css';

// Import the SVG logos
import DesktopIcon from '/desktop_icon.svg'; 
import NvidiaLogo from '/nvidia_logo.svg';

function App() {
  const { local: localSystem, remote: remoteSystem } = useSystemInfo();
  const { local: localNetwork, remote: remoteNetwork } = useNetworkStatus();
  const { monitor_target_host_set, monitorTargetHost, monitorTargetPort, loading: configLoading, error: configError } = useConfig();
  const gpu = useGpuInfo(); // Call the useGpuInfo hook
  const [rebootMessage, setRebootMessage] = useState<string | null>(null);
  const [softRebootMessage, setSoftRebootMessage] = useState<string | null>(null); // New state for soft reboot message

  const isJetsonApp = !monitor_target_host_set;

  const handleHardReboot = async () => {
    if (!window.confirm("Are you sure you want to perform a hard reboot on the remote host? This action will immediately power cycle the system.")) {
      return;
    }

    if (!monitorTargetHost || !monitorTargetPort) {
      setRebootMessage("Hard reboot failed: Remote host IP or port is not configured.");
      return;
    }

          setRebootMessage(`Attempting to hard reboot remote host (${monitorTargetHost}:${monitorTargetPort})...`);
        try {
          const response = await fetch(`http://${monitorTargetHost}:${monitorTargetPort}/api/command/reboot`, { 
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ type: 'hard' }),
          });
          const data = await response.json();
      if (response.ok) {
        setRebootMessage(`Hard reboot initiated: ${data.message}`);
      } else {
        setRebootMessage(`Hard reboot failed: ${data.message || response.statusText}`);
      }
    } catch (error: any) {
      setRebootMessage(`Hard reboot request failed: ${error.message}`);
    }
  };

  const handleSoftReboot = async () => {
    if (!window.confirm("Are you sure you want to perform a soft reboot (container restart) on the remote host? This will restart the Docker containers but not power cycle the system.")) {
      return;
    }

    if (!monitorTargetHost || !monitorTargetPort) {
      setSoftRebootMessage("Soft reboot failed: Remote host IP or port is not configured.");
      return;
    }

    setSoftRebootMessage(`Attempting to soft reboot remote host (${monitorTargetHost}:${monitorTargetPort})...`);
    try {
      const response = await fetch(`http://${monitorTargetHost}:${monitorTargetPort}/api/command/reboot`, { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type: 'soft' }),
      });
      const data = await response.json();

      if (response.ok) {
        setSoftRebootMessage(`Soft reboot initiated: ${data.message}`);
      } else {
        setSoftRebootMessage(`Soft reboot failed: ${data.message || response.statusText}`);
      }
    } catch (error: any) {
      setSoftRebootMessage(`Soft reboot request failed: ${error.message}`);
    }
  };

  return (
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <div className="min-h-screen bg-background text-foreground font-sans antialiased">
        <FaviconChanger isJetsonApp={isJetsonApp} configLoading={configLoading} />

        <header className="py-6 border-b border-border">
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
              <p className="text-center text-muted-foreground">
                {isJetsonApp ? "Monitor your Jetson." : "Monitor your local PC and a remote host."}
              </p>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          {configLoading && <p className="text-center">Loading configuration...</p>}
          {configError && <p className="text-center text-destructive">Error loading configuration: {configError}</p>}
          
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
                    onHardRebootClick={handleHardReboot} // Pass the new hard reboot handler
                    onSoftRebootClick={handleSoftReboot} // Pass the new soft reboot handler
                  />
                  <GpuInfoCard 
                    title="Jetson GPU Status" 
                    gpuInfo={gpu.gpuInfo} 
                    error={gpu.error} 
                    loading={gpu.loading} 
                  />
                  {rebootMessage && (
                    <p className={`text-center text-sm ${rebootMessage.includes("failed") ? "text-destructive" : "text-primary"} mt-2`}>
                      {rebootMessage}
                    </p>
                  )}
                  {softRebootMessage && ( // Display soft reboot message
                    <p className={`text-center text-sm ${softRebootMessage.includes("failed") ? "text-destructive" : "text-primary"} mt-2`}>
                      {softRebootMessage}
                    </p>
                  )}
                </>
              ) : (
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

          {/* Chat with Ollama - NEW POSITION */}
          {/* Always render ChatCard if it's the Jetson App OR if configured for remote monitoring */}
          {(isJetsonApp || monitor_target_host_set) && (
            <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
              <ChatCard />
            </div>
          )}

          {!configLoading && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8"> {/* Added mt-8 for spacing */}
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

          {/* Placeholder for future features */}
          <section className="mt-8 p-4 border rounded-lg shadow-sm bg-card text-card-foreground">
            <h2 className="text-xl font-semibold mb-4">Other Features (Coming Soon!)</h2>
            <p className="text-muted-foreground">
              Deployment tools, 
              Qwen chat interface...
            </p>
          </section>
        </main>
      </div>
    </ThemeProvider>
  );
}
export default App;