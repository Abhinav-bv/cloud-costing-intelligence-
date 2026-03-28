import React, { useState, useEffect, useRef } from 'react';

const FAKE_LOGS = [
  '[INFO] Auth service health check passed.',
  '[INFO] EBS Volume vol-9x8a optimized.',
  '[DEBUG] Fetching metric stream from AP-SOUTHEAST-1.',
  '[INFO] SQS Queue depth normal.',
  '[DEBUG] Garbage collection routine executed.',
  '[INFO] KMS Key rotation verified successfully.',
];

const Terminal = ({ status }) => {
  const [logs, setLogs] = useState([]);
  const containerRef = useRef(null);

  useEffect(() => {
    let interval = setInterval(() => {
      const timestamp = new Date().toISOString().split('T')[1].slice(0, 12);
      
      let newLog = '';
      if (status === 'ANOMALY') {
        newLog = `[FATAL] CPU > 95% DETECTED ON CORE-99 OVERLOAD TRIPPED`;
      } else if (status === 'REMEDIATING') {
        newLog = `[SYSTEM] EXECUTING ISOLATION PROTOCOL... SIGTERM INITIATED`;
      } else {
        newLog = FAKE_LOGS[Math.floor(Math.random() * FAKE_LOGS.length)];
      }

      const logString = `${timestamp} ${newLog}`;
      
      setLogs(prev => {
        const next = [...prev, logString];
        if (next.length > 50) return next.slice(next.length - 50);
        return next;
      });
      
    }, 1000);

    // If status changes, inject a log immediately
    if (status === 'ANOMALY') {
      const timestamp = new Date().toISOString().split('T')[1].slice(0, 12);
      setLogs(prev => [...prev, `${timestamp} [CRITICAL] 🔴 RESOURCE SPIKE DETECTED`]);
    }

    return () => clearInterval(interval);
  }, [status]);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-black/80 backdrop-blur-md border border-slate-800 rounded-xl flex flex-col shadow-xl overflow-hidden h-64 w-full shrink-0">
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-2 flex items-center gap-2">
        <div className="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
        <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></div>
        <div className="w-2.5 h-2.5 rounded-full bg-green-500/80"></div>
        <span className="text-slate-500 font-mono text-xs ml-2">syslog - bash</span>
      </div>
      <div ref={containerRef} className="p-4 font-mono text-xs leading-5 overflow-y-auto flex-grow h-full text-slate-300">
        {logs.map((log, i) => {
          let colorClass = 'text-slate-400';
          if (log.includes('[FATAL]') || log.includes('[CRITICAL]')) colorClass = 'text-red-500 font-bold drop-shadow-[0_0_5px_rgba(239,68,68,0.8)]';
          else if (log.includes('REMEDIATING') || log.includes('[SYSTEM]')) colorClass = 'text-blue-400 font-bold';
          else if (log.includes('[INFO]')) colorClass = 'text-emerald-400';

          return <div key={i} className={colorClass}>{log}</div>;
        })}
      </div>
    </div>
  );
};

export default Terminal;
