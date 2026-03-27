import React from 'react';
import { Activity, Clock } from 'lucide-react';

const ActionLog = ({ logs }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden mb-8 w-full">
      <div className="p-6 border-b border-slate-800">
        <h3 className="text-slate-200 font-semibold text-lg flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-400" />
          Autonomous Action Log
        </h3>
        <p className="text-slate-500 text-sm">Recent AI-driven resolutions and cost optimizations</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-slate-950/50 text-slate-400 border-b border-slate-800">
            <tr>
              <th className="px-6 py-4 font-medium flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Timestamp
              </th>
              <th className="px-6 py-4 font-medium">Resource ID</th>
              <th className="px-6 py-4 font-medium">Detection Reason</th>
              <th className="px-6 py-4 font-medium">Action Taken</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                <td className="px-6 py-4 text-slate-400">{log.timestamp}</td>
                <td className="px-6 py-4 font-mono text-slate-300">{log.resourceId}</td>
                <td className="px-6 py-4 text-slate-300">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                    log.reason.includes('Idle') || log.reason.includes('Overprovisioned') 
                      ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' 
                      : 'bg-red-500/10 text-red-400 border-red-500/20'
                  }`}>
                    {log.reason}
                  </span>
                </td>
                <td className="px-6 py-4 text-slate-300 font-medium text-green-400">
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
