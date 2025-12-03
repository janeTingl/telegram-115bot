
import React, { useState } from 'react';
import { AppConfig } from '../types';
import { loadConfig, saveConfig } from '../services/mockConfig';
import { Tooltip } from '../components/Tooltip';
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
    setTimeout(() => {
      saveConfig(config);
      setIsSaving(false);
      setToast('Emby 联动配置已保存');
      setTimeout(() => setToast(null), 3000);
    }, 800);
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
        <div className="fixed top-6 right-6 bg-slate-800/90 backdrop-blur-md text-white px-6 py-3 rounded-xl shadow-2xl z-50 flex items-center gap-3 font-medium border border-slate-700/50">
          <RefreshCw size={18} className="animate-spin text-brand-400" />
          {toast}
        </div>
      )}

      <div className="flex flex-col md:flex-row justify-between items-center pb-2 gap-4">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white tracking-tight drop-shadow-sm">Emby 联动</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Connection */}
        <section className="bg-white/70 dark:bg-slate-900/50 backdrop-blur-md rounded-xl border border-white/50 dark:border-slate-700/50 shadow-sm h-fit">
           <div className="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50 flex items-center justify-between">
            <div className="flex items-center gap-3">
               <Clapperboard size={18} className="text-green-500" />
               <h3 className="font-bold text-slate-700 dark:text-slate-200">服务器连接</h3>
            </div>
             <div className="flex items-center gap-4">
               {config.emby.enabled && (
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100/50 dark:bg-slate-700/30 border border-slate-200/50 dark:border-slate-600/50">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                        <span className="text-[10px] font-mono font-medium text-slate-500 dark:text-slate-400">32ms</span>
                    </div>
               )}
               {/* Header Toggle */}
               <div className="relative inline-block w-9 h-5 transition duration-200 ease-in-out rounded-full cursor-pointer">
                  <input 
                    id="embyEnabled" 
                    type="checkbox" 
                    className="peer sr-only"
                    checked={config.emby.enabled}
                    onChange={(e) => updateNested('emby', 'enabled', e.target.checked)}
                  />
                  <label htmlFor="embyEnabled" className="block h-5 overflow-hidden bg-slate-200 dark:bg-slate-700 rounded-full cursor-pointer peer-checked:bg-green-600 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white dark:after:bg-white after:w-4 after:h-4 after:rounded-full after:shadow-sm after:transition-all peer-checked:after:translate-x-full"></label>
              </div>
            </div>
          </div>
          <div className={`p-6 space-y-6 transition-opacity duration-300 ${config.emby.enabled ? 'opacity-100' : 'opacity-50 pointer-events-none'}`}>
             <div>
                <div className="flex justify-between items-center mb-2">
                   <label className="block text-sm font-medium text-slate-600 dark:text-slate-400">服务器地址</label>
                   <button onClick={fillLocalIp} className="text-xs text-brand-600 hover:text-brand-500 flex items-center gap-1 font-medium"><Zap size={12} /> 自动填入</button>
                </div>
                <input
                  type="text"
                  value={config.emby.serverUrl}
                  onChange={(e) => updateNested('emby', 'serverUrl', e.target.value)}
                  placeholder="http://192.168.1.5:8096"
                  className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-green-500 outline-none text-sm backdrop-blur-sm"
                />
             </div>
             <div>
                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1.5">API 密钥 (API Key)</label>
                <SensitiveInput
                    value={config.emby.apiKey}
                    onChange={(e) => updateNested('emby', 'apiKey', e.target.value)}
                    className="w-full pl-4 pr-10 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-green-500 outline-none text-sm font-mono backdrop-blur-sm"
                  />
             </div>
             <div className="flex items-center gap-3 pt-2">
                 <input 
                    type="checkbox" 
                    id="refreshDelay"
                    checked={config.emby.refreshAfterOrganize}
                    onChange={(e) => updateNested('emby', 'refreshAfterOrganize', e.target.checked)}
                    className="w-4 h-4 rounded text-green-600 focus:ring-green-500"
                 />
                 <label htmlFor="refreshDelay" className="text-sm font-medium text-slate-700 dark:text-slate-300 cursor-pointer select-none">
                    整理完成后延迟 3 秒刷新 Emby 媒体库
                 </label>
             </div>
             
             {/* Webhook Copy */}
             <div className="pt-6 border-t border-slate-100 dark:border-slate-700">
                <label className="block text-xs font-bold text-slate-500 uppercase mb-3">Webhook 回调地址 (一键复制)</label>
                <div className="flex gap-3">
                    <div className="flex-1 bg-slate-50/50 dark:bg-slate-900/50 p-3 rounded-lg border border-slate-200/50 dark:border-slate-700/50 text-sm font-mono text-slate-500 truncate select-all backdrop-blur-sm">
                        http://{window.location.hostname}:12808/api/webhook/115bot
                    </div>
                    <button onClick={copyWebhook} className="px-4 bg-slate-100/50 dark:bg-slate-700/50 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg text-slate-600 dark:text-slate-300 transition-colors backdrop-blur-sm">
                        <Copy size={18} />
                    </button>
                </div>
                <p className="text-xs text-slate-400 mt-2 ml-1">将此地址填入 Emby Webhook 插件设置中，实现实时状态推送。</p>
             </div>

             {/* Inline Save Button */}
             <div className="flex justify-end mt-2">
                <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="bg-green-600/90 hover:bg-green-600 backdrop-blur-md border border-white/10 text-white disabled:opacity-70 px-5 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all active:scale-95 shadow-green-500/20"
                >
                    {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />}
                    保存设置
                </button>
             </div>
          </div>
        </section>

        {/* Notification & Reporting */}
        <section className="bg-white/70 dark:bg-slate-900/50 backdrop-blur-md rounded-xl border border-white/50 dark:border-slate-700/50 shadow-sm h-fit">
           <div className="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50 flex items-center justify-between">
             <div className="flex items-center gap-3">
               <Bell size={18} className="text-blue-500" />
               <h3 className="font-bold text-slate-700 dark:text-slate-200">通知与报告</h3>
            </div>
           </div>
           <div className={`p-6 space-y-6 ${config.emby.notifications.enabled ? 'opacity-100' : 'opacity-50 pointer-events-none'}`}>
              <div className="flex items-center justify-between">
                 <span className="text-sm font-medium text-slate-700 dark:text-slate-300">转发 Emby 通知</span>
                 <input 
                    type="checkbox" 
                    checked={config.emby.notifications.forwardToTelegram}
                    onChange={(e) => updateNotifications('forwardToTelegram', e.target.checked)}
                    className="w-5 h-5 rounded text-blue-600 focus:ring-blue-500"
                 />
              </div>
              
              <div className="pt-6 border-t border-slate-100 dark:border-slate-700">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <BarChart3 size={18} className="text-slate-400" />
                        <span className="text-sm font-bold text-slate-700 dark:text-slate-200">观影报告推送频率</span>
                    </div>
                     <div className="flex bg-slate-100/50 dark:bg-slate-900/50 rounded-lg p-1 backdrop-blur-sm">
                     {['daily', 'weekly', 'monthly'].map((freq) => (
                        <button
                           key={freq}
                           onClick={() => updateNotifications('playbackReportingFreq', freq)}
                           className={`py-1.5 px-3 rounded-md text-xs font-bold transition-all ${
                              config.emby.notifications.playbackReportingFreq === freq 
                                ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm' 
                                : 'text-slate-500 hover:text-slate-700'
                           }`}
                        >
                           {freq === 'daily' ? '每天' : freq === 'weekly' ? '每周' : '每月'}
                        </button>
                     ))}
                  </div>
                  </div>
                  
                  {/* Visual Report Widget (Mock) */}
                  <div className="bg-slate-50/50 dark:bg-slate-900/30 border border-slate-100/50 dark:border-slate-700/50 rounded-xl p-4 backdrop-blur-sm">
                     <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <TrendingUp size={16} className="text-blue-500" />
                            <span className="text-xs font-bold text-slate-600 dark:text-slate-300">周报预览 (Weekly Report)</span>
                        </div>
                        <span className="text-xs text-slate-400 font-mono">10/20 - 10/27</span>
                     </div>
                     <div className="flex items-end justify-between gap-3 h-24 mb-3">
                        {[40, 65, 30, 85, 50, 70, 90].map((h, i) => (
                            <div key={i} className="flex-1 bg-blue-200 dark:bg-blue-900/30 rounded-t-sm relative group">
                                <div className="absolute bottom-0 left-0 right-0 bg-blue-500 rounded-t-sm transition-all duration-500 group-hover:bg-blue-400" style={{ height: `${h}%` }}></div>
                            </div>
                        ))}
                     </div>
                     <div className="flex justify-between items-center text-xs text-slate-500 dark:text-slate-400 pt-3 border-t border-slate-200 dark:border-slate-700/50">
                        <div className="flex items-center gap-1.5">
                            <Users size={14} />
                            <span>活跃用户: 12</span>
                        </div>
                        <div>总播放: 48h</div>
                     </div>
                  </div>
              </div>

               {/* Inline Save Button */}
               <div className="flex justify-end mt-2">
                  <button
                      onClick={handleSave}
                      disabled={isSaving}
                      className="bg-blue-600/90 hover:bg-blue-600 backdrop-blur-md border border-white/10 text-white disabled:opacity-70 px-5 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all active:scale-95 shadow-blue-500/20"
                  >
                      {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />}
                      保存设置
                  </button>
               </div>
           </div>
        </section>

        {/* Poster Wall Generation */}
        <section className="bg-white/70 dark:bg-slate-900/50 backdrop-blur-md rounded-xl border border-white/50 dark:border-slate-700/50 shadow-sm lg:col-span-2 h-fit">
           <div className="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50 flex items-center justify-between">
             <div className="flex items-center gap-3">
               <ImageIcon size={18} className="text-purple-500" />
               <h3 className="font-bold text-slate-700 dark:text-slate-200">媒体库海报墙</h3>
            </div>
             <div className="flex items-center gap-3">
               {/* Header Toggle */}
               <div className="relative inline-block w-9 h-5 transition duration-200 ease-in-out rounded-full cursor-pointer">
                  <input 
                    id="posterEnabled" 
                    type="checkbox" 
                    className="peer sr-only"
                    checked={config.emby.posterGeneration.enabled}
                    onChange={(e) => updatePoster('enabled', e.target.checked)}
                  />
                  <label htmlFor="posterEnabled" className="block h-5 overflow-hidden bg-slate-200 dark:bg-slate-700 rounded-full cursor-pointer peer-checked:bg-purple-600 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white dark:after:bg-white after:w-4 after:h-4 after:rounded-full after:shadow-sm after:transition-all peer-checked:after:translate-x-full"></label>
              </div>
            </div>
           </div>
           
           <div className={`p-6 grid grid-cols-1 md:grid-cols-3 gap-8 transition-all duration-300 ${config.emby.posterGeneration.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
              <div className="md:col-span-3 mb-2 flex items-center gap-3 bg-purple-50/50 dark:bg-purple-900/20 p-4 rounded-xl border border-purple-100 dark:border-purple-900/50 backdrop-blur-sm">
                  <Sparkles size={20} className="text-purple-500" />
                  <span className="text-sm text-purple-800 dark:text-purple-300 font-medium">功能说明: 自动将媒体库封面组合成精美的拼图，并设置为媒体目录的封面图。</span>
              </div>

              <div>
                 <label className="block text-xs font-bold text-slate-500 uppercase mb-4 flex items-center gap-1"><Layout size={14}/> 拼图创意模版</label>
                 <div className="grid grid-cols-3 gap-3">
                    <button 
                      onClick={() => updatePoster('template', 'modern_grid')}
                      className={`p-3 border-2 rounded-lg flex flex-col items-center gap-2 hover:border-purple-300 transition-all ${config.emby.posterGeneration.template === 'modern_grid' ? 'border-purple-500 bg-purple-50/50 dark:bg-purple-900/20' : 'border-slate-200/50 dark:border-slate-700/50'}`}
                    >
                       <div className="grid grid-cols-2 gap-0.5 w-10 h-10 shadow-sm">
                          <div className="bg-slate-300 rounded-sm"></div><div className="bg-slate-300 rounded-sm"></div>
                          <div className="bg-slate-300 rounded-sm"></div><div className="bg-slate-300 rounded-sm"></div>
                       </div>
                       <span className="text-xs font-medium text-slate-600 dark:text-slate-400">网格</span>
                    </button>
                    <button 
                      onClick={() => updatePoster('template', 'creative_puzzle')}
                      className={`p-3 border-2 rounded-lg flex flex-col items-center gap-2 hover:border-purple-300 transition-all ${config.emby.posterGeneration.template === 'creative_puzzle' ? 'border-purple-500 bg-purple-50/50 dark:bg-purple-900/20' : 'border-slate-200/50 dark:border-slate-700/50'}`}
                    >
                       <div className="grid grid-cols-3 gap-0.5 w-10 h-10 shadow-sm">
                          <div className="bg-slate-300 col-span-2 row-span-2 rounded-sm"></div>
                          <div className="bg-slate-300 rounded-sm"></div>
                          <div className="bg-slate-300 rounded-sm"></div>
                       </div>
                       <span className="text-xs font-medium text-slate-600 dark:text-slate-400">拼图</span>
                    </button>
                    <button 
                      onClick={() => updatePoster('template', 'classic_list')}
                      className={`p-3 border-2 rounded-lg flex flex-col items-center gap-2 hover:border-purple-300 transition-all ${config.emby.posterGeneration.template === 'classic_list' ? 'border-purple-500 bg-purple-50/50 dark:bg-purple-900/20' : 'border-slate-200/50 dark:border-slate-700/50'}`}
                    >
                       <div className="flex flex-col gap-0.5 w-10 h-10 shadow-sm">
                          <div className="bg-slate-300 h-2.5 w-full rounded-sm"></div>
                          <div className="bg-slate-300 h-2.5 w-full rounded-sm"></div>
                          <div className="bg-slate-300 h-2.5 w-full rounded-sm"></div>
                       </div>
                       <span className="text-xs font-medium text-slate-600 dark:text-slate-400">列表</span>
                    </button>
                 </div>
              </div>

              <div>
                 <label className="block text-xs font-bold text-slate-500 uppercase mb-4">选项设置</label>
                 <div className="space-y-4">
                    <div className="flex items-center gap-3">
                       <input 
                          type="checkbox" 
                          id="overlayName"
                          checked={config.emby.posterGeneration.overlayDirName}
                          onChange={(e) => updatePoster('overlayDirName', e.target.checked)}
                          className="w-4 h-4 rounded text-purple-600 focus:ring-purple-500"
                       />
                       <label htmlFor="overlayName" className="text-sm font-medium text-slate-700 dark:text-slate-300 cursor-pointer select-none flex items-center gap-2">
                          <Folder size={16} className="text-slate-400"/>
                          在封面图中包含目录名称
                       </label>
                    </div>
                 </div>
                 <div className="mt-6">
                     <label className="block text-xs font-bold text-slate-500 uppercase mb-2">排序依据</label>
                     <select 
                        value={config.emby.posterGeneration.sortOrder}
                        onChange={(e) => updatePoster('sortOrder', e.target.value)}
                        className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-purple-500 outline-none text-sm backdrop-blur-sm"
                     >
                        <option value="release_date">上映日期 (新 -&gt; 旧)</option>
                        <option value="added_date">入库时间 (新 -&gt; 旧)</option>
                        <option value="rating">评分 (高 -&gt; 低)</option>
                     </select>
                 </div>
              </div>

              <div>
                 <label className="block text-xs font-bold text-slate-500 uppercase mb-4 flex items-center gap-1"><Clock size={14}/> 生成定时 (Cron)</label>
                 <input
                    type="text"
                    value={config.emby.posterGeneration.cronSchedule}
                    onChange={(e) => updatePoster('cronSchedule', e.target.value)}
                    placeholder="0 0 * * *"
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-purple-500 outline-none text-sm font-mono backdrop-blur-sm"
                 />
                 <p className="text-xs text-slate-400 mt-2 ml-1">默认: 每天午夜生成</p>
              </div>

               {/* Inline Save Button */}
               <div className="md:col-span-3 flex justify-end mt-2">
                  <button
                      onClick={handleSave}
                      disabled={isSaving}
                      className="bg-purple-600/90 hover:bg-purple-600 backdrop-blur-md border border-white/10 text-white disabled:opacity-70 px-5 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all active:scale-95 shadow-purple-500/20"
                  >
                      {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />}
                      保存设置
                  </button>
               </div>
           </div>
        </section>
      </div>
    </div>
  );
};
