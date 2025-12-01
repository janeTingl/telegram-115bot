import React, { useEffect, useState, useRef } from 'react';

interface LogEntry {
  time: string;
  status: string;
  task: string;
  result: string;
}

export const LogsView: React.FC = () => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  
  // 轮询获取真实日志
  useEffect(() => {
    const fetchLogs = async () => {
        try {
            const res = await fetch('/api/logs');
            if (res.ok) {
                const data = await res.json();
                setLogs(data);
            }
        } catch (e) {
            console.error("Failed to fetch logs");
        }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 3000); // 3秒刷新一次
    return () => clearInterval(interval);
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="h-[calc(100vh-140px)] flex flex-col">
       <div className="mb-4 flex justify-between items-end">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white">运行日志</h2>
        <span className="text-xs text-slate-400 font-mono">Real-time Logging</span>
      </div>
      
      <div className="flex-1 bg-white dark:bg-slate-900 rounded-xl shadow-inner border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col font-mono text-xs">
        <div className="bg-slate-100 dark:bg-slate-800 px-3 py-2 border-b border-slate-200 dark:border-slate-700 grid grid-cols-12 gap-2 font-bold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
            <div className="col-span-3">时间</div>
            <div className="col-span-1">状态</div>
            <div className="col-span-2">任务</div>
            <div className="col-span-6">运行结果</div>
        </div>

        <div className="p-0 overflow-y-auto flex-1 scroll-smooth custom-scrollbar" ref={scrollRef}>
            {logs.length === 0 ? (
                <div className="p-4 text-center text-slate-400 italic">暂无日志...</div>
            ) : (
                logs.map((log, i) => (
                    <div key={i} className="grid grid-cols-12 gap-2 px-3 py-1 border-b border-slate-50 dark:border-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors items-center">
                        <div className="col-span-3 text-slate-400 opacity-80 scale-95 origin-left">{log.time}</div>
                        <div className="col-span-1">
                            <span className={`px-1.5 py-0.5 rounded-[3px] text-[9px] font-bold border ${
                                log.status === 'INFO' ? 'bg-blue-50 text-blue-600 border-blue-100 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-900' : 
                                log.status === 'WARNING' || log.status === 'WARN' ? 'bg-amber-50 text-amber-600 border-amber-100 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-900' :
                                log.status === 'ERROR' ? 'bg-red-50 text-red-600 border-red-100 dark:bg-red-900/30 dark:text-red-400 dark:border-red-900' :
                                'bg-emerald-50 text-emerald-600 border-emerald-100 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-900'
                            }`}>
                                {log.status}
                            </span>
                        </div>
                        <div className="col-span-2 font-medium text-slate-700 dark:text-slate-300 truncate">{log.task}</div>
                        <div className="col-span-6 text-slate-600 dark:text-slate-400 truncate" title={log.result}>{log.result}</div>
                    </div>
                ))
            )}
            <div className="py-2 text-center opacity-50">
                 <div className="animate-pulse w-1.5 h-3 bg-brand-400 inline-block align-middle"></div>
            </div>
        </div>
      </div>
    </div>
  );
};
