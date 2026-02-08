import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { useDockerServices } from '../hooks/useDockerServices';
import { RefreshCw, Play, Square, RotateCcw } from 'lucide-react';

const DockerServiceManager: React.FC = () => {
  const { services, restartingServices, loading, error, restartService, refresh } = useDockerServices();
  const [feedback, setFeedback] = React.useState<string | null>(null);

  const getStatusColor = (status: string, isRestarting: boolean) => {
    if (isRestarting) return 'text-yellow-500';
    switch (status.toLowerCase()) {
      case 'running': return 'text-green-500';
      case 'exited': return 'text-red-500';
      case 'restarting': return 'text-yellow-500';
      default: return 'text-muted-foreground';
    }
  };

  const handleRestart = async (name: string) => {
    setFeedback(`Restarting ${name}...`);
    await restartService(name);
    // Feedback is cleared when restartingServices set is updated in the hook, 
    // but we can also clear it after a timeout if it's a self-restart
    if (name.includes('dashboard') || name.includes('web_monitor')) {
      setTimeout(() => setFeedback(null), 5000);
    } else {
      // For other services, the hook will eventually clear the pending state
      setTimeout(() => setFeedback(prev => prev === `Restarting ${name}...` ? null : prev), 10000);
    }
  };

  return (
    <Card className="h-full flex flex-col transition-all">
      <CardHeader className="py-3 px-4 flex flex-row items-center justify-between">
        <div className="space-y-0.5">
          <CardTitle className="text-sm font-semibold">Service Manager</CardTitle>
          {feedback && (
            <p className="text-[10px] text-primary animate-pulse font-medium">{feedback}</p>
          )}
        </div>
        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={refresh} disabled={loading}>
          <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
        </Button>
      </CardHeader>
      <CardContent className="px-4 pb-4 space-y-2 overflow-y-auto max-h-[300px]">
        {error && <p className="text-[10px] text-destructive">Error: {error}</p>}
        {services.length === 0 && !loading && (
          <p className="text-xs text-muted-foreground text-center py-4">No services found.</p>
        )}
        
        {services.map((service) => {
          const isRestarting = restartingServices.has(service.name);
          return (
            <div key={service.id} className="flex items-center justify-between p-2 rounded-md border border-border/50 bg-muted/30">
              <div className="space-y-0.5">
                <p className="text-xs font-bold truncate max-w-[120px]">{service.name}</p>
                <div className="flex items-center gap-1.5">
                  <span className={`w-1.5 h-1.5 rounded-full ${
                    isRestarting ? 'bg-yellow-500 animate-ping' : 
                    service.status === 'running' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className={`text-[10px] font-medium ${getStatusColor(service.status, isRestarting)}`}>
                    {isRestarting ? 'RESTARTING...' : service.status.toUpperCase()}
                  </span>
                </div>
              </div>
              
              <div className="flex gap-1">
                <Button 
                  variant="outline" 
                  size="icon" 
                  className="h-7 w-7" 
                  onClick={() => handleRestart(service.name)}
                  disabled={isRestarting}
                  title="Restart Service"
                >
                  {isRestarting ? (
                    <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <RotateCcw className="h-3.5 w-3.5" />
                  )}
                </Button>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
};

export default DockerServiceManager;
