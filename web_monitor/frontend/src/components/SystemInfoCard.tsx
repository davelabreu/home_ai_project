import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'; // Assuming shadcn cards
import { Progress } from '@/components/ui/progress'; // Shadcn Progress component
import { Button } from '@/components/ui/button'; // Import Button component
import { SystemInfo } from '../hooks/useSystemInfo'; // Import the SystemInfo interface

interface SystemInfoCardProps {
  title: string;
  systemInfo: SystemInfo | null;
  error: string | null;
  loading: boolean;
  onRebootClick?: () => void; // Optional reboot action prop
}

const SystemInfoCard: React.FC<SystemInfoCardProps> = ({ title, systemInfo, error, loading, onRebootClick }) => {
  const getProgressColorClass = (value: number) => {
    if (value > 80) return 'bg-red-500';
    if (value > 50) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {loading && <p>Loading {title.toLowerCase()}...</p>}
        {error && <p className="text-red-500">Error fetching {title.toLowerCase()}: {error}</p>}
        {!loading && !error && systemInfo && (
          <>
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span>CPU Usage:</span>
                <span>{systemInfo.cpu_percent.toFixed(1)}%</span>
              </div>
              <Progress value={systemInfo.cpu_percent} className={getProgressColorClass(systemInfo.cpu_percent)} />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span>Memory Usage:</span>
                <span>{systemInfo.memory_percent.toFixed(1)}% ({systemInfo.memory_used_gb}GB / {systemInfo.memory_total_gb}GB)</span>
              </div>
              <Progress value={systemInfo.memory_percent} className={getProgressColorClass(systemInfo.memory_percent)} />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span>Disk Usage:</span>
                <span>{systemInfo.disk_percent.toFixed(1)}% ({systemInfo.disk_used_gb}GB / {systemInfo.disk_total_gb}GB)</span>
              </div>
              <Progress value={systemInfo.disk_percent} className={getProgressColorClass(systemInfo.disk_percent)} />
            </div>

            <div className="flex justify-between items-center text-sm">
              <span>Uptime:</span>
              <span className="font-medium">{systemInfo.uptime}</span>
            </div>
            {onRebootClick && (
              <div className="pt-4">
                <Button onClick={onRebootClick} disabled={loading || error !== null} className="w-full">
                  Reboot {title.includes("Remote Host") ? "Remote Host" : "System"}
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default SystemInfoCard;