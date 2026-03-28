import React from 'react';
import { Activity, Clock } from 'lucide-react';

const ActionLog = ({ logs }) => {
  return (
    <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-xl shadow-xl overflow-hidden w-full">
      <div className="p-5 border-b border-slate-800 flex justify-between items-center">
        <h3 className="text-slate-200 font-bold text-sm tracking-wide flex items-center gap-2 uppercase">
          <Activity className="w-4 h-4 text-rose-600" />
          Intervention History
        </h3>
        <span className="text-xs font-mono text-slate-500 border border-slate-700 px-2 py-1 rounded bg-slate-900">
          Showing last {logs.length} actions
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 font-mono text-xs uppercase">
            <tr>
              <th className="px-6 py-4 font-medium flex items-center gap-2">
                <Clock className="w-3 h-3" />
                Timestamp
              </th>
              <th className="px-6 py-4 font-medium">Resource ID</th>
              <th className="px-6 py-4 font-medium">Detection Reason</th>
              <th className="px-6 py-4 font-medium">Action Taken</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50 font-mono text-xs">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="px-6 py-4 text-slate-500">{log.timestamp}</td>
                <td className="px-6 py-4 text-slate-300">{log.resourceId}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2 py-1 rounded-sm text-[10px] uppercase font-bold tracking-wider border ${
                    log.reason.includes('Idle') || log.reason.includes('Overprovisioned') || log.reason.includes('Rebalanced')
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
                      : 'bg-red-500/10 text-red-500 border-red-500/30 shadow-[0_0_8px_rgba(239,68,68,0.2)]'
                  }`}>
                    {log.reason}
                  </span>
                </td>
                <td className="px-6 py-4 font-bold text-rose-600">
                  {log.action}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ActionLog;
