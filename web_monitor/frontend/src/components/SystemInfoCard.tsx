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
  onHardRebootClick?: () => void; // Optional hard reboot action prop
  onSoftRebootClick?: () => void; // Optional soft reboot action prop
}

const SystemInfoCard: React.FC<SystemInfoCardProps> = ({ title, systemInfo, error, loading, onHardRebootClick, onSoftRebootClick }) => {
  const getProgressColorClass = (value: number) => {
    if (value > 80) return 'bg-red-500';
    if (value > 50) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <Card className="col-span-1 min-h-[220px]">
      <CardHeader className="py-3 px-4 flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-semibold">{title}</CardTitle>
        {loading && <span className="animate-pulse text-[10px] text-muted-foreground italic">Updating...</span>}
      </CardHeader>
      <CardContent className="px-4 pb-4 space-y-3">
        {error && !systemInfo && <p className="text-xs text-red-500">Error: {error}</p>}
        {loading && !systemInfo && <p className="text-xs text-muted-foreground">Loading status...</p>}
        
        {systemInfo && (
          <>
            <div className="space-y-1">
              <div className="flex justify-between items-center text-xs font-medium">
                <span>CPU Usage</span>
                <span>{systemInfo.cpu_percent.toFixed(1)}%</span>
              </div>
              <Progress value={systemInfo.cpu_percent} className={`h-1.5 ${getProgressColorClass(systemInfo.cpu_percent)}`} />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between items-center text-xs font-medium">
                <span>Memory</span>
                <span className="text-[10px] text-muted-foreground">{systemInfo.memory_used_gb} / {systemInfo.memory_total_gb}GB</span>
              </div>
              <Progress value={systemInfo.memory_percent} className={`h-1.5 ${getProgressColorClass(systemInfo.memory_percent)}`} />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between items-center text-xs font-medium">
                <span>Disk</span>
                <span className="text-[10px] text-muted-foreground">{systemInfo.disk_used_gb} / {systemInfo.disk_total_gb}GB</span>
              </div>
              <Progress value={systemInfo.disk_percent} className={`h-1.5 ${getProgressColorClass(systemInfo.disk_percent)}`} />
            </div>

            <div className="flex justify-between items-center text-xs pt-1">
              <span className="text-muted-foreground">Uptime</span>
              <span className="font-semibold">{systemInfo.uptime}</span>
            </div>

            {(onHardRebootClick || onSoftRebootClick) && (
              <div className="pt-2 flex gap-2">
                {onHardRebootClick && (
                  <Button 
                    onClick={onHardRebootClick} 
                    disabled={loading} 
                    size="sm"
                    variant="destructive"
                    className="flex-1 h-7 text-[10px] px-2"
                  >
                    Hard Reboot
                  </Button>
                )}
                {onSoftRebootClick && (
                  <Button 
                    onClick={onSoftRebootClick} 
                    disabled={loading} 
                    size="sm"
                    className="flex-1 h-7 text-[10px] px-2"
                  >
                    Soft Reboot
                  </Button>
                )}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default SystemInfoCard;