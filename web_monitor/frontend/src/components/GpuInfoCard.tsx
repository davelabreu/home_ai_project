import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'; // Assuming these exist
import { Progress } from './ui/progress'; // Assuming this exists

interface GpuInfoProps {
  gpuInfo: {
    gpu_usage_percent: number | null;
    gpu_clock_mhz: number | null;
    gpu_percent: number | null; // Keep for fallback
    emc_percent: number | null;
    gpu_temp_c: number | null;
    power_mw: number | null;
    ram_usage_mb: number | null;
    ram_total_mb: number | null;
  } | null;
  loading: boolean;
  error: string | null;
  title: string;
}

const GpuInfoCard: React.FC<GpuInfoProps> = ({ gpuInfo, loading, error, title }) => {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Loading GPU information...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-destructive">Error: {error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!gpuInfo) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p>No GPU information available.</p>
        </CardContent>
      </Card>
    );
  }

  // Determine usage and clock with fallbacks
  const usage = gpuInfo.gpu_usage_percent !== undefined ? gpuInfo.gpu_usage_percent : gpuInfo.gpu_percent;
  const clock = gpuInfo.gpu_clock_mhz;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* GPU Usage */}
        {usage !== null && (
          <div>
            <div className="flex justify-between text-sm">
              <span>GPU Usage</span>
              <span>{usage}%</span>
            </div>
            <Progress value={usage} className="h-2" />
          </div>
        )}

        {/* GPU Clock */}
        {clock !== null && clock > 0 && (
          <div>
            <div className="flex justify-between text-sm">
              <span>GPU Clock</span>
              <span>{clock} MHz</span>
            </div>
          </div>
        )}

        {/* EMC Usage */}
        {gpuInfo.emc_percent !== null && (
          <div>
            <div className="flex justify-between text-sm">
              <span>Memory Controller (EMC)</span>
              <span>{gpuInfo.emc_percent}%</span>
            </div>
            <Progress value={gpuInfo.emc_percent} className="h-2" />
          </div>
        )}

        {/* GPU Temperature */}
        {gpuInfo.gpu_temp_c !== null && (
          <div>
            <div className="flex justify-between text-sm">
              <span>GPU Temperature</span>
              <span>{gpuInfo.gpu_temp_c}°C</span>
            </div>
          </div>
        )}

        {/* Power Consumption */}
        {gpuInfo.power_mw !== null && (
          <div>
            <div className="flex justify-between text-sm">
              <span>Power Consumption</span>
              <span>{(gpuInfo.power_mw / 1000).toFixed(2)} W</span>
            </div>
          </div>
        )}

        {/* GPU RAM Usage */}
        {gpuInfo.ram_usage_mb !== null && gpuInfo.ram_total_mb !== null && (
          <div>
            <div className="flex justify-between text-sm">
              <span>GPU RAM Usage</span>
              <span>{gpuInfo.ram_usage_mb}MB / {gpuInfo.ram_total_mb}MB</span>
            </div>
            <Progress value={(gpuInfo.ram_usage_mb / gpuInfo.ram_total_mb) * 100} className="h-2" />
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default GpuInfoCard;
