import React from 'react';
import { Activity, DollarSign, Server } from 'lucide-react';

const KPICards = ({ status, savings, chartData }) => {
  // Determine color theme based on status
  let statusColor = 'text-emerald-500';
  let dotColor = 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]';
  let borderColor = 'border-emerald-500/20';

  if (status === 'ANOMALY') {
    statusColor = 'text-red-500';
    dotColor = 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)]';
    borderColor = 'border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]';
  } else if (status === 'REMEDIATING') {
    statusColor = 'text-blue-500';
    dotColor = 'bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)]';
    borderColor = 'border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.3)]';
  }

  const currentRunRate = chartData.length > 0 ? chartData[chartData.length - 1].actualCost : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Current Run Rate */}
      <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl flex flex-col justify-between hover:bg-slate-900/80 transition-all">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-slate-400 font-mono text-sm uppercase tracking-wider">Current Run Rate</h3>
          <Activity className="text-emerald-500 w-5 h-5 opacity-70" />
        </div>
        <div>
          <span className="text-4xl font-black text-slate-100">${currentRunRate.toFixed(2)}</span>
          <span className="text-slate-500 ml-2 font-mono text-sm">/hr</span>
        </div>
      </div>

      {/* System Status */}
      <div className={`bg-slate-900/50 backdrop-blur-md border-2 rounded-xl p-6 shadow-xl flex flex-col justify-between transition-all duration-300 ${borderColor} relative overflow-hidden`}>
        {/* Subtle background glow */}
        <div className={`absolute -inset-4 opacity-10 blur-2xl ${dotColor.replace('bg-', 'bg-').split(' ')[0]}`}></div>
        
        <div className="flex items-center justify-between mb-4 relative z-10">
          <h3 className="text-slate-400 font-mono text-sm uppercase tracking-wider">System Status</h3>
          <Server className={`${statusColor} w-5 h-5 opacity-80`} />
        </div>
        <div className="flex items-center gap-3 relative z-10">
          <div className={`w-3 h-3 rounded-full animate-pulse ${dotColor}`}></div>
          <span className={`text-2xl font-black tracking-widest ${statusColor}`}>{status}</span>
        </div>
      </div>

      {/* Total Savings */}
      <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl flex flex-col justify-between hover:bg-slate-900/80 transition-all">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-slate-400 font-mono text-sm uppercase tracking-wider">Total Savings</h3>
          <DollarSign className="text-emerald-500 w-5 h-5 opacity-70" />
        </div>
        <div>
          <span className="text-4xl font-black text-emerald-500 drop-shadow-[0_0_8px_rgba(16,185,129,0.4)]">
            ${savings.toFixed(2)}
          </span>
          <span className="text-slate-500 ml-2 font-mono text-sm">YTD</span>
        </div>
      </div>
    </div>
  );
};

export default KPICards;
