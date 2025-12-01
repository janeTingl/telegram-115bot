import React, { useState } from 'react';
import { AppConfig } from '../types';
import { loadConfig, saveConfig } from '../services/mockConfig';
import { Tooltip } from '../components/Tooltip';
import { CommandCard } from '../components/CommandCard';
import { Bot, Save, RefreshCw, MessageSquare } from 'lucide-react';
import { SensitiveInput } from '../components/SensitiveInput';

export const BotSettingsView: React.FC = () => {
  const [config, setConfig] = useState<AppConfig>(loadConfig());
  const [isSaving, setIsSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const updateNested = (section: keyof AppConfig, key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], [key]: value }
    }));
  };

  const handleSave = () => {
    setIsSaving(true);
    saveConfig(config).then(() => {
      setIsSaving(false);
      setToast('机器人配置已保存 (后端已热重载)');
      setTimeout(() => setToast(null), 3000);
    });
  };

  const commands = [
    { cmd: '/start', desc: '初始化机器人并检查连接状态', example: '/start' },
    { cmd: '/magnet', desc: '添加磁力/Ed2k/HTTP 链接离线任务', example: '/magnet magnet:?xt=urn:btih:...' },
    { cmd: '/quota', desc: '查看 115 账号离线配额和空间使用', example: '/quota' },
    { cmd: '/help', desc: '获取帮助菜单', example: '/help' },
  ];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
      {toast && (
        <div className="fixed top-6 right-6 bg-emerald-500 text-white px-6 py-3 rounded-lg shadow-xl shadow-emerald-500/20 z-50 flex items-center gap-3 font-medium">
          <RefreshCw size={20} className="animate-spin" />
          {toast}
        </div>
      )}

      <div className="flex flex-col md:flex-row justify-between items-center border-b border-slate-200 dark:border-slate-700 pb-4 gap-4">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white">机器人设置</h2>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="bg-brand-600 hover:bg-brand-700 disabled:opacity-70 text-white px-5 py-2 rounded-lg font-medium flex items-center gap-2 shadow-lg shadow-brand-500/30 transition-all active:scale-95 text-sm"
        >
          {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />}
          保存设置
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden h-fit">
          <div className="px-5 py-3 bg-slate-50/80 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
            <Bot size={16} className="text-blue-500" />
            <h3 className="font-bold text-slate-700 dark:text-slate-100 text-sm">核心参数</h3>
          </div>
          <div className="p-5 space-y-4">
            <div>
              <label className="flex items-center text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                机器人令牌 (Bot Token)
                <Tooltip content="从 @BotFather 获取的 API Token" />
              </label>
              <SensitiveInput
                  value={config.telegram.botToken}
                  onChange={(e) => updateNested('telegram', 'botToken', e.target.value)}
                  className="w-full pl-3 pr-9 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 outline-none transition-all font-mono text-sm"
                  placeholder="123456:ABC-DEF..."
                />
            </div>

            <div>
              <label className="flex items-center text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                管理员 ID (Admin User ID)
                <Tooltip content="你的 Telegram 数字 ID (可通过 @userinfobot 获取)，用于鉴权" />
              </label>
              <SensitiveInput
                value={config.telegram.adminUserId}
                onChange={(e) => updateNested('telegram', 'adminUserId', e.target.value)}
                className="w-full pl-3 pr-9 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 outline-none text-sm font-mono"
                placeholder="123456789"
              />
            </div>
            
             <div>
              <label className="flex items-center text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                通知频道 ID
                <Tooltip content="可选：任务完成通知发送到的频道 ID (如 -100xxxxxxxx)" />
              </label>
              <SensitiveInput
                value={config.telegram.notificationChannelId}
                onChange={(e) => updateNested('telegram', 'notificationChannelId', e.target.value)}
                className="w-full pl-3 pr-9 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 outline-none text-sm font-mono"
                placeholder="-100123456789"
              />
            </div>
            
             <div className="flex items-center gap-3 pt-2">
               <div className="relative inline-block w-9 h-5 transition duration-200 ease-in-out rounded-full cursor-pointer">
                  <input 
                    id="whitelist" 
                    type="checkbox" 
                    className="peer sr-only"
                    checked={config.telegram.whitelistMode}
                    onChange={(e) => updateNested('telegram', 'whitelistMode', e.target.checked)}
                  />
                  <label htmlFor="whitelist" className="block h-5 overflow-hidden bg-slate-200 dark:bg-slate-600 rounded-full cursor-pointer peer-checked:bg-blue-600 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:w-4 after:h-4 after:rounded-full after:shadow-sm after:transition-all peer-checked:after:translate-x-full"></label>
              </div>
              <label htmlFor="whitelist" className="text-sm font-medium text-slate-600 dark:text-slate-400 cursor-pointer select-none">开启白名单模式 (仅管理员可用)</label>
            </div>
          </div>
        </section>

        <section className="space-y-4">
           <h3 className="font-bold text-slate-700 dark:text-slate-200 flex items-center gap-2 text-sm">
             <MessageSquare size={16} /> 指令速查
           </h3>
           <div className="grid grid-cols-1 gap-3 h-[400px] overflow-y-auto pr-2 custom-scrollbar">
             {commands.map((c) => (
                <CommandCard 
                  key={c.cmd} 
                  command={c.cmd} 
                  description={c.desc} 
                  example={c.example} 
                />
              ))}
           </div>
        </section>
      </div>
    </div>
  );
};
