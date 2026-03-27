import React from 'react';
import { Activity, DollarSign, ShieldAlert, CheckCircle2, Loader2 } from 'lucide-react';

const KPICards = ({ systemStatus, currentRunRate, totalSavings }) => {
  // Determine styles and icon based on system status
  let statusColor = 'text-green-500';
  let borderColor = 'border-slate-800';
  let Icon = CheckCircle2;
  
  if (systemStatus === '🔴 ANOMALY DETECTED') {
    statusColor = 'text-red-500';
    borderColor = 'border-red-500 shadow-[0_0_15px_rgba(255,0,0,0.5)]';
    Icon = ShieldAlert;
  } else if (systemStatus === '🔵 REMEDIATING...') {
    statusColor = 'text-blue-400';
    borderColor = 'border-blue-400 shadow-[0_0_15px_rgba(0,100,255,0.4)]';
    Icon = Loader2;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {/* Run Rate Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl flex flex-col justify-between">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-slate-400 font-medium">Current Run Rate</h3>
          <Activity className="text-slate-500 w-5 h-5" />
        </div>
        <div>
          <span className="text-3xl font-bold text-slate-100">${currentRunRate.toFixed(2)}</span>
          <span className="text-slate-500 ml-2">/hr</span>
        </div>
      </div>

      {/* System Status Card */}
      <div className={`bg-slate-900 border-2 rounded-xl p-6 shadow-xl flex flex-col justify-between transition-all duration-300 ${borderColor}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-slate-400 font-medium">System Status</h3>
          <Icon className={`${statusColor} w-5 h-5 ${systemStatus === '🔵 REMEDIATING...' ? 'animate-spin' : ''}`} />
        </div>
        <div>
          <span className={`text-xl font-bold ${statusColor}`}>{systemStatus}</span>
        </div>
      </div>

      {/* Total Savings Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl flex flex-col justify-between">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-slate-400 font-medium">Total Savings</h3>
          <DollarSign className="text-green-400 w-5 h-5" />
        </div>
        <div>
          <span className="text-3xl font-bold text-green-400">${totalSavings.toFixed(2)}</span>
          <span className="text-slate-500 ml-2">month-to-date</span>
        </div>
      </div>
    </div>
  );
};

export default KPICards;
