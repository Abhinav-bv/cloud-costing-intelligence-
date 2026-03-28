import React from 'react';

const NodeMap = ({ status, activeAnomalyNode, offlineNodes }) => {
  const nodes = Array.from({ length: 8 }).map((_, i) => ({ id: i }));

  return (
    <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-xl p-5 shadow-xl">
      <h3 className="text-slate-200 font-bold tracking-wide text-sm mb-4">NODE CLUSTER</h3>
      
      <div className="grid grid-cols-4 gap-3">
        {nodes.map(node => {
          const isTargetNode = node.id === activeAnomalyNode;
          const isOffline = offlineNodes.includes(node.id);
          
          let nodeColor = 'bg-emerald-500/20 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.2)]';
          let pulse = false;

          if (isOffline) {
            nodeColor = 'bg-slate-700/30 border-slate-600 shadow-none';
          } else if (isTargetNode) {
            if (status === 'ANOMALY') {
              nodeColor = 'bg-red-500/30 border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.6)]';
              pulse = true;
            } else if (status === 'REMEDIATING') {
              nodeColor = 'bg-blue-500/30 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.5)]';
              pulse = true;
            }
          }

          return (
            <div 
              key={node.id} 
              className={`aspect-square rounded-md border flex items-center justify-center transition-all duration-300 relative ${nodeColor}`}
            >
              {pulse && (
                <div className={`absolute inset-0 rounded-md animate-ping opacity-50 ${isTargetNode && status === 'ANOMALY' ? 'bg-red-500' : 'bg-blue-500'}`}></div>
              )}
              <div className={`w-2 h-2 rounded-full ${isOffline ? 'bg-slate-500' : isTargetNode && status === 'ANOMALY' ? 'bg-red-500' : isTargetNode && status === 'REMEDIATING' ? 'bg-blue-500' : 'bg-emerald-500'}`}></div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default NodeMap;
