import React, { useState } from 'react';
import { AppConfig } from '../types';
import { loadConfig, saveConfig } from '../services/mockConfig';
import { Save, RefreshCw, HardDrive, Globe, Cloud, Zap, Server, Network, Lock } from 'lucide-react';
import { SensitiveInput } from '../components/SensitiveInput';
import { FileSelector } from '../components/FileSelector';

export const StrmView: React.FC = () => {
  const [config, setConfig] = useState<AppConfig>(loadConfig());
  const [isSaving, setIsSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  
  // File Selector State
  const [fileSelectorOpen, setFileSelectorOpen] = useState(false);
  const [activeModule, setActiveModule] = useState<'115'|'123'|'openlist'>('115');

  const updateStrm = (key: string, value: any) => {
    setConfig(prev => ({ ...prev, strm: { ...prev.strm, [key]: value } }));
  };

  const updateWebdav = (key: string, value: any) => {
    setConfig(prev => ({ ...prev, strm: { ...prev.strm, webdav: { ...prev.strm.webdav, [key]: value } } }));
  };

  const handleSave = () => {
    setIsSaving(true);
    saveConfig(config).then(() => {
      setIsSaving(false);
      setToast('STRM 配置已保存 (后端服务已热重载)');
      setTimeout(() => setToast(null), 3000);
    });
  };
  
  const handleTriggerStrm = async () => {
      try {
          await fetch('/api/trigger/strm', { method: 'POST' });
          setToast('后台生成任务已启动');
          setTimeout(() => setToast(null), 3000);
      } catch(e) { alert('触发失败'); }
  };
  
  const openSelector = (module: '115'|'123'|'openlist') => {
    setActiveModule(module);
    setFileSelectorOpen(true);
  };
  
  const handleFileSelect = (id: string, name: string) => {
    if (activeModule === '115') updateStrm('sourceCid115', id);
    if (activeModule === '123') updateStrm('sourceDir123', id); 
    if (activeModule === 'openlist') updateStrm('sourcePathOpenList', id);
  };

  const fillLocalIp = (key: string, suffix: string) => {
    // 自动填入 WebDAV 地址，端口改为 FastAPI 主端口 12808 的子路径 /dav
    updateStrm(key, `http://${window.location.hostname}:12808/dav${suffix}`);
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
      {toast && (
        <div className="fixed top-6 right-6 bg-emerald-500 text-white px-6 py-3 rounded-lg shadow-xl z-50 flex items-center gap-3 font-medium">
          <RefreshCw size={20} className="animate-spin" /> {toast}
        </div>
      )}

      <div className="flex flex-col md:flex-row justify-between items-center border-b border-slate-200 dark:border-slate-700 pb-4 gap-4">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white">STRM 生成</h2>
        <div className="flex gap-2">
            <button onClick={handleTriggerStrm} className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 text-sm shadow-lg shadow-indigo-500/30">
                <Zap size={16} /> 生成文件
            </button>
            <button onClick={handleSave} disabled={isSaving} className="bg-brand-600 hover:bg-brand-700 disabled:opacity-70 text-white px-5 py-2 rounded-lg font-medium flex items-center gap-2 text-sm shadow-lg">
                {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />} 保存设置
            </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Global Config */}
        <div className="lg:col-span-2 bg-slate-50 dark:bg-slate-900/30 p-4 rounded-xl border border-slate-200 dark:border-slate-700 flex items-center justify-between">
           <div className="flex items-center gap-4">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">本地输出目录</label>
              <input type="text" value={config.strm.outputDir} onChange={(e) => updateStrm('outputDir', e.target.value)} className="px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 w-96 text-sm font-mono" />
           </div>
           <div className="flex items-center gap-3">
               <input type="checkbox" checked={config.strm.enabled} onChange={(e) => updateStrm('enabled', e.target.checked)} className="w-4 h-4 rounded text-teal-600" />
               <label className="text-sm font-bold text-slate-700 dark:text-slate-300">启用功能</label>
            </div>
        </div>

        {/* 115 Module */}
        <section className={`bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden ${config.strm.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
           <div className="px-5 py-3 bg-slate-50/80 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
              <HardDrive size={16} className="text-orange-500" />
              <h3 className="font-bold text-slate-700 dark:text-slate-100 text-sm">115 网盘模块</h3>
           </div>
           <div className="p-5 space-y-4">
               <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">源文件夹 (CID)</label>
                  <div className="flex gap-2">
                     <input type="text" value={config.strm.sourceCid115} onChange={(e) => updateStrm('sourceCid115', e.target.value)} className="flex-1 px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm font-mono" />
                     <button onClick={() => openSelector('115')} className="px-3 py-2 bg-slate-100 dark:bg-slate-700 rounded-lg text-sm font-medium">选择</button>
                  </div>
               </div>
               <div>
                  <div className="flex justify-between items-center mb-1.5">
                     <label className="block text-xs font-bold text-slate-500 uppercase">WebDAV 前缀</label>
                     <button onClick={() => fillLocalIp('urlPrefix115', '/115')} className="text-[10px] text-brand-600 hover:underline flex items-center gap-1"><Zap size={10} /> 自动填入</button>
                  </div>
                  <input type="text" value={config.strm.urlPrefix115} onChange={(e) => updateStrm('urlPrefix115', e.target.value)} className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm font-mono" />
               </div>
           </div>
        </section>

        {/* 123 Module */}
        <section className={`bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden ${config.strm.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
           <div className="px-5 py-3 bg-slate-50/80 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
              <Cloud size={16} className="text-blue-500" />
              <h3 className="font-bold text-slate-700 dark:text-slate-100 text-sm">123 云盘模块</h3>
           </div>
           <div className="p-5 space-y-4">
               <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">源文件夹 (File ID)</label>
                  <div className="flex gap-2">
                     <input type="text" value={config.strm.sourceDir123} onChange={(e) => updateStrm('sourceDir123', e.target.value)} className="flex-1 px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm font-mono" />
                     <button onClick={() => openSelector('123')} className="px-3 py-2 bg-slate-100 dark:bg-slate-700 rounded-lg text-sm font-medium">选择</button>
                  </div>
               </div>
               <div>
                  <div className="flex justify-between items-center mb-1.5">
                     <label className="block text-xs font-bold text-slate-500 uppercase">WebDAV 前缀</label>
                     <button onClick={() => fillLocalIp('urlPrefix123', '/123')} className="text-[10px] text-brand-600 hover:underline flex items-center gap-1"><Zap size={10} /> 自动填入</button>
                  </div>
                  <input type="text" value={config.strm.urlPrefix123} onChange={(e) => updateStrm('urlPrefix123', e.target.value)} className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm font-mono" />
               </div>
           </div>
        </section>

        {/* WebDAV Server */}
        <section className={`bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden lg:col-span-2 ${config.strm.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
           <div className="px-5 py-3 bg-slate-50/80 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                 <Network size={16} className="text-teal-500" />
                 <h3 className="font-bold text-slate-700 dark:text-slate-100 text-sm">内置 WebDAV 服务</h3>
              </div>
              <input type="checkbox" checked={config.strm.webdav?.enabled} onChange={(e) => updateWebdav('enabled', e.target.checked)} className="w-4 h-4 rounded text-teal-600" />
           </div>
           
           <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
               <div className="md:col-span-2 bg-teal-50 dark:bg-teal-900/10 p-2 rounded-lg border border-teal-100 dark:border-teal-900/30 text-xs text-teal-700 dark:text-teal-400 mb-2 flex items-center gap-2">
                   <Server size={14} />
                   <span>挂载地址: <strong>http://{window.location.hostname}:12808/dav</strong> (子路径: /115, /123, /openlist)</span>
               </div>
               <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">用户名</label>
                  <input type="text" value={config.strm.webdav?.username} onChange={(e) => updateWebdav('username', e.target.value)} className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm" />
               </div>
               <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">密码</label>
                  <SensitiveInput value={config.strm.webdav?.password || ''} onChange={(e) => updateWebdav('password', e.target.value)} className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm" />
               </div>
           </div>
        </section>
      </div>
      
      {/* File Selector: 传入 mode 参数 */}
      <FileSelector 
         isOpen={fileSelectorOpen} 
         onClose={() => setFileSelectorOpen(false)} 
         onSelect={handleFileSelect}
         title={`选择目录`}
         mode={activeModule || '115'}
      />
    </div>
  );
};
