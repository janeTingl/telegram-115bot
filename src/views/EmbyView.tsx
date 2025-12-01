import React, { useState } from 'react';
import { AppConfig } from '../types';
import { loadConfig, saveConfig } from '../services/mockConfig';
import { Save, RefreshCw, Clapperboard, BarChart3, Layout, Clock, Image as ImageIcon, Sparkles, Folder, Bell, Copy, Zap, TrendingUp, Users } from 'lucide-react';
import { SensitiveInput } from '../components/SensitiveInput';

export const EmbyView: React.FC = () => {
  const [config, setConfig] = useState<AppConfig>(loadConfig());
  const [isSaving, setIsSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const updateNested = (section: keyof AppConfig, key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], [key]: value }
    }));
  };

  const updateNotifications = (key: string, value: any) => {
    setConfig(prev => ({
        ...prev,
        emby: {
            ...prev.emby,
            notifications: { ...prev.emby.notifications, [key]: value }
        }
    }));
  };
  
  const updatePoster = (key: string, value: any) => {
     setConfig(prev => ({
      ...prev,
      emby: { 
          ...prev.emby, 
          posterGeneration: { ...prev.emby.posterGeneration, [key]: value } 
      }
    }));
  };

  const handleSave = () => {
    setIsSaving(true);
    saveConfig(config).then(() => {
      setIsSaving(false);
      setToast('Emby 配置已保存');
      setTimeout(() => setToast(null), 3000);
    });
  };

  const copyWebhook = () => {
      navigator.clipboard.writeText(`http://${window.location.hostname}:12808/api/webhook/115bot`);
      setToast('Webhook 地址已复制');
      setTimeout(() => setToast(null), 2000);
  };
  
  const fillLocalIp = () => {
      updateNested('emby', 'serverUrl', `http://${window.location.hostname}:8096`);
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
      {toast && (
        <div className="fixed top-6 right-6 bg-emerald-500 text-white px-6 py-3 rounded-lg shadow-xl z-50 flex items-center gap-3 font-medium">
          <RefreshCw size={20} className="animate-spin" /> {toast}
        </div>
      )}

      <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-700 pb-4">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Emby 联动</h2>
        <button onClick={handleSave} disabled={isSaving} className="bg-brand-600 hover:bg-brand-700 text-white px-5 py-2 rounded-lg font-medium flex items-center gap-2 shadow-lg text-sm">
          {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />} 保存设置
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Connection */}
        <section className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden h-fit">
           <div className="px-5 py-3 bg-slate-50/80 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
            <div className="flex items-center gap-2"><Clapperboard size={16} className="text-green-500" /><h3 className="font-bold text-slate-700 dark:text-slate-100 text-sm">服务器连接</h3></div>
            <div className="flex items-center gap-3">
               <input type="checkbox" checked={config.emby.enabled} onChange={(e) => updateNested('emby', 'enabled', e.target.checked)} className="w-4 h-4 rounded text-green-600" />
               <label className="text-sm font-bold text-slate-700 dark:text-slate-300">启用</label>
            </div>
          </div>
          <div className={`p-5 space-y-4 ${config.emby.enabled ? 'opacity-100' : 'opacity-50 pointer-events-none'}`}>
             <div>
                <div className="flex justify-between items-center mb-1.5">
                   <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400">服务器地址</label>
                   <button onClick={fillLocalIp} className="text-[10px] text-brand-600 hover:underline flex items-center gap-1"><Zap size={10} /> 自动填入</button>
                </div>
                <input type="text" value={config.emby.serverUrl} onChange={(e) => updateNested('emby', 'serverUrl', e.target.value)} placeholder="http://192.168.1.5:8096" className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm" />
             </div>
             <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">API 密钥 (API Key)</label>
                <SensitiveInput value={config.emby.apiKey} onChange={(e) => updateNested('emby', 'apiKey', e.target.value)} className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm font-mono" />
             </div>
             
             <div className="pt-4 border-t border-slate-100 dark:border-slate-700">
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Webhook 回调地址</label>
                <div className="flex gap-2">
                    <div className="flex-1 bg-slate-100 dark:bg-slate-900/50 p-2 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-mono text-slate-500 truncate select-all">
                        http://{window.location.hostname}:12808/api/webhook/115bot
                    </div>
                    <button onClick={copyWebhook} className="p-2 bg-slate-200 dark:bg-slate-700 rounded-lg text-slate-600 dark:text-slate-300"><Copy size={16} /></button>
                </div>
             </div>
          </div>
        </section>

        {/* Notification */}
        <section className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden h-fit">
           <div className="px-5 py-3 bg-slate-50/80 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
               <Bell size={16} className="text-blue-500" />
               <h3 className="font-bold text-slate-700 dark:text-slate-100 text-sm">通知与报告</h3>
           </div>
           <div className={`p-5 space-y-4 ${config.emby.notifications.enabled ? 'opacity-100' : 'opacity-50 pointer-events-none'}`}>
              <div className="flex items-center justify-between">
                 <span className="text-sm font-medium text-slate-700 dark:text-slate-300">转发 Emby 通知到 Telegram</span>
                 <input type="checkbox" checked={config.emby.notifications.forwardToTelegram} onChange={(e) => updateNotifications('forwardToTelegram', e.target.checked)} className="w-4 h-4 rounded text-blue-600" />
              </div>
              <div className="flex items-center justify-between">
                 <span className="text-sm font-medium text-slate-700 dark:text-slate-300">周报预览</span>
                 <div className="text-xs text-slate-400">Mock Data</div>
              </div>
           </div>
        </section>

        {/* Poster Wall (原版找回) */}
        <section className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden h-fit lg:col-span-2">
           <div className="px-5 py-3 bg-slate-50/80 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
             <div className="flex items-center gap-2">
               <ImageIcon size={16} className="text-purple-500" />
               <h3 className="font-bold text-slate-700 dark:text-slate-100 text-sm">媒体库海报墙</h3>
            </div>
             <div className="flex items-center gap-3">
                <input type="checkbox" checked={config.emby.posterGeneration.enabled} onChange={(e) => updatePoster('enabled', e.target.checked)} className="w-4 h-4 rounded text-purple-600" />
            </div>
           </div>
           
           <div className={`p-5 grid grid-cols-1 md:grid-cols-3 gap-6 transition-all duration-300 ${config.emby.posterGeneration.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
              <div className="md:col-span-3 mb-1 flex items-center gap-3 bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg border border-purple-100 dark:border-purple-900/50">
                  <Sparkles size={16} className="text-purple-500" />
                  <span className="text-xs text-purple-800 dark:text-purple-300 font-medium">功能说明: 自动将媒体库封面组合成精美的拼图，并设置为媒体目录的封面图。</span>
              </div>

              <div>
                 <label className="block text-xs font-bold text-slate-500 uppercase mb-3 flex items-center gap-1"><Layout size={14}/> 拼图创意模版</label>
                 <div className="grid grid-cols-3 gap-2">
                    {['modern_grid', 'creative_puzzle', 'classic_list'].map(tpl => (
                        <button key={tpl} onClick={() => updatePoster('template', tpl)} className={`p-2 border-2 rounded-lg flex flex-col items-center gap-1 ${config.emby.posterGeneration.template === tpl ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20' : 'border-slate-200 dark:border-slate-700'}`}>
                           <div className="w-6 h-6 bg-slate-300 rounded"></div>
                           <span className="text-[10px]">{tpl.split('_')[1]}</span>
                        </button>
                    ))}
                 </div>
              </div>

              <div>
                 <label className="block text-xs font-bold text-slate-500 uppercase mb-3">选项设置</label>
                 <div className="space-y-3">
                    <div className="flex items-center gap-2">
                       <input type="checkbox" checked={config.emby.posterGeneration.overlayDirName} onChange={(e) => updatePoster('overlayDirName', e.target.checked)} className="rounded text-purple-600" />
                       <label className="text-xs font-medium text-slate-700 dark:text-slate-300">包含目录名称</label>
                    </div>
                 </div>
                 <div className="mt-4">
                     <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">排序依据</label>
                     <select value={config.emby.posterGeneration.sortOrder} onChange={(e) => updatePoster('sortOrder', e.target.value)} className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm">
                        <option value="release_date">上映日期 (新 -&gt; 旧)</option>
                        <option value="added_date">入库时间 (新 -&gt; 旧)</option>
                     </select>
                 </div>
              </div>

              <div>
                 <label className="block text-xs font-bold text-slate-500 uppercase mb-3 flex items-center gap-1"><Clock size={14}/> 生成定时 (Cron)</label>
                 <input type="text" value={config.emby.posterGeneration.cronSchedule} onChange={(e) => updatePoster('cronSchedule', e.target.value)} className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm font-mono" />
                 <p className="text-[10px] text-slate-400 mt-2">默认: 每天午夜生成</p>
              </div>
           </div>
        </section>
      </div>
    </div>
  );
};
