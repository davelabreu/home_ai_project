import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { useHardwareSentinel } from '../hooks/useHardwareSentinel';
import { Thermometer, Wind, Zap, Database, AlertTriangle } from 'lucide-react';

const HardwareSentinelCard: React.FC = () => {
  const { data, loading, error, toggleTurbo, updateFan } = useHardwareSentinel();
  const [localTurbo, setLocalTurbo] = useState<boolean>(false);
  const [localFanMode, setLocalFanMode] = useState<string>('quiet');
  const [localFanSpeed, setLocalFanSpeed] = useState<number>(50);

  useEffect(() => {
    if (data) {
      setLocalTurbo(data.clocks === true || data.clocks === 'running');
      setLocalFanMode(data.fan.profile || data.fan.mode);
      setLocalFanSpeed(data.fan.speed);
    }
  }, [data]);

  if (loading && !data) {
    return (
      <Card className="min-h-[300px] flex items-center justify-center">
        <p className="text-sm text-muted-foreground animate-pulse">Initializing Hardware Sentinel...</p>
      </Card>
    );
  }

  if (error && !data) {
    return (
      <Card className="min-h-[300px] flex items-center justify-center">
        <p className="text-sm text-destructive font-medium">Error: {error}</p>
      </Card>
    );
  }

  const getTempColor = (temp: number) => {
    if (temp < 45) return 'text-blue-400';
    if (temp < 75) return 'text-orange-400';
    return 'text-red-500 font-bold';
  };

  const getTempBg = (temp: number) => {
    if (temp < 45) return 'bg-blue-500/10 border-blue-500/20';
    if (temp < 75) return 'bg-orange-500/10 border-orange-500/20';
    return 'bg-red-500/20 border-red-500/40';
  };

  const maxTemp = data ? Math.max(...Object.values(data.thermals).map((v: any) => v.temp)) : 0;
  const isDangerous = maxTemp > 75;
  const isCritical = maxTemp > 82;

  const handleTurboToggle = async () => {
    const newState = !localTurbo;
    setLocalTurbo(newState); // Optimistic UI
    const success = await toggleTurbo(newState);
    if (!success) setLocalTurbo(!newState); // Rollback
  };

  const handleFanChange = async (mode: string) => {
    setLocalFanMode(mode);
    await updateFan(mode, mode === 'manual' ? localFanSpeed : undefined);
  };

  // Helper to extract nested temp value
  const getTemp = (val: any) => (typeof val === 'object' ? val.temp : val);

  return (
    <Card className={`min-h-[400px] transition-all duration-500 ${isCritical ? 'border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]' : ''}`}>
      <CardHeader className="py-3 px-4 flex flex-row items-center justify-between border-b bg-muted/30">
        <div className="flex items-center gap-2">
          <Zap className={`h-4 w-4 ${localTurbo ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground'}`} />
          <CardTitle className="text-sm font-bold uppercase tracking-wider">Hardware Sentinel</CardTitle>
        </div>
        {isDangerous && (
          <div className="flex items-center gap-1 text-red-500 animate-bounce">
            <AlertTriangle className="h-4 w-4" />
            <span className="text-[10px] font-bold">THERMAL WARNING</span>
          </div>
        )}
      </CardHeader>

      <CardContent className="p-4 space-y-6">
        {/* Thermal Grid */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground mb-1">
            <Thermometer className="h-3 w-3" />
            <span>THERMAL ZONES</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {data && Object.entries(data.thermals).map(([zone, val]) => {
              const temp = getTemp(val);
              return (
                <div key={zone} className={`flex flex-col p-2 rounded border transition-colors ${getTempBg(temp)}`}>
                  <span className="text-[10px] uppercase text-muted-foreground font-medium">{zone}</span>
                  <span className={`text-sm font-mono ${getTempColor(temp)}`}>{temp.toFixed(1)}°C</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Control Section */}
        <div className="grid grid-cols-2 gap-4">
          {/* Turbo Mode */}
          <div className="space-y-2">
            <div className="text-[10px] font-bold text-muted-foreground uppercase">Performance</div>
            <button
              onClick={handleTurboToggle}
              disabled={isCritical}
              className={`w-full py-2 px-3 rounded text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                localTurbo 
                  ? 'bg-yellow-500 text-black hover:bg-yellow-400' 
                  : 'bg-muted hover:bg-muted/80 text-muted-foreground'
              } ${isCritical ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <Zap className="h-3 w-3" />
              {localTurbo ? 'TURBO ON' : 'TURBO OFF'}
            </button>
          </div>

          {/* Fan Profiles */}
          <div className="space-y-2">
            <div className="text-[10px] font-bold text-muted-foreground uppercase">Fan Profile</div>
            <div className="flex gap-1">
              {['quiet', 'cool', 'manual'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => handleFanChange(mode)}
                  className={`flex-1 py-1 px-1 rounded text-[9px] font-bold uppercase transition-all ${
                    localFanMode === mode 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-muted text-muted-foreground hover:bg-muted/80'
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Fan Manual Slider */}
        {localFanMode === 'manual' && (
          <div className="space-y-2 animate-in slide-in-from-top-2 duration-300">
            <div className="flex justify-between text-[10px] font-bold uppercase text-muted-foreground">
              <span>Manual Speed</span>
              <span>{localFanSpeed}%</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={localFanSpeed} 
              onChange={(e) => setLocalFanSpeed(parseInt(e.target.value))}
              onMouseUp={() => handleFanChange('manual')}
              className="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>
        )}

        {/* Swap usage */}
        {data && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-muted-foreground">
              <div className="flex items-center gap-2">
                <Database className="h-3 w-3" />
                <span>SWAP PRESSURE</span>
              </div>
              <span className={data.swap.usage > 50 ? 'text-orange-400' : ''}>
                {data.swap.used_gb} / {data.swap.total_gb} GB
              </span>
            </div>
            <Progress value={data.swap.usage} className="h-1.5" />
            <div className="flex justify-between text-[10px] text-muted-foreground italic">
              <span>NVMe Endurance: Stable</span>
              <span>{data.swap.usage.toFixed(1)}% Active</span>
            </div>
          </div>
        )}

        {/* Safety Interlock Message */}
        {isCritical && (
          <div className="p-2 rounded bg-red-500/20 border border-red-500/50 text-red-500 text-[11px] font-bold flex gap-2 items-start">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <p>CRITICAL TEMPERATURE DETECTED. Turbo mode disabled. Cooling forced to maximum profile. System safety interlock active.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default HardwareSentinelCard;
