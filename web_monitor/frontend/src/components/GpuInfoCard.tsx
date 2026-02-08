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
  // Only show the full loading state if we don't have data yet.
  // This prevents the card from "flashing" during refreshes.
  if (loading && !gpuInfo) {
    return (
      <Card className="min-h-[200px]">
        <CardHeader className="py-3 px-4">
          <CardTitle className="text-sm font-semibold">{title}</CardTitle>
        </CardHeader>
        <CardContent className="px-4 pb-4">
          <p className="text-xs text-muted-foreground">Loading GPU information...</p>
        </CardContent>
      </Card>
    );
  }

  if (error && !gpuInfo) {
    return (
      <Card className="min-h-[200px]">
        <CardHeader className="py-3 px-4">
          <CardTitle className="text-sm font-semibold">{title}</CardTitle>
        </CardHeader>
        <CardContent className="px-4 pb-4">
          <p className="text-xs text-destructive">Error: {error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!gpuInfo && !loading) {
    return (
      <Card className="min-h-[200px]">
        <CardHeader className="py-3 px-4">
          <CardTitle className="text-sm font-semibold">{title}</CardTitle>
        </CardHeader>
        <CardContent className="px-4 pb-4">
          <p className="text-xs text-muted-foreground">No GPU information available.</p>
        </CardContent>
      </Card>
    );
  }

  // Determine usage and clock with fallbacks
  const usage = gpuInfo ? (gpuInfo.gpu_usage_percent !== undefined ? gpuInfo.gpu_usage_percent : gpuInfo.gpu_percent) : null;
  const clock = gpuInfo ? gpuInfo.gpu_clock_mhz : null;

  return (
    <Card className="min-h-[200px] transition-all duration-300">
      <CardHeader className="py-3 px-4 flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-semibold">{title}</CardTitle>
        {loading && <span className="animate-pulse text-[10px] text-muted-foreground italic">Updating...</span>}
      </CardHeader>
      <CardContent className="px-4 pb-4 space-y-2">
        {/* GPU Usage */}
        {usage !== null && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-medium">
              <span>GPU Usage</span>
              <span>{usage}%</span>
            </div>
            <Progress value={usage} className="h-1.5" />
          </div>
        )}

        {/* GPU Clock */}
        {clock !== null && clock > 0 && (
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">GPU Clock</span>
            <span className="font-medium">{clock} MHz</span>
          </div>
        )}

        {/* EMC Usage */}
        {gpuInfo && gpuInfo.emc_percent !== null && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-medium">
              <span>Memory (EMC)</span>
              <span>{gpuInfo.emc_percent}%</span>
            </div>
            <Progress value={gpuInfo.emc_percent} className="h-1.5" />
          </div>
        )}

        {/* GPU Temperature */}
        {gpuInfo && gpuInfo.gpu_temp_c !== null && (
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Temperature</span>
            <span className="font-medium">{gpuInfo.gpu_temp_c}°C</span>
          </div>
        )}

        {/* Power Consumption */}
        {gpuInfo && gpuInfo.power_mw !== null && (
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Power</span>
            <span className="font-medium">{(gpuInfo.power_mw / 1000).toFixed(1)}W</span>
          </div>
        )}

        {/* GPU RAM Usage */}
        {gpuInfo && gpuInfo.ram_usage_mb !== null && gpuInfo.ram_total_mb !== null && (
          <div className="space-y-1">
            <div className="flex justify-between text-[11px] font-medium">
              <span>GPU RAM</span>
              <span>{gpuInfo.ram_usage_mb} / {gpuInfo.ram_total_mb}MB</span>
            </div>
            <Progress value={(gpuInfo.ram_usage_mb / gpuInfo.ram_total_mb) * 100} className="h-1.5" />
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default GpuInfoCard;
