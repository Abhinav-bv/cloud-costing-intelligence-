import React, { useState, useEffect } from 'react';
import KPICards from './components/KPICards';
import LiveChart from './components/LiveChart';
import ActionLog from './components/ActionLog';
import { Zap } from 'lucide-react';

const initialChartData = Array.from({ length: 10 }).map((_, i) => ({
  time: `T-${10 - i}`,
  cpu: Math.floor(Math.random() * 11) + 10, // fluctuating between 10% and 20%
}));

const initialLogs = [
  {
    id: 1,
    timestamp: '10:14:22 AM',
    resourceId: 'i-0abcd1234efgh5678',
    reason: 'Idle > 24h',
    action: 'Autonomously Stopped Instance'
  },
  {
    id: 2,
    timestamp: '09:42:05 AM',
    resourceId: 'vol-0987654321fedcba',
    reason: 'Unattached EBS Volume',
    action: 'Snapshot & Delete'
  }
];

function App() {
  const [systemStatus, setSystemStatus] = useState('🟢 HEALTHY');
  const [currentRunRate, setCurrentRunRate] = useState(0.12);
  const [totalSavings, setTotalSavings] = useState(14.40);
  const [chartData, setChartData] = useState(initialChartData);
  const [logs, setLogs] = useState(initialLogs);
  const [isSimulating, setIsSimulating] = useState(false);

  // Background fluctuation for chart when healthy
  useEffect(() => {
    if (systemStatus !== '🟢 HEALTHY') return;
    
    const interval = setInterval(() => {
      setChartData(prev => {
        const newData = [...prev.slice(1)];
        newData.push({
          time: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          cpu: Math.floor(Math.random() * 11) + 10 // 10% to 20%
        });
        return newData;
      });
    }, 2000);
    
    return () => clearInterval(interval);
  }, [systemStatus]);

  const handleSimulateChaos = () => {
    if (isSimulating) return;
    setIsSimulating(true);

    // 1. Spike CPU immediately
    setChartData(prev => [
      ...prev.slice(1),
      { time: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }), cpu: 98 }
    ]);
    
    // 2. Change status to ANOMALY DETECTED
    setSystemStatus('🔴 ANOMALY DETECTED');

    // 3. Wait 3 seconds, change to REMEDIATING...
    setTimeout(() => {
      setSystemStatus('🔵 REMEDIATING...');
      
      // Keep CPU randomly high during remediation
      setChartData(prev => [
        ...prev.slice(1),
        { time: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }), cpu: 95 }
      ]);
      
      // 4. Wait 2 seconds, Resolve to HEALTHY
      setTimeout(() => {
        // Drop CPU to 0%
        setChartData(prev => [
          ...prev.slice(1),
          { time: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }), cpu: 0 }
        ]);
        
        // Add action log row
        const newLog = {
          id: Date.now(),
          timestamp: new Date().toLocaleTimeString(),
          resourceId: 'i-chaos999spike00',
          reason: 'CPU Anomaly > 95%',
          action: 'Autonomously Stopped Instance'
        };
        setLogs(prev => [newLog, ...prev]);
        
        // Update Savings to 15.80
        setTotalSavings(15.80);
        
        // Status back to HEALTHY
        setSystemStatus('🟢 HEALTHY');
        setIsSimulating(false);
      }, 2000);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6 md:p-10 selection:bg-neon-green/30">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-6 gap-6">
          <div className="flex items-center gap-4">
            <div className="bg-[#39ff14]/10 p-3 rounded-xl border border-[#39ff14]/30 shadow-[0_0_15px_rgba(57,255,20,0.15)]">
              <Zap className="text-[#39ff14] w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                ⚡ FinOps Auto-Healer
              </h1>
              <p className="text-slate-400 text-sm mt-1 font-medium tracking-wide">Cloud Cost Intelligence & Autonomous Remediation</p>
            </div>
          </div>
          
          <button 
            onClick={handleSimulateChaos}
            disabled={isSimulating}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-bold tracking-wide transition-all duration-300 shadow-lg border ${
              isSimulating 
                ? 'bg-slate-800 text-slate-500 border-slate-700 cursor-not-allowed' 
                : 'bg-red-500/10 text-red-500 border-red-500/50 hover:bg-red-500 hover:text-white hover:shadow-[0_0_20px_rgba(255,7,58,0.5)] active:scale-95'
            }`}
          >
            <Zap className={`w-5 h-5 ${isSimulating ? '' : 'animate-pulse'}`} />
            {isSimulating ? 'SYSTEM BUSY...' : 'Simulate Chaos (Spike CPU)'}
          </button>
        </header>

        {/* Dashboard Content */}
        <main className="animate-in fade-in zoom-in-95 duration-500">
          <KPICards 
            systemStatus={systemStatus} 
            totalSavings={totalSavings} 
            currentRunRate={currentRunRate} 
          />
          <LiveChart data={chartData} />
          <ActionLog logs={logs} />
        </main>
      </div>
    </div>
  );
}

export default App;
