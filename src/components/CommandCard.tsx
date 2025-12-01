import React from 'react';
import { Copy } from 'lucide-react';

interface CommandCardProps {
  command: string;
  description: string;
  example?: string;
}

export const CommandCard: React.FC<CommandCardProps> = ({ command, description, example }) => {
  const copyToClipboard = () => { navigator.clipboard.writeText(command); };
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <code className="bg-slate-100 dark:bg-slate-700 text-brand-700 dark:text-brand-400 px-2 py-1 rounded text-sm font-mono font-bold">{command}</code>
        <button onClick={copyToClipboard} className="text-slate-400 hover:text-brand-600"><Copy size={16} /></button>
      </div>
      <p className="text-slate-600 dark:text-slate-400 text-sm mb-2">{description}</p>
      {example && <div className="text-xs text-slate-400 bg-slate-50 dark:bg-slate-900/50 p-2 rounded border border-slate-100 dark:border-slate-700 font-mono mt-2"><span className="text-slate-500 select-none">$ </span>{example}</div>}
    </div>
  );
};
