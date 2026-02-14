import React, { useState } from 'react';
import { Button } from './components/ui/button';
import NetworkStatusCard from './components/NetworkStatusCard';
import SystemInfoCard from './components/SystemInfoCard';
import { useSystemInfo } from './hooks/useSystemInfo';
import { useNetworkStatus } from './hooks/useNetworkStatus';
import { useConfig } from './hooks/useConfig';
import FaviconChanger from './components/FaviconChanger';
import ChatCard from './components/ChatCard';
import GpuInfoCard from './components/GpuInfoCard'; // Import GpuInfoCard
import { useGpuInfo } from './hooks/useGpuInfo'; // Import useGpuInfo
import DockerServiceManager from './components/DockerServiceManager'; // Import DockerServiceManager
import PowerModeCard from './components/PowerModeCard';
import { usePowerMode } from './hooks/usePowerMode';
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
  const powerMode = usePowerMode();
  const [rebootMessage, setRebootMessage] = useState<string | null>(null);
  const [softRebootMessage, setSoftRebootMessage] = useState<string | null>(null); // New state for soft reboot message
  const [toastMessage, setToastMessage] = useState<{ text: string; isError: boolean } | null>(null);

  const isJetsonApp = !monitor_target_host_set;

  const handleToast = (text: string, isError: boolean) => {
    setToastMessage({ text, isError });
    setTimeout(() => setToastMessage(null), 5000);
  };

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

        <header className="py-4 border-b border-border">
          <div className="container mx-auto px-4 flex items-center justify-center space-x-3">
            {isJetsonApp ? (
              <img src={NvidiaLogo} alt="Nvidia Logo" style={{ height: '2rem', width: 'auto' }} />
            ) : (
              <img src={DesktopIcon} alt="Desktop Icon" style={{ height: '2rem', width: 'auto' }} />
            )}
            <div>
              <h1 className="text-xl font-bold tracking-tight">
                {isJetsonApp ? "Jetson Dashboard" : "PC Dashboard"}
              </h1>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-6 max-w-6xl">
          {configLoading && <p className="text-center text-sm italic">Loading configuration...</p>}
          {configError && <p className="text-center text-sm text-destructive">Error: {configError}</p>}
          
          {!configLoading && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {/* Local System Info */}
              <SystemInfoCard
                title={isJetsonApp ? "Local System" : "Local PC"}
                systemInfo={localSystem.info}
                error={localSystem.error}
                loading={localSystem.loading}
              />

              {/* Jetson Power Mode (local Jetson view) */}
              {isJetsonApp && (
                <PowerModeCard
                  currentId={powerMode.powerMode?.current_id ?? null}
                  currentName={powerMode.powerMode?.current_name ?? null}
                  modes={powerMode.powerMode?.modes ?? []}
                  loading={powerMode.loading}
                  error={powerMode.error}
                  switching={powerMode.switching}
                  onSwitchMode={powerMode.switchMode}
                  onToast={handleToast}
                />
              )}

              {/* Remote System Info & GPU Status */}
              {monitor_target_host_set && (
                <>
                  <SystemInfoCard
                    title="Remote Jetson"
                    systemInfo={remoteSystem.info}
                    error={remoteSystem.error}
                    loading={remoteSystem.loading}
                    onHardRebootClick={handleHardReboot}
                    onSoftRebootClick={handleSoftReboot}
                  />
                  <GpuInfoCard
                    title="Jetson GPU"
                    gpuInfo={gpu.gpuInfo}
                    error={gpu.error}
                    loading={gpu.loading}
                  />
                  <PowerModeCard
                    currentId={powerMode.powerMode?.current_id ?? null}
                    currentName={powerMode.powerMode?.current_name ?? null}
                    modes={powerMode.powerMode?.modes ?? []}
                    loading={powerMode.loading}
                    error={powerMode.error}
                    switching={powerMode.switching}
                    onSwitchMode={powerMode.switchMode}
                    onToast={handleToast}
                  />
                </>
              )}

              {/* Chat Card - Positioned in the grid */}
              {(isJetsonApp || monitor_target_host_set) && (
                <div className="md:col-span-2 lg:col-span-3">
                  <ChatCard />
                </div>
              )}

              {/* Network Cards */}
              <NetworkStatusCard 
                title={isJetsonApp ? "Local Network" : "PC Network"} 
                networkStatus={localNetwork.devices} 
                error={localNetwork.error} 
                loading={localNetwork.loading} 
              />

              {monitor_target_host_set && (
                <NetworkStatusCard 
                  title="Remote Network" 
                  networkStatus={remoteNetwork.devices} 
                  error={remoteNetwork.error} 
                  loading={remoteNetwork.loading} 
                />
              )}

              {/* Docker Service Manager */}
              {(isJetsonApp || monitor_target_host_set) && (
                <DockerServiceManager />
              )}
            </div>
          )}

          {rebootMessage && (
            <div className="fixed bottom-4 right-4 z-50 max-w-xs p-3 rounded-lg border bg-card shadow-lg text-xs transition-all animate-in fade-in slide-in-from-bottom-2">
              <p className={rebootMessage.includes("failed") ? "text-destructive" : "text-primary font-medium"}>
                {rebootMessage}
              </p>
              <Button size="sm" variant="ghost" className="h-6 mt-2 w-full text-[10px]" onClick={() => setRebootMessage(null)}>Dismiss</Button>
            </div>
          )}
          
          {softRebootMessage && (
            <div className="fixed bottom-4 right-4 z-50 max-w-xs p-3 rounded-lg border bg-card shadow-lg text-xs transition-all animate-in fade-in slide-in-from-bottom-2">
              <p className={softRebootMessage.includes("failed") ? "text-destructive" : "text-primary font-medium"}>
                {softRebootMessage}
              </p>
              <Button size="sm" variant="ghost" className="h-6 mt-2 w-full text-[10px]" onClick={() => setSoftRebootMessage(null)}>Dismiss</Button>
            </div>
          )}

          {toastMessage && (
            <div className="fixed bottom-4 right-4 z-50 max-w-xs p-3 rounded-lg border bg-card shadow-lg text-xs transition-all animate-in fade-in slide-in-from-bottom-2">
              <p className={toastMessage.isError ? "text-destructive" : "text-primary font-medium"}>
                {toastMessage.text}
              </p>
              <Button size="sm" variant="ghost" className="h-6 mt-2 w-full text-[10px]" onClick={() => setToastMessage(null)}>Dismiss</Button>
            </div>
          )}
        </main>
      </div>
    </ThemeProvider>
  );
}
export default App;