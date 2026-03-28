import React, { useState, useEffect } from 'react';
import KPICards from './components/KPICards';
import LiveChart from './components/LiveChart';
import NodeMap from './components/NodeMap';
import Terminal from './components/Terminal';
import ActionLog from './components/ActionLog';
import { Zap, RefreshCw } from 'lucide-react';

const initialChartData = Array.from({ length: 15 }).map((_, i) => ({
  time: `T-${15 - i}`,
  actualCost: Math.random() * 2 + 10,
  projectedCost: Math.random() * 2 + 10,
}));

const initialLogs = [
  {
    id: 1,
    timestamp: new Date(Date.now() - 3600000).toLocaleTimeString(),
    resourceId: 'i-0abcd1234efgh5678',
    reason: 'Idle > 24h',
    action: 'Autonomously Stopped Instance'
  }
];

function App() {
  const [status, setStatus] = useState('HEALTHY'); // 'HEALTHY', 'ANOMALY', 'REMEDIATING'
  const [savings, setSavings] = useState(14.40);
  const [chartData, setChartData] = useState(initialChartData);
  const [logs, setLogs] = useState(initialLogs);
  const [isSimulating, setIsSimulating] = useState(false);
  const [offlineNodes, setOfflineNodes] = useState([]);
  const [activeAnomalyNode, setActiveAnomalyNode] = useState(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Background fluctuation for chart when healthy
  useEffect(() => {
    if (status !== 'HEALTHY') return;

    const interval = setInterval(() => {
      setChartData(prev => {
        const newData = [...prev.slice(1)];
        const activeCount = 8 - offlineNodes.length;
        // Scale cost directly proportional to active nodes (0 nodes = $0.00/hr)
        const baseCost = activeCount === 0 ? 0 : (activeCount * 1.2) + Math.random();
        
        newData.push({
          time: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          actualCost: baseCost,
          projectedCost: activeCount === 0 ? 0 : baseCost + Math.random() * 0.5
        });
        return newData;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [status, offlineNodes.length]);

  const simulateChaos = () => {
    if (isSimulating) return;

    const availableNodes = [0, 1, 2, 3, 4, 5, 6, 7].filter(n => !offlineNodes.includes(n));
    if (availableNodes.length === 0) {
      alert("All nodes have been shut down! Refresh to reset.");
      return;
    }
    const targetNode = availableNodes[Math.floor(Math.random() * availableNodes.length)];
    setActiveAnomalyNode(targetNode);
    setIsSimulating(true);

    const getTime = () => new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });

    // T=0s: status 'ANOMALY', spike actual and projected to $85
    setStatus('ANOMALY');
    setChartData(prev => [
      ...prev.slice(1),
      { time: getTime(), actualCost: 85, projectedCost: 85 }
    ]);

    // T=3s: status 'REMEDIATING'
    setTimeout(() => {
      setStatus('REMEDIATING');
      setChartData(prev => [
        ...prev.slice(1),
        { time: getTime(), actualCost: 80, projectedCost: 88 }
      ]);

      // T=5s: status 'HEALTHY', drop actual cost. Keep projected high ($90). savings +$75.50
      setTimeout(() => {
        setStatus('HEALTHY');
        
        // Calculate new base drop cost based on upcoming node count
        const newActiveCount = 8 - offlineNodes.length - 1;
        const dropCost = newActiveCount === 0 ? 0 : (newActiveCount * 1.2);

        setChartData(prev => [
          ...prev.slice(1),
          { time: getTime(), actualCost: dropCost, projectedCost: 90 }
        ]);

        setOfflineNodes(prev => [...prev, targetNode]);
        setActiveAnomalyNode(null);

        setLogs(prev => [
          {
            id: Date.now(),
            timestamp: new Date().toLocaleTimeString(),
            resourceId: `i-core-node-${targetNode}`,
            reason: 'CPU > 95% (Cost Spike)',
            action: 'Autonomously Stopped Instance'
          },
          ...prev
        ]);

        setSavings(prev => prev + 75.50);
        setIsSimulating(false);
      }, 2000);
    }, 3000);
  };

  const recoverNodes = () => {
    if (offlineNodes.length === 0 || isSimulating) return;

    const count = offlineNodes.length;
    setOfflineNodes([]);

    setLogs(prev => [
      {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString(),
        resourceId: 'auto-scaling-group',
        reason: 'Capacity Rebalanced',
        action: `Spun up ${count} Replacement Node${count > 1 ? 's' : ''}`
      },
      ...prev
    ]);
  };

  const handleMouseMove = (e) => {
    setMousePosition({ x: e.clientX, y: e.clientY });
  };

  return (
    <div 
      className="min-h-screen bg-slate-950 text-slate-100 font-sans p-4 md:p-8 selection:bg-emerald-500/30 relative overflow-hidden"
      onMouseMove={handleMouseMove}
    >
      {/* Dynamic Cyberpunk Cursor Spotlight */}
      <div 
        className="pointer-events-none fixed inset-0 z-0 transition-opacity duration-300"
        style={{
          background: `radial-gradient(800px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(16, 185, 129, 0.08), transparent 80%)`
        }}
      />

      <div className="max-w-7xl mx-auto space-y-6 relative z-10">

        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-emerald-500/20 pb-4 gap-4">
          <div className="flex items-center gap-4">
            <div className="bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
              <Zap className="text-emerald-500 w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 drop-shadow-md">
                ⚡ CYBERPUNK FINOPS
              </h1>
              <p className="text-emerald-500/70 text-xs font-mono tracking-widest mt-1 uppercase">Autonomous Remediation Core</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            {offlineNodes.length > 0 && (
              <button
                onClick={recoverNodes}
                disabled={isSimulating}
                className={`flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-black tracking-widest uppercase transition-all duration-300 border backdrop-blur-sm ${isSimulating
                    ? 'bg-slate-900 border-slate-700 text-slate-500 cursor-not-allowed'
                    : 'bg-emerald-500/10 border-emerald-500 text-emerald-500 hover:bg-emerald-500 hover:text-white shadow-[0_0_20px_rgba(16,185,129,0.3)] active:scale-95'
                  }`}
              >
                <RefreshCw className="w-5 h-5" />
                Auto-Recover
              </button>
            )}
            <button
              onClick={simulateChaos}
              disabled={isSimulating}
              className={`flex items-center justify-center gap-2 px-8 py-3 rounded-lg font-black tracking-widest uppercase transition-all duration-300 border backdrop-blur-sm ${isSimulating
                  ? 'bg-slate-900 border-slate-700 text-slate-500 cursor-not-allowed'
                  : 'bg-red-500/10 border-red-500 text-red-500 hover:bg-red-500 hover:text-white shadow-[0_0_20px_rgba(239,68,68,0.4)] active:scale-95'
                }`}
            >
              <Zap className={`w-5 h-5 ${isSimulating ? '' : 'animate-pulse'}`} />
              {isSimulating ? 'System Busy...' : 'Simulate Chaos'}
            </button>
          </div>
        </header>

        <main className="animate-in fade-in duration-700 glassmorphism space-y-6">
          {/* Row 1: KPI Cards */}
          <section className="w-full">
            <KPICards status={status} savings={savings} chartData={chartData} />
          </section>

          {/* Row 2: Grid Layout (Chart 2/3, Maps/Terminal 1/3) */}
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <LiveChart data={chartData} />
            </div>
            <div className="flex flex-col gap-6 lg:col-span-1">
              <NodeMap status={status} activeAnomalyNode={activeAnomalyNode} offlineNodes={offlineNodes} />
              <Terminal status={status} />
            </div>
          </section>

          {/* Row 3: Action Log */}
          <section className="w-full">
            <ActionLog logs={logs} />
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
