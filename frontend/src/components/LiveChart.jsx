import React from 'react';
import { ResponsiveContainer, ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const LiveChart = ({ data }) => {
  return (
    <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl h-full flex flex-col min-h-[400px]">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h3 className="text-slate-200 font-bold tracking-wide">COST TRAJECTORY</h3>
          <p className="text-slate-500 text-xs font-mono mt-1">Real-time Actual vs Projected ($/hr)</p>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-rose-600 rounded-sm shadow-[0_0_5px_#e11d48]"></div>
            <span className="text-slate-300">Actual Cost</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-cyan-400 border-t border-dashed border-cyan-400"></div>
            <span className="text-slate-300">Projected (Without AI)</span>
          </div>
        </div>
      </div>
      
      <div className="flex-grow w-full h-full relative">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#e11d48" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#e11d48" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="time" stroke="#475569" tick={{ fill: '#475569', fontSize: 10, fontFamily: 'monospace' }} />
            <YAxis stroke="#475569" tick={{ fill: '#475569', fontSize: 10, fontFamily: 'monospace' }} domain={[0, 100]} />
            <Tooltip
              contentStyle={{ backgroundColor: '#020617', border: '1px solid #1e293b', borderRadius: '8px', fontFamily: 'monospace' }}
              itemStyle={{ fontWeight: 'bold' }}
            />
            {/* The Actual Cost Area */}
            <Area 
              type="monotone" 
              dataKey="actualCost" 
              name="Actual Cost ($)"
              stroke="#e11d48" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorActual)" 
              isAnimationActive={true}
              animationDuration={400}
            />
            {/* The Ghost Line (Projected Cost) */}
            <Line 
              type="monotone" 
              dataKey="projectedCost" 
              name="Projected Cost ($)"
              stroke="#22d3ee" 
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              isAnimationActive={true}
              animationDuration={400}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default LiveChart;
