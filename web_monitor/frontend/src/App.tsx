import React, { useState } from 'react';
import NetworkStatusCard from './components/NetworkStatusCard';
import SystemInfoCard from './components/SystemInfoCard';
import { useSystemInfo } from './hooks/useSystemInfo';
import { useNetworkStatus } from './hooks/useNetworkStatus';
import { useConfig } from './hooks/useConfig';
import FaviconChanger from './components/FaviconChanger';
import ChatCard from './components/ChatCard';
import { ThemeProvider } from './components/theme-provider'; // Import ThemeProvider
import './index.css';

// Import the SVG logos
import DesktopIcon from '/desktop_icon.svg'; 
import NvidiaLogo from '/nvidia_logo.svg';

function App() {
  const { local: localSystem, remote: remoteSystem } = useSystemInfo();
  const { local: localNetwork, remote: remoteNetwork } = useNetworkStatus();
  const { monitor_target_host_set, monitorTargetHost, loading: configLoading, error: configError } = useConfig();
  const [rebootMessage, setRebootMessage] = useState<string | null>(null);

  const isJetsonApp = !monitor_target_host_set;

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
      const response = await fetch(`http://${monitorTargetHost}:5000/api/command/reboot`, { method: 'POST' });
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
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <div className="min-h-screen bg-background text-foreground font-sans antialiased"> {/* Use theme classes */}
        <FaviconChanger isJetsonApp={isJetsonApp} configLoading={configLoading} />

        <header className="py-6 border-b border-border"> {/* Use theme classes */}
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
              <p className="text-center text-muted-foreground"> {/* Use theme classes */}
                {isJetsonApp ? "Monitor your Jetson." : "Monitor your local PC and a remote host."}
              </p>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          {configLoading && <p className="text-center">Loading configuration...</p>}
          {configError && <p className="text-center text-destructive">Error loading configuration: {configError}</p>} {/* Use theme classes */}
          
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
                    onRebootClick={handleReboot}
                  />
                  {rebootMessage && (
                    <p className={`text-center text-sm ${rebootMessage.includes("failed") ? "text-destructive" : "text-primary"} mt-2`}>
                      {rebootMessage}
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
          <section className="mt-8 p-4 border rounded-lg shadow-sm bg-card text-card-foreground"> {/* Use theme classes */}
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