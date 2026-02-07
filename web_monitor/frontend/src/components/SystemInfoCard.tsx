import React from 'react';
import { useSystemInfo } from '../hooks/useSystemInfo';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'; // Assuming shadcn cards
import { Progress } from '@/components/ui/progress'; // Shadcn Progress component

const SystemInfoCard: React.FC = () => {
  const { info, error, loading } = useSystemInfo();

  const getProgressColorClass = (value: number) => {
    if (value > 80) return 'bg-red-500';
    if (value > 50) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Jetson System Status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {loading && <p>Loading system info...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}
        {!loading && !error && info && (
          <>
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span>CPU Usage:</span>
                <span>{info.cpu_percent.toFixed(1)}%</span>
              </div>
              <Progress value={info.cpu_percent} className={getProgressColorClass(info.cpu_percent)} />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span>Memory Usage:</span>
                <span>{info.memory_percent.toFixed(1)}% ({info.memory_used_gb}GB / {info.memory_total_gb}GB)</span>
              </div>
              <Progress value={info.memory_percent} className={getProgressColorClass(info.memory_percent)} />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span>Disk Usage:</span>
                <span>{info.disk_percent.toFixed(1)}% ({info.disk_used_gb}GB / {info.disk_total_gb}GB)</span>
              </div>
              <Progress value={info.disk_percent} className={getProgressColorClass(info.disk_percent)} />
            </div>

            <div className="flex justify-between items-center text-sm">
              <span>Uptime:</span>
              <span className="font-medium">{info.uptime}</span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default SystemInfoCard;