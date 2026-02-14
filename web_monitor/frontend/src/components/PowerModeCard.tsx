import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';

interface PowerMode {
  id: number;
  name: string;
}

interface PowerModeCardProps {
  currentId: number | null;
  currentName: string | null;
  modes: PowerMode[];
  loading: boolean;
  error: string | null;
  switching: boolean;
  onSwitchMode: (modeId: number) => Promise<{ success: boolean; message: string }>;
  onToast: (message: string, isError: boolean) => void;
}

const PowerModeCard: React.FC<PowerModeCardProps> = ({
  currentId,
  currentName,
  modes,
  loading,
  error,
  switching,
  onSwitchMode,
  onToast,
}) => {
  const [pendingModeId, setPendingModeId] = useState<number | null>(null);

  const handleSwitch = async (modeId: number) => {
    const modeName = modes.find(m => m.id === modeId)?.name || `Mode ${modeId}`;
    if (!window.confirm(`Switch power mode to ${modeName}? This may affect system performance.`)) {
      return;
    }

    setPendingModeId(modeId);
    const result = await onSwitchMode(modeId);
    setPendingModeId(null);

    onToast(
      result.success ? `Power mode switched to ${modeName}` : `Failed: ${result.message}`,
      !result.success
    );
  };

  return (
    <Card className="col-span-1 min-h-[180px]">
      <CardHeader className="py-3 px-4 flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-semibold">Power Mode</CardTitle>
        {(loading || switching) && (
          <span className="animate-pulse text-[10px] text-muted-foreground italic">
            {switching ? 'Switching...' : 'Updating...'}
          </span>
        )}
      </CardHeader>
      <CardContent className="px-4 pb-4 space-y-3">
        {error && !currentName && (
          <p className="text-xs text-destructive">Error: {error}</p>
        )}
        {loading && !currentName && (
          <p className="text-xs text-muted-foreground">Loading power mode...</p>
        )}

        {currentName !== null && (
          <>
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground">Current Mode</span>
              <span className="font-semibold text-primary">{currentName}</span>
            </div>

            {modes.length > 0 && (
              <div className="space-y-1.5 pt-1">
                <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Available Modes</span>
                <div className="grid gap-1.5">
                  {modes.map((mode) => (
                    <Button
                      key={mode.id}
                      size="sm"
                      variant={mode.id === currentId ? 'default' : 'outline'}
                      className="h-7 text-[11px] justify-between px-3"
                      disabled={mode.id === currentId || switching}
                      onClick={() => handleSwitch(mode.id)}
                    >
                      <span>{mode.name}</span>
                      {mode.id === currentId && (
                        <span className="text-[9px] opacity-70">Active</span>
                      )}
                      {pendingModeId === mode.id && (
                        <span className="animate-spin text-[9px]">⏳</span>
                      )}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default PowerModeCard;
