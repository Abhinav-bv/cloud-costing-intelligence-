import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const LiveChart = ({ data }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl mb-8 w-full">
      <div className="mb-4">
        <h3 className="text-slate-200 font-semibold text-lg">EC2 CPU Utilization (%)</h3>
        <p className="text-slate-500 text-sm">Real-time resource usage monitoring across instances</p>
      </div>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#39ff14" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#39ff14" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="time" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
            <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} domain={[0, 100]} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f1f5f9' }}
              itemStyle={{ color: '#39ff14' }}
            />
            <Area 
              type="monotone" 
              dataKey="cpu" 
              stroke="#39ff14" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorCpu)" 
              isAnimationActive={true}
              animationDuration={300}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default LiveChart;
