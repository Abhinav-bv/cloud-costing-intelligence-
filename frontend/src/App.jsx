import React, { useState, useEffect, useRef } from 'react';
import KPICards from './components/KPICards';
import LiveChart from './components/LiveChart';
import NodeMap from './components/NodeMap';
import Terminal from './components/Terminal';
import ActionLog from './components/ActionLog';
import { Zap, RefreshCw } from 'lucide-react';
import { fetchClusterData, triggerChaos, autoRecover } from './services/api';
import * as THREE from 'three';
import CLOUDS from 'vanta/src/vanta.clouds';

// Essential for Vanta to locate Three.js globally in a Vite environment
if (typeof window !== 'undefined') {
  window.THREE = THREE;
}

function App() {
  const [status, setStatus] = useState('HEALTHY'); // 'HEALTHY', 'ANOMALY', 'REMEDIATING'
  const [savings, setSavings] = useState(0);
  const [chartData, setChartData] = useState([]);
  const [logs, setLogs] = useState([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [offlineNodes, setOfflineNodes] = useState([]);
  const [activeAnomalyNode, setActiveAnomalyNode] = useState(null);
  const [vantaEffect, setVantaEffect] = useState(null);
  const vantaRef = useRef(null);

  useEffect(() => {
    if (!vantaEffect && vantaRef.current) {
      setVantaEffect(
        CLOUDS({
          el: vantaRef.current,
          THREE: THREE,
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.00,
          minWidth: 200.00,
          skyColor: 0x000216,
          cloudColor: 0x0a192f,
          cloudShadowColor: 0x020c1b,
          sunColor: 0x1d4ed8, // Dark Blue Glow (blue-700)
          sunGlareColor: 0x2563eb, // blue-600
          sunPosition: { x: 0, y: 0, z: 0 },
          speed: 1.0
        })
      );
    }
    return () => {
      if (vantaEffect) vantaEffect.destroy();
    };
  }, [vantaEffect]);

  // Poll the backend every 1.5 seconds to synchronize state
  useEffect(() => {
    const pollBackend = async () => {
      const data = await fetchClusterData();
      if (data) {
        setStatus(data.status);
        setOfflineNodes(data.offlineNodes);
        setActiveAnomalyNode(data.activeAnomalyNode);
        setSavings(data.savings);
        setLogs(data.logs);
        setChartData(data.chartData);
        setIsSimulating(data.isSimulating);
      }
    };

    pollBackend(); // Initial fetch
    const interval = setInterval(pollBackend, 1500);
    return () => clearInterval(interval);
  }, []);

  const simulateChaos = async () => {
    if (isSimulating) return;
    setIsSimulating(true);
    await triggerChaos();
  };

  const recoverNodes = async () => {
    if (offlineNodes.length === 0 || isSimulating) return;
    await autoRecover();
  };

  return (
    <>
      {/* Vanta WebGL Background Layer */}
      <div ref={vantaRef} className="fixed inset-0 z-0" style={{ backgroundColor: '#000216' }} />

      {/* Main Foreground Application */}
      <div className="min-h-screen text-slate-100 font-sans p-4 md:p-8 selection:bg-rose-600/30 relative z-10 overflow-y-auto">
        <div className="max-w-7xl mx-auto space-y-6 relative">

        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-rose-600/20 pb-4 gap-4">
          <div className="flex items-center gap-4">
            <div className="bg-rose-600/10 p-3 rounded-xl border border-rose-600/30 shadow-[0_0_20px_rgba(225,29,72,0.2)]">
              <Zap className="text-rose-600 w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 drop-shadow-md">
                ⚡ CYBERPUNK FINOPS
              </h1>
              <p className="text-rose-600/70 text-xs font-mono tracking-widest mt-1 uppercase">Autonomous Remediation Core</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            {offlineNodes.length > 0 && (
              <button
                onClick={recoverNodes}
                disabled={isSimulating}
                className={`flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-black tracking-widest uppercase transition-all duration-300 border backdrop-blur-sm ${isSimulating
                  ? 'bg-slate-900 border-slate-700 text-slate-500 cursor-not-allowed'
                  : 'bg-rose-600/10 border-rose-600 text-rose-600 hover:bg-rose-600 hover:text-white shadow-[0_0_20px_rgba(225,29,72,0.3)] active:scale-95'
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
    </>
  );
}

export default App;
