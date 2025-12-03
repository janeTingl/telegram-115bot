
import React, { useState } from 'react';
import { AppConfig } from '../types';
import { loadConfig, saveConfig } from '../services/mockConfig';
import { Tooltip } from '../components/Tooltip';
import { Save, RefreshCw, FileVideo, HardDrive, Link as LinkIcon, Globe, Cloud, Zap, Server, Network, Lock } from 'lucide-react';
import { SensitiveInput } from '../components/SensitiveInput';
import { FileSelector } from '../components/FileSelector';

export const StrmView: React.FC = () => {
  const [config, setConfig] = useState<AppConfig>(loadConfig());
  const [isSaving, setIsSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  
  // File Selector
  const [fileSelectorOpen, setFileSelectorOpen] = useState(false);
  const [activeModule, setActiveModule] = useState<'115'|'123'|'openlist'|null>(null);

  const updateNested = (section: keyof AppConfig, key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], [key]: value }
    }));
  };
  
  const updateStrm = (key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      strm: { ...prev.strm, [key]: value }
    }));
  };

  const updateWebdav = (key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      strm: { 
          ...prev.strm, 
          webdav: { ...prev.strm.webdav, [key]: value } 
      }
    }));
  };

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => {
      saveConfig(config);
      setIsSaving(false);
      setToast('STRM 生成配置已保存');
      setTimeout(() => setToast(null), 3000);
    }, 800);
  };
  
  const openSelector = (module: '115'|'123'|'openlist') => {
    setActiveModule(module);
    setFileSelectorOpen(true);
  };
  
  const handleFileSelect = (id: string, name: string) => {
    if (activeModule === '115') updateStrm('sourceCid115', id);
    if (activeModule === '123') updateStrm('sourceDir123', id === '0' ? '/' : `/${name}`); 
    if (activeModule === 'openlist') updateStrm('sourcePathOpenList', id === '0' ? '/' : `/${name}`);
  };

  const fillLocalIp = (key: string, port: string, suffix: string) => {
    const ip = window.location.hostname;
    updateStrm(key, `http://${ip}:${port}${suffix}`);
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
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white tracking-tight drop-shadow-sm">STRM 生成</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Global Config */}
        <div className="lg:col-span-2 bg-slate-50/80 dark:bg-slate-800/50 backdrop-blur-md rounded-xl border border-slate-200/50 dark:border-slate-700/50 shadow-sm overflow-hidden">
           <div className="p-6 flex items-center justify-between">
              <div className="flex items-center gap-4">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">本地输出目录</label>
                  <input 
                    type="text" 
                    value={config.strm.outputDir}
                    onChange={(e) => updateStrm('outputDir', e.target.value)}
                    className="px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 w-96 text-sm font-mono focus:ring-2 focus:ring-teal-500 outline-none backdrop-blur-sm"
                  />
              </div>
              <div className="flex items-center gap-3">
                   {/* Header Toggle */}
                   <div className="relative inline-block w-9 h-5 transition duration-200 ease-in-out rounded-full cursor-pointer">
                      <input 
                        id="strmEnabled" 
                        type="checkbox" 
                        className="peer sr-only"
                        checked={config.strm.enabled}
                        onChange={(e) => updateStrm('enabled', e.target.checked)}
                      />
                      <label htmlFor="strmEnabled" className="block h-5 overflow-hidden bg-slate-200 dark:bg-slate-700 rounded-full cursor-pointer peer-checked:bg-teal-600 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white dark:after:bg-white after:w-4 after:h-4 after:rounded-full after:shadow-sm after:transition-all peer-checked:after:translate-x-full"></label>
                  </div>
                  <label htmlFor="strmEnabled" className="text-sm font-bold text-slate-700 dark:text-slate-300 cursor-pointer select-none">启用功能</label>
              </div>
              
               <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="bg-brand-600/90 hover:bg-brand-600 backdrop-blur-md border border-white/10 text-white disabled:opacity-70 px-5 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all active:scale-95 ml-auto shadow-brand-500/20"
                >
                  {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />}
                  保存设置
                </button>
           </div>
        </div>

        {/* 115 Module */}
        <section className={`bg-white/80 dark:bg-slate-800/50 backdrop-blur-md rounded-xl border border-slate-200/50 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all duration-300 ${config.strm.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
           <div className="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50 flex items-center gap-3">
              <HardDrive size={18} className="text-orange-500" />
              <h3 className="font-bold text-slate-700 dark:text-slate-200">115 网盘模块</h3>
           </div>
           <div className="p-6 space-y-6">
               <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">STRM生成文件夹</label>
                  <div className="flex gap-3">
                     <input
                       type="text"
                       value={config.strm.sourceCid115}
                       onChange={(e) => updateStrm('sourceCid115', e.target.value)}
                       className="flex-1 px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 font-mono text-sm backdrop-blur-sm"
                     />
                     <button onClick={() => openSelector('115')} className="px-4 py-2.5 bg-slate-100/50 dark:bg-slate-700/50 rounded-lg text-sm font-medium hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors backdrop-blur-sm">选择</button>
                  </div>
               </div>
               <div>
                  <div className="flex justify-between items-center mb-2">
                     <label className="block text-xs font-bold text-slate-500 uppercase">路径前缀</label>
                     <button onClick={() => fillLocalIp('urlPrefix115', '9527', '/d/115')} className="text-xs text-brand-600 hover:text-brand-500 flex items-center gap-1 font-medium"><Zap size={12} /> 自动填入</button>
                  </div>
                  <input
                    type="text"
                    value={config.strm.urlPrefix115}
                    onChange={(e) => updateStrm('urlPrefix115', e.target.value)}
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 font-mono text-sm backdrop-blur-sm"
                  />
               </div>

                {/* Inline Save Button */}
               <div className="flex justify-end mt-2">
                  <button
                      onClick={handleSave}
                      disabled={isSaving}
                      className="bg-orange-600/90 hover:bg-orange-600 backdrop-blur-md border border-white/10 text-white disabled:opacity-70 px-5 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all active:scale-95 shadow-orange-500/20"
                  >
                      {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />}
                      保存设置
                  </button>
               </div>
           </div>
        </section>

        {/* 123 Module */}
        <section className={`bg-white/80 dark:bg-slate-800/50 backdrop-blur-md rounded-xl border border-slate-200/50 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all duration-300 ${config.strm.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
           <div className="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50 flex items-center gap-3">
              <Cloud size={18} className="text-blue-500" />
              <h3 className="font-bold text-slate-700 dark:text-slate-200">123 云盘模块</h3>
           </div>
           <div className="p-6 space-y-6">
               <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">STRM生成文件夹</label>
                  <div className="flex gap-3">
                     <input
                       type="text"
                       value={config.strm.sourceDir123}
                       onChange={(e) => updateStrm('sourceDir123', e.target.value)}
                       className="flex-1 px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 font-mono text-sm backdrop-blur-sm"
                     />
                     <button onClick={() => openSelector('123')} className="px-4 py-2.5 bg-slate-100/50 dark:bg-slate-700/50 rounded-lg text-sm font-medium hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors backdrop-blur-sm">选择</button>
                  </div>
               </div>
               <div>
                  <div className="flex justify-between items-center mb-2">
                     <label className="block text-xs font-bold text-slate-500 uppercase">路径前缀</label>
                     <button onClick={() => fillLocalIp('urlPrefix123', '9527', '/d/123')} className="text-xs text-brand-600 hover:text-brand-500 flex items-center gap-1 font-medium"><Zap size={12} /> 自动填入</button>
                  </div>
                  <input
                    type="text"
                    value={config.strm.urlPrefix123}
                    onChange={(e) => updateStrm('urlPrefix123', e.target.value)}
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 font-mono text-sm backdrop-blur-sm"
                  />
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

        {/* OpenList Module */}
        <section className={`bg-white/80 dark:bg-slate-800/50 backdrop-blur-md rounded-xl border border-slate-200/50 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all duration-300 ${config.strm.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
           <div className="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50 flex items-center gap-3">
              <Globe size={18} className="text-cyan-500" />
              <h3 className="font-bold text-slate-700 dark:text-slate-200">OpenList 挂载模块</h3>
           </div>
           <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
               <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">STRM生成文件夹</label>
                  <div className="flex gap-3">
                     <input
                       type="text"
                       value={config.strm.sourcePathOpenList}
                       onChange={(e) => updateStrm('sourcePathOpenList', e.target.value)}
                       className="flex-1 px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 font-mono text-sm backdrop-blur-sm"
                     />
                     <button onClick={() => openSelector('openlist')} className="px-4 py-2.5 bg-slate-100/50 dark:bg-slate-700/50 rounded-lg text-sm font-medium hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors backdrop-blur-sm">选择</button>
                  </div>
               </div>
               <div>
                  <div className="flex justify-between items-center mb-2">
                     <label className="block text-xs font-bold text-slate-500 uppercase">路径前缀</label>
                     <button onClick={() => fillLocalIp('urlPrefixOpenList', '5244', '/d')} className="text-xs text-brand-600 hover:text-brand-500 flex items-center gap-1 font-medium"><Zap size={12} /> 自动填入</button>
                  </div>
                  <input
                    type="text"
                    value={config.strm.urlPrefixOpenList}
                    onChange={(e) => updateStrm('urlPrefixOpenList', e.target.value)}
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 font-mono text-sm backdrop-blur-sm"
                  />
               </div>
               
               {/* Inline Save Button */}
               <div className="md:col-span-2 flex justify-end mt-2">
                  <button
                      onClick={handleSave}
                      disabled={isSaving}
                      className="bg-cyan-600/90 hover:bg-cyan-600 backdrop-blur-md border border-white/10 text-white disabled:opacity-70 px-5 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all active:scale-95 shadow-cyan-500/20"
                  >
                      {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />}
                      保存设置
                  </button>
               </div>
           </div>
        </section>

        {/* WebDAV Server */}
        <section className={`bg-white/80 dark:bg-slate-800/50 backdrop-blur-md rounded-xl border border-slate-200/50 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all duration-300 ${config.strm.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
           <div className="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50 flex items-center justify-between">
              <div className="flex items-center gap-3">
                 <Network size={18} className="text-teal-500" />
                 <h3 className="font-bold text-slate-700 dark:text-slate-200">WebDAV 服务 (挂载 STRM)</h3>
              </div>
              <div className="flex items-center gap-3">
                  {/* Header Toggle */}
                  <div className="relative inline-block w-9 h-5 transition duration-200 ease-in-out rounded-full cursor-pointer">
                      <input 
                        id="webdavEnabled" 
                        type="checkbox" 
                        className="peer sr-only"
                        checked={config.strm.webdav?.enabled || false}
                        onChange={(e) => updateWebdav('enabled', e.target.checked)}
                      />
                      <label htmlFor="webdavEnabled" className="block h-5 overflow-hidden bg-slate-200 dark:bg-slate-700 rounded-full cursor-pointer peer-checked:bg-teal-600 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white dark:after:bg-white after:w-4 after:h-4 after:rounded-full after:shadow-sm after:transition-all peer-checked:after:translate-x-full"></label>
                  </div>
              </div>
           </div>
           
           <div className={`p-6 grid grid-cols-1 md:grid-cols-2 gap-6 ${config.strm.webdav?.enabled ? 'opacity-100' : 'opacity-50 pointer-events-none'}`}>
               <div className="md:col-span-2 bg-teal-50/50 dark:bg-teal-900/10 p-3 rounded-xl border border-teal-100/50 dark:border-teal-900/30 text-sm text-teal-700 dark:text-teal-400 mb-2 flex items-center gap-3 backdrop-blur-sm">
                   <Server size={18} />
                   <span>
                       WebDAV 挂载地址: <strong>http://{window.location.hostname}:12808/dav</strong>
                   </span>
               </div>
               
               <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">内部端口 (Internal Port)</label>
                  <input
                    type="text"
                    value={config.strm.webdav?.port}
                    onChange={(e) => updateWebdav('port', e.target.value)}
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 font-mono text-sm backdrop-blur-sm"
                  />
               </div>
               
               <div className="flex items-end mb-3">
                   <div className="flex items-center gap-2">
                       <input 
                          type="checkbox" 
                          id="webdavReadOnly"
                          checked={config.strm.webdav?.readOnly || false}
                          onChange={(e) => updateWebdav('readOnly', e.target.checked)}
                          className="w-4 h-4 rounded text-teal-600 focus:ring-teal-500"
                       />
                       <label htmlFor="webdavReadOnly" className="text-sm font-medium text-slate-700 dark:text-slate-300 cursor-pointer select-none flex items-center gap-2">
                          <Lock size={16} className="text-slate-400"/>
                          只读模式 (Read Only)
                       </label>
                   </div>
               </div>
               
               <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">用户名</label>
                  <input
                    type="text"
                    value={config.strm.webdav?.username}
                    onChange={(e) => updateWebdav('username', e.target.value)}
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 text-sm backdrop-blur-sm"
                  />
               </div>
               
               <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">密码</label>
                  <SensitiveInput
                    value={config.strm.webdav?.password || ''}
                    onChange={(e) => updateWebdav('password', e.target.value)}
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 text-sm backdrop-blur-sm"
                  />
               </div>
               
               {/* Inline Save Button */}
               <div className="md:col-span-2 flex justify-end mt-2">
                  <button
                      onClick={handleSave}
                      disabled={isSaving}
                      className="bg-teal-600/90 hover:bg-teal-600 backdrop-blur-md border border-white/10 text-white disabled:opacity-70 px-5 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all active:scale-95 shadow-teal-500/20"
                  >
                      {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />}
                      保存设置
                  </button>
               </div>
           </div>
        </section>
      </div>
      
      <FileSelector 
         isOpen={fileSelectorOpen} 
         onClose={() => setFileSelectorOpen(false)} 
         onSelect={handleFileSelect}
         title={`选择 ${activeModule === '115' ? '115 文件夹' : '目录'}`}
      />
    </div>
  );
};
