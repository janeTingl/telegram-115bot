import React, { useState } from 'react';
import { AppConfig, ClassificationRule, MatchConditionType } from '../types';
import { loadConfig, saveConfig, DEFAULT_MOVIE_RULES, DEFAULT_TV_RULES } from '../services/mockConfig';
import { Save, RefreshCw, Cookie, QrCode, Smartphone, FolderInput, Gauge, Trash2, Plus, Film, Type, Globe, Cloud, Tv, LayoutList, FolderOutput, Zap, RotateCcw, X, Edit, Check, BrainCircuit, AlertCircle } from 'lucide-react';
import { SensitiveInput } from '../components/SensitiveInput';
import { FileSelector } from '../components/FileSelector';

// --- 完整的字典数据 (原版找回) ---
const GENRES = [
  { id: '28', name: '动作 (Action)' }, { id: '12', name: '冒险 (Adventure)' }, { id: '16', name: '动画 (Animation)' },
  { id: '35', name: '喜剧 (Comedy)' }, { id: '80', name: '犯罪 (Crime)' }, { id: '99', name: '纪录 (Documentary)' },
  { id: '18', name: '剧情 (Drama)' }, { id: '10751', name: '家庭 (Family)' }, { id: '14', name: '奇幻 (Fantasy)' },
  { id: '36', name: '历史 (History)' }, { id: '27', name: '恐怖 (Horror)' }, { id: '10402', name: '音乐 (Music)' },
  { id: '9648', name: '悬疑 (Mystery)' }, { id: '10749', name: '爱情 (Romance)' }, { id: '878', name: '科幻 (Sci-Fi)' },
  { id: '10770', name: '电视电影 (TV Movie)' }, { id: '53', name: '惊悚 (Thriller)' }, { id: '10752', name: '战争 (War)' },
  { id: '37', name: '西部 (Western)' }, { id: '10762', name: '儿童 (Kids)' }, { id: '10764', name: '真人秀 (Reality)' },
  { id: '10767', name: '脱口秀 (Talk)' }
];

const LANGUAGES = [
  { id: 'zh,cn,bo,za', name: '中文 (Chinese)' }, { id: 'en', name: '英语 (English)' }, { id: 'ja', name: '日语 (Japanese)' },
  { id: 'ko', name: '韩语 (Korean)' }, { id: 'fr', name: '法语 (French)' }, { id: 'de', name: '德语 (German)' },
  { id: 'es', name: '西班牙语 (Spanish)' }, { id: 'ru', name: '俄语 (Russian)' }, { id: 'hi', name: '印地语 (Hindi)' }
];

const COUNTRIES = [
  { id: 'CN,TW,HK', name: '中国/港台 (CN/TW/HK)' }, { id: 'US', name: '美国 (USA)' }, { id: 'JP', name: '日本 (Japan)' },
  { id: 'KR', name: '韩国 (Korea)' }, { id: 'GB', name: '英国 (UK)' }, { id: 'FR', name: '法国 (France)' },
  { id: 'DE', name: '德国 (Germany)' }, { id: 'IN', name: '印度 (India)' }, { id: 'TH', name: '泰国 (Thailand)' }
];

const RENAME_TAGS = [
  { label: '标题', value: '{title}' },
  { label: '年份', value: '{year}' },
  { label: '季号(S)', value: '{season}' },
  { label: '集号(E)', value: '{episode}' },
  { label: '分辨率', value: '{resolution}' },
  { label: '制作组', value: '{group}' },
  { label: '原名', value: '{original_title}' },
  { label: '来源', value: '{source}' },
];

export const CloudOrganizeView: React.FC = () => {
  const [config, setConfig] = useState<AppConfig>(loadConfig());
  const [isSaving, setIsSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  
  // UI State
  const [activeTab, setActiveTab] = useState<'115' | '123' | 'openlist'>('115');
  const [activeRuleTab, setActiveRuleTab] = useState<'movie' | 'tv'>('movie');
  const [fileSelectorOpen, setFileSelectorOpen] = useState(false);
  const [selectorTarget, setSelectorTarget] = useState<'download' | 'source' | 'target' | null>(null);
  
  // Rule Edit State
  const [editingRuleId, setEditingRuleId] = useState<string | null>(null);
  const [tempRule, setTempRule] = useState<ClassificationRule | null>(null);

  // QR Logic (Integrated with Backend)
  const [qrState, setQrState] = useState<'idle' | 'loading' | 'scanned' | 'success' | 'expired'>('idle');
  const [qrImage, setQrImage] = useState<string>('');
  const [qrData, setQrData] = useState<any>(null);

  const handleSave = async () => {
    setIsSaving(true);
    try {
        await saveConfig(config);
        setToast('配置已保存 (后端热重载成功)');
    } catch(e) {
        setToast('保存失败');
    }
    setTimeout(() => {
      setIsSaving(false);
      setTimeout(() => setToast(null), 3000);
    }, 800);
  };

  // 触发后端整理任务
  const handleTriggerOrganize = async () => {
      try {
          await fetch('/api/trigger/organize', { method: 'POST' });
          setToast('整理任务已在后台启动，请查看日志');
          setTimeout(() => setToast(null), 3000);
      } catch(e) {
          alert('触发失败');
      }
  };

  const updateNested = (section: keyof AppConfig, key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], [key]: value }
    }));
  };

  const updateRenameRule = (key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      organize: { 
        ...prev.organize, 
        rename: { ...prev.organize.rename, [key]: value }
      }
    }));
  };
  
  const updateAiConfig = (key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      organize: {
        ...prev.organize,
        ai: { ...prev.organize.ai, [key]: value }
      }
    }));
  };
  
  const updateOrganize = (key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      organize: { ...prev.organize, [key]: value }
    }));
  };

  // Rule Logic
  const getActiveRules = () => activeRuleTab === 'movie' ? config.organize.movieRules : config.organize.tvRules;
  
  const updateRuleList = (newRules: ClassificationRule[]) => {
    setConfig(prev => ({
      ...prev,
      organize: {
        ...prev.organize,
        [activeRuleTab === 'movie' ? 'movieRules' : 'tvRules']: newRules
      }
    }));
  };

  const handleAddRule = () => {
    const newRule: ClassificationRule = {
      id: `custom_${Date.now()}`,
      name: '自定义模块',
      targetCid: '',
      conditions: {}
    };
    setTempRule(newRule);
    setEditingRuleId(newRule.id);
  };

  const handleEditRule = (rule: ClassificationRule) => {
    setTempRule({ ...rule, conditions: { ...rule.conditions } });
    setEditingRuleId(rule.id);
  };

  const handleDeleteRule = (id: string) => {
    updateRuleList(getActiveRules().filter(r => r.id !== id));
  };

  const handleSaveRule = () => {
    if (!tempRule) return;
    const currentRules = getActiveRules();
    const existingIndex = currentRules.findIndex(r => r.id === tempRule.id);
    
    if (existingIndex >= 0) {
      const updated = [...currentRules];
      updated[existingIndex] = tempRule;
      updateRuleList(updated);
    } else {
      updateRuleList([...currentRules, tempRule]);
    }
    setEditingRuleId(null);
    setTempRule(null);
  };

  const handleRestorePresets = () => {
    if (confirm('确定要恢复默认分类模块吗？所有自定义更改将丢失。')) {
      setConfig(prev => ({
        ...prev,
        organize: {
          ...prev.organize,
          movieRules: DEFAULT_MOVIE_RULES,
          tvRules: DEFAULT_TV_RULES
        }
      }));
      setToast('已恢复默认预设模块');
      setTimeout(() => setToast(null), 3000);
    }
  };

  // Temp Rule Editor Helpers
  const toggleTempCondition = (type: MatchConditionType, value: string) => {
    if (!tempRule) return;
    let currentVal = tempRule.conditions[type] || '';
    let items = currentVal.replace(/^!/, '').split(',').filter(Boolean);
    const hasExclusiveFlag = currentVal.startsWith('!');
    
    if (items.includes(value)) items = items.filter(i => i !== value);
    else items.push(value);
    
    let newVal = items.join(',');
    if (newVal && hasExclusiveFlag) newVal = '!' + newVal;
    
    setTempRule({
      ...tempRule,
      conditions: { ...tempRule.conditions, [type]: newVal }
    });
  };
  
  const toggleExclusive = (type: MatchConditionType) => {
    if (!tempRule) return;
    const currentVal = tempRule.conditions[type] || '';
    if (!currentVal) return;
    
    if (currentVal.startsWith('!')) {
      setTempRule({ ...tempRule, conditions: { ...tempRule.conditions, [type]: currentVal.substring(1) } });
    } else {
      setTempRule({ ...tempRule, conditions: { ...tempRule.conditions, [type]: '!' + currentVal } });
    }
  };

  const isSelected = (type: MatchConditionType, value: string) => {
    if (!tempRule) return false;
    const val = tempRule.conditions[type] || '';
    return val.replace(/^!/, '').split(',').includes(value);
  };
  
  const isExclusiveMode = (type: MatchConditionType) => {
     return tempRule?.conditions[type]?.startsWith('!') || false;
  };

  // 真实扫码逻辑 (对接后端)
  const generateRealQr = async () => {
    setQrState('loading');
    try {
        const res = await fetch('/api/115/qrcode/token');
        const data = await res.json();
        if (data.qrcode) {
            setQrImage(data.qrcode); 
            setQrData(data);
            setQrState('idle');
            pollQrStatus(data);
        } else {
            alert('获取二维码失败，请检查网络或日志');
            setQrState('idle');
        }
    } catch(e) { setQrState('idle'); }
  };

  const pollQrStatus = (data: any) => {
      const interval = setInterval(async () => {
          try {
              const res = await fetch(`/api/115/qrcode/status?uid=${data.uid}&time=${data.time}&sign=${data.sign}`);
              const statusData = await res.json();
              
              if (statusData.status === 'scanned') {
                  setQrState('scanned');
              } else if (statusData.status === 'success') {
                  setQrState('success');
                  clearInterval(interval);
                  // 自动刷新配置
                  setTimeout(() => {
                      setConfig(loadConfig());
                      setToast('登录成功，Cookie 已保存');
                      setTimeout(() => setToast(null), 3000);
                  }, 1500);
              } else if (statusData.status === 'expired') {
                  setQrState('expired');
                  clearInterval(interval);
              }
          } catch(e) { clearInterval(interval); }
      }, 2000);
  };
  
  const handleDirSelect = (cid: string, name: string) => {
     if (selectorTarget === 'download') {
         updateNested('cloud115', 'downloadPath', cid);
         updateNested('cloud115', 'downloadDirName', name);
     } else if (selectorTarget === 'source') {
         updateOrganize('sourceCid', cid);
         updateOrganize('sourceDirName', name);
     } else if (selectorTarget === 'target') {
         updateOrganize('targetCid', cid);
         updateOrganize('targetDirName', name);
     }
  };
  
  const fillOpenListIp = () => {
      updateNested('openList', 'url', `http://${window.location.hostname}:5244`);
  };

  const insertTag = (tag: string, target: 'movie' | 'series') => {
      const current = target === 'movie' ? config.organize.rename.movieTemplate : config.organize.rename.seriesTemplate;
      updateRenameRule(target === 'movie' ? 'movieTemplate' : 'seriesTemplate', current + ' ' + tag);
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
      {toast && (
        <div className="fixed top-6 right-6 bg-emerald-500 text-white px-6 py-3 rounded-lg shadow-xl shadow-emerald-500/20 z-50 flex items-center gap-3 font-medium">
          <RefreshCw size={20} className="animate-spin" />
          {toast}
        </div>
      )}

      <div className="flex flex-col md:flex-row justify-between items-center border-b border-slate-200 dark:border-slate-700 pb-4 gap-4">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white">网盘整理</h2>
        <div className="flex gap-2">
            <button
              onClick={handleTriggerOrganize}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 shadow-lg shadow-indigo-500/30 transition-all active:scale-95 text-sm"
            >
              <Zap size={16} /> 立即整理
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="bg-brand-600 hover:bg-brand-700 disabled:opacity-70 text-white px-5 py-2 rounded-lg font-medium flex items-center gap-2 shadow-lg shadow-brand-500/30 transition-all active:scale-95 text-sm"
            >
              {isSaving ? <RefreshCw className="animate-spin" size={16} /> : <Save size={16} />}
              保存设置
            </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        
        {/* Account Management */}
        <section className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden xl:col-span-2">
           <div className="px-5 py-3 bg-slate-50/80 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
              <div className="p-1.5 bg-orange-100 dark:bg-orange-900/30 rounded text-orange-600 dark:text-orange-400">
               <Cookie size={16} />
             </div>
             <h3 className="font-bold text-slate-700 dark:text-slate-100 text-sm">账号与连接</h3>
          </div>
          <div className="p-5">
             <div className="flex gap-4 border-b border-slate-200 dark:border-slate-700 mb-5">
               <button onClick={() => setActiveTab('115')} className={`pb-2 px-3 font-medium text-sm transition-colors border-b-2 ${activeTab === '115' ? 'border-brand-600 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>115 网盘</button>
               <button onClick={() => setActiveTab('123')} className={`pb-2 px-3 font-medium text-sm transition-colors border-b-2 ${activeTab === '123' ? 'border-brand-600 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>123 云盘</button>
               <button onClick={() => setActiveTab('openlist')} className={`pb-2 px-3 font-medium text-sm transition-colors border-b-2 ${activeTab === 'openlist' ? 'border-brand-600 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>OpenList</button>
             </div>

             {/* 115 Settings */}
             {activeTab === '115' && (
               <div className="space-y-5 animate-in fade-in duration-300">
                  <div className="flex flex-wrap gap-2 mb-4">
                    {[
                      { id: 'cookie', label: 'Cookie 导入', icon: Cookie },
                      { id: 'qrcode', label: '扫码获取', icon: QrCode },
                      { id: 'open_app', label: '第三方 App ID', icon: Smartphone }
                    ].map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => updateNested('cloud115', 'loginMethod', tab.id)}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border ${
                          config.cloud115.loginMethod === tab.id
                            ? 'bg-brand-50 border-brand-200 text-brand-600 dark:bg-brand-900/20 dark:border-brand-800 dark:text-brand-400'
                            : 'bg-white dark:bg-slate-700 border-slate-200 dark:border-slate-600 text-slate-500'
                        }`}
                      >
                        <tab.icon size={14} /> {tab.label}
                      </button>
                    ))}
                  </div>

                  {config.cloud115.loginMethod === 'cookie' && (
                    <div className="space-y-2">
                       <label className="text-xs font-semibold text-slate-600 dark:text-slate-400">Cookie 字符串</label>
                       <SensitiveInput
                          multiline
                          value={config.cloud115.cookies}
                          onChange={(e) => updateNested('cloud115', 'cookies', e.target.value)}
                          placeholder="UID=...; CID=...; SEID=..."
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 outline-none font-mono text-sm leading-relaxed resize-none"
                        />
                    </div>
                  )}

                  {(config.cloud115.loginMethod === 'qrcode' || config.cloud115.loginMethod === 'open_app') && (
                     <div className="border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-xl p-6 flex flex-col items-center justify-center bg-slate-50/50 dark:bg-slate-900/30">
                        {config.cloud115.loginMethod === 'qrcode' && (
                            <div className="w-full max-w-sm mb-4">
                                <label className="text-xs font-bold text-slate-500 uppercase mb-2 block flex items-center gap-1">
                                    <Smartphone size={12}/> 模拟登录终端 (App Type)
                                </label>
                                <select 
                                    value={config.cloud115.loginApp || 'web'}
                                    onChange={(e) => updateNested('cloud115', 'loginApp', e.target.value)}
                                    className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 text-sm focus:ring-2 focus:ring-brand-500 outline-none"
                                >
                                    <option value="web">Web 网页版</option>
                                    <option value="android">Android 客户端</option>
                                    <option value="ios">iOS 客户端</option>
                                    <option value="tv">TV 电视端</option>
                                </select>
                            </div>
                        )}

                        {!qrImage ? (
                           <button onClick={generateRealQr} className="px-5 py-2 bg-brand-600 text-white rounded-lg text-sm flex items-center gap-2 hover:bg-brand-700 transition-colors">
                              <QrCode size={16} /> 获取登录二维码
                           </button>
                        ) : (
                           <div className="text-center animate-in fade-in zoom-in duration-300">
                             <img src={qrImage} alt="QR" className="w-32 h-32 rounded-lg border-4 border-white shadow-lg mx-auto mb-3" />
                             <p className="text-xs text-slate-500 font-medium">请使用 115 App 扫码</p>
                             <p className="text-[10px] text-slate-400 mt-1">
                                {qrState === 'scanned' ? '已扫描，请在手机上确认' : qrState === 'success' ? '登录成功！' : qrState === 'expired' ? '二维码已过期' : '等待扫描...'}
                             </p>
                           </div>
                        )}
                     </div>
                  )}

                  <div className="flex gap-6 pt-4 border-t border-slate-100 dark:border-slate-700">
                     <div className="flex-1">
                        <label className="flex items-center text-xs font-semibold text-slate-600 dark:text-slate-400 mb-2">默认下载目录</label>
                        <div className="flex gap-2">
                           <div className="flex-1 px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-400 text-sm flex items-center gap-2">
                             <FolderInput size={16} />
                             {config.cloud115.downloadDirName} 
                             <span className="text-xs opacity-50 ml-auto font-mono">CID: {config.cloud115.downloadPath}</span>
                           </div>
                           <button 
                             onClick={() => { setSelectorTarget('download'); setFileSelectorOpen(true); }}
                             className="px-3 py-2 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 hover:border-brand-500 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-medium transition-colors"
                           >
                             选择
                           </button>
                        </div>
                     </div>
                     <div className="w-1/3">
                        <label className="flex items-center text-xs font-semibold text-slate-600 dark:text-slate-400 mb-2 gap-2">
                          <Gauge size={14} /> QPS 限制
                        </label>
                        <input 
                          type="range" min="0.1" max="1.2" step="0.1"
                          value={config.cloud115.qps}
                          onChange={(e) => updateNested('cloud115', 'qps', parseFloat(e.target.value))}
                          className="w-full h-1.5 bg-slate-200 dark:bg-slate-600 rounded-lg cursor-pointer accent-brand-600 mb-2"
                        />
                        <div className="flex justify-between text-[10px] text-slate-500">
                           <span>0.1</span>
                           <span className="font-bold text-brand-600">{config.cloud115.qps} /s</span>
                           <span>1.2</span>
                        </div>
                     </div>
                  </div>
               </div>
             )}

             {/* 123 Settings (OpenAPI) */}
             {activeTab === '123' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 animate-in fade-in duration-300">
                   <div className="md:col-span-2 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg border border-blue-100 dark:border-blue-900 mb-1">
                      <h4 className="font-bold text-blue-700 dark:text-blue-400 text-xs mb-0.5">OpenAPI 授权模式</h4>
                      <p className="text-[10px] text-blue-600 dark:text-blue-300">请前往 123 云盘开放平台申请应用，填入 Client ID 和 Client Secret 进行授权连接。</p>
                   </div>
                   
                   <div>
                      <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">客户端 ID (Client ID)</label>
                      <input 
                         type="text"
                         value={config.cloud123.clientId}
                         onChange={(e) => updateNested('cloud123', 'clientId', e.target.value)}
                         className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 outline-none text-sm"
                      />
                   </div>
                   <div>
                      <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">客户端密钥 (Client Secret)</label>
                      <SensitiveInput 
                         value={config.cloud123.clientSecret}
                         onChange={(e) => updateNested('cloud123', 'clientSecret', e.target.value)}
                         className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 outline-none text-sm"
                      />
                   </div>
                </div>
             )}

             {/* OpenList Settings */}
             {activeTab === 'openlist' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 animate-in fade-in duration-300">
                   <div className="md:col-span-2 bg-cyan-50 dark:bg-cyan-900/20 p-3 rounded-lg border border-cyan-100 dark:border-cyan-800 mb-1 flex items-start gap-3">
                       <AlertCircle size={16} className="text-cyan-600 dark:text-cyan-400 shrink-0 mt-0.5" />
                       <div className="text-[10px] text-cyan-800 dark:text-cyan-200">
                         <strong>重要提示：</strong> 适用于 Alist 兼容接口。
                       </div>
                   </div>

                   <div className="md:col-span-2">
                      <div className="flex justify-between items-center mb-1.5">
                        <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400">服务器地址 (Alist URL)</label>
                        <button onClick={fillOpenListIp} className="text-[10px] text-brand-600 hover:underline flex items-center gap-1"><Zap size={10} /> 自动填入</button>
                      </div>
                      <input 
                         type="text"
                         value={config.openList.url}
                         onChange={(e) => updateNested('openList', 'url', e.target.value)}
                         placeholder="http://192.168.1.5:5244"
                         className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 outline-none text-sm font-mono"
                      />
                   </div>
                   <div>
                      <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">用户名</label>
                      <input 
                         type="text"
                         value={config.openList.username}
                         onChange={(e) => updateNested('openList', 'username', e.target.value)}
                         className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 outline-none text-sm"
                      />
                   </div>
                   <div>
                      <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">密码</label>
                      <SensitiveInput 
                         value={config.openList.password || ''}
                         onChange={(e) => updateNested('openList', 'password', e.target.value)}
                         className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 outline-none text-sm"
                      />
                   </div>
                </div>
             )}
          </div>
        </section>

        {/* Organize Rules Engine */}
        {activeTab === '115' && (
        <section className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden xl:col-span-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
           <div className="px-5 py-3 bg-slate-50/80 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-indigo-100 dark:bg-indigo-900/30 rounded text-indigo-600 dark:text-indigo-400">
               <Film size={16} />
             </div>
              <h3 className="font-bold text-slate-700 dark:text-slate-100 text-sm">分类与重命名规则 (TMDB)</h3>
            </div>
             <div className="flex items-center gap-3">
               <div className="relative inline-block w-9 h-5 transition duration-200 ease-in-out rounded-full cursor-pointer">
                  <input 
                    id="organizeEnabled" 
                    type="checkbox" 
                    className="peer sr-only"
                    checked={config.organize.enabled}
                    onChange={(e) => setConfig({...config, organize: {...config.organize, enabled: e.target.checked}})}
                  />
                  <label htmlFor="organizeEnabled" className="block h-5 overflow-hidden bg-slate-200 dark:bg-slate-600 rounded-full cursor-pointer peer-checked:bg-indigo-600 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:w-4 after:h-4 after:rounded-full after:shadow-sm after:transition-all peer-checked:after:translate-x-full"></label>
              </div>
            </div>
          </div>
          
          <div className="p-5 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-slate-50 dark:bg-slate-900/30 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                 <div>
                    <label className="flex items-center text-xs font-bold text-slate-500 uppercase mb-2">源目录 (Source)</label>
                    <div className="flex gap-2">
                       <div className="flex-1 px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-sm flex items-center gap-2">
                         <FolderInput size={16} />
                         {config.organize.sourceDirName || '默认下载目录'}
                       </div>
                       <button onClick={() => { setSelectorTarget('source'); setFileSelectorOpen(true); }} className="px-3 py-2 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 hover:border-indigo-500 rounded-lg text-sm font-medium">选择</button>
                    </div>
                 </div>
                 <div>
                    <label className="flex items-center text-xs font-bold text-slate-500 uppercase mb-2">目标目录 (Target)</label>
                    <div className="flex gap-2">
                       <div className="flex-1 px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-sm flex items-center gap-2">
                         <FolderOutput size={16} />
                         {config.organize.targetDirName || '整理存放目录'}
                       </div>
                       <button onClick={() => { setSelectorTarget('target'); setFileSelectorOpen(true); }} className="px-3 py-2 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 hover:border-indigo-500 rounded-lg text-sm font-medium">选择</button>
                    </div>
                 </div>
            </div>

            <div className={`transition-all duration-300 ${config.organize.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
               <div className="mb-6 border-b border-slate-100 dark:border-slate-700 pb-6">
                  <div className="flex items-center justify-between mb-3">
                     <div className="flex items-center gap-2">
                        <BrainCircuit size={16} className="text-pink-500" />
                        <h4 className="font-bold text-slate-700 dark:text-slate-200 text-sm">AI 智能重命名 (大模型辅助)</h4>
                     </div>
                     <input 
                        type="checkbox" 
                        checked={config.organize.ai.enabled}
                        onChange={(e) => updateAiConfig('enabled', e.target.checked)}
                        className="w-4 h-4 rounded text-pink-600 focus:ring-pink-500"
                     />
                  </div>
                  {config.organize.ai.enabled && (
                     <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-pink-50 dark:bg-pink-900/10 p-4 rounded-xl border border-pink-100 dark:border-pink-900/50">
                        <div>
                           <label className="block text-xs font-bold text-slate-500 uppercase mb-1">服务商</label>
                           <select className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm">
                              <option value="openai">OpenAI</option>
                           </select>
                        </div>
                        <div>
                           <label className="block text-xs font-bold text-slate-500 uppercase mb-1">API Key</label>
                           <SensitiveInput 
                              value={config.organize.ai.apiKey}
                              onChange={(e) => updateAiConfig('apiKey', e.target.value)}
                              className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm font-mono"
                           />
                        </div>
                        <div>
                           <label className="block text-xs font-bold text-slate-500 uppercase mb-1">模型名称</label>
                           <input 
                              type="text"
                              value={config.organize.ai.model}
                              onChange={(e) => updateAiConfig('model', e.target.value)}
                              placeholder="gpt-3.5-turbo"
                              className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm font-mono"
                           />
                        </div>
                     </div>
                  )}
               </div>

               <div className="mb-6 grid grid-cols-1 gap-6 border-b border-slate-100 dark:border-slate-700 pb-6">
                 <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-1">TMDB API 密钥</label>
                    <SensitiveInput
                          value={config.tmdb.apiKey}
                          onChange={(e) => updateNested('tmdb', 'apiKey', e.target.value)}
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none text-sm font-mono"
                    />
                 </div>

                 <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="space-y-3">
                       <label className="flex items-center text-xs font-semibold text-slate-500 uppercase tracking-wide">电影重命名规则</label>
                       <div className="flex flex-wrap gap-2 mb-2">
                          {RENAME_TAGS.map(tag => (
                             <button key={tag.value} onClick={() => insertTag(tag.value, 'movie')} className="px-2 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs rounded hover:bg-indigo-100 hover:text-indigo-600 transition-colors">
                                {tag.label}
                             </button>
                          ))}
                       </div>
                       <div className="flex items-center">
                          <input 
                             type="text" 
                             value={config.organize.rename.movieTemplate} 
                             onChange={(e) => updateRenameRule('movieTemplate', e.target.value)} 
                             className="flex-1 px-3 py-2 rounded-l-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 text-sm font-mono focus:ring-2 focus:ring-indigo-500 outline-none border-r-0" 
                          />
                          <div className="px-3 py-2 bg-indigo-50 dark:bg-indigo-900/30 border border-l-0 border-indigo-200 dark:border-indigo-800 text-indigo-600 dark:text-indigo-400 text-sm font-mono font-bold rounded-r-lg select-none whitespace-nowrap">
                             [TMDB-{'{id}'}]
                          </div>
                       </div>
                    </div>
                    
                    <div className="space-y-3">
                       <label className="flex items-center text-xs font-semibold text-slate-500 uppercase tracking-wide">剧集重命名规则</label>
                       <div className="flex flex-wrap gap-2 mb-2">
                          {RENAME_TAGS.map(tag => (
                             <button key={tag.value} onClick={() => insertTag(tag.value, 'series')} className="px-2 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs rounded hover:bg-indigo-100 hover:text-indigo-600 transition-colors">
                                {tag.label}
                             </button>
                          ))}
                       </div>
                       <div className="flex items-center">
                          <input 
                             type="text" 
                             value={config.organize.rename.seriesTemplate} 
                             onChange={(e) => updateRenameRule('seriesTemplate', e.target.value)} 
                             className="flex-1 px-3 py-2 rounded-l-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 text-sm font-mono focus:ring-2 focus:ring-indigo-500 outline-none border-r-0" 
                          />
                          <div className="px-3 py-2 bg-indigo-50 dark:bg-indigo-900/30 border border-l-0 border-indigo-200 dark:border-indigo-800 text-indigo-600 dark:text-indigo-400 text-sm font-mono font-bold rounded-r-lg select-none whitespace-nowrap">
                             [TMDB-{'{id}'}]
                          </div>
                       </div>
                    </div>
                 </div>
               </div>

               {/* Modules / Rules System */}
               <div>
                  <div className="flex items-center justify-between mb-4">
                     <div className="flex gap-2 bg-slate-100 dark:bg-slate-900/50 p-1 rounded-lg">
                         <button 
                            onClick={() => { setActiveRuleTab('movie'); setEditingRuleId(null); }}
                            className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all flex items-center gap-2 ${activeRuleTab === 'movie' ? 'bg-white dark:bg-slate-700 shadow text-indigo-600 dark:text-indigo-400' : 'text-slate-500 hover:text-slate-700'}`}
                         >
                           <Film size={14} /> 电影模块
                         </button>
                         <button 
                            onClick={() => { setActiveRuleTab('tv'); setEditingRuleId(null); }}
                            className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all flex items-center gap-2 ${activeRuleTab === 'tv' ? 'bg-white dark:bg-slate-700 shadow text-indigo-600 dark:text-indigo-400' : 'text-slate-500 hover:text-slate-700'}`}
                         >
                           <Tv size={14} /> 剧集模块
                         </button>
                     </div>
                     <div className="flex gap-2">
                        <button 
                           onClick={handleRestorePresets}
                           className="px-3 py-1.5 text-xs font-medium text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg flex items-center gap-1 transition-colors"
                        >
                           <RotateCcw size={12} /> 恢复预设
                        </button>
                        <button 
                           onClick={handleAddRule}
                           className="px-3 py-1.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg flex items-center gap-1 shadow-sm transition-colors"
                        >
                           <Plus size={12} /> 添加模块
                        </button>
                     </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                     {getActiveRules().map((rule) => (
                        <div key={rule.id} className="bg-slate-50 dark:bg-slate-900/30 border border-slate-200 dark:border-slate-700 rounded-xl p-3 group hover:border-indigo-400 dark:hover:border-indigo-500 transition-colors relative">
                           <div className="flex justify-between items-start mb-2">
                              <h4 className="font-bold text-slate-700 dark:text-slate-200 text-sm">{rule.name}</h4>
                              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                 <button onClick={() => handleEditRule(rule)} className="p-1 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded"><Edit size={14} /></button>
                                 <button onClick={() => handleDeleteRule(rule.id)} className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded"><Trash2 size={14} /></button>
                              </div>
                           </div>
                           <div className="space-y-1.5">
                              <div className="flex items-center gap-2 text-[10px]">
                                 <LayoutList size={12} className="text-slate-400" />
                                 <span className="text-slate-500 truncate">
                                    {rule.conditions.genre_ids 
                                      ? GENRES.filter(g => rule.conditions.genre_ids?.split(',').includes(g.id)).map(g => g.name.split(' ')[0]).join(', ')
                                      : '全部类型'}
                                 </span>
                              </div>
                              <div className="flex items-center gap-2 text-[10px]">
                                 <Globe size={12} className="text-slate-400" />
                                 <span className="text-slate-500 truncate">
                                    {rule.conditions.origin_country 
                                      ? (rule.conditions.origin_country.startsWith('!') ? '排除: ' : '') + COUNTRIES.filter(c => rule.conditions.origin_country?.replace('!','').split(',').includes(c.id)).map(c => c.name.split(' ')[0]).join(', ')
                                      : '全部地区'}
                                 </span>
                              </div>
                           </div>
                        </div>
                     ))}
                  </div>
               </div>
            </div>
          </div>
        </section>
        )}
      </div>

      {/* Edit Rule Modal */}
      {editingRuleId && tempRule && (
         <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
             <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden border border-slate-200 dark:border-slate-700 flex flex-col max-h-[90vh]">
                 <div className="p-4 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
                    <h3 className="font-bold text-slate-700 dark:text-slate-200 text-sm">编辑模块: {tempRule.name}</h3>
                    <button onClick={() => setEditingRuleId(null)} className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-full transition-colors"><X size={20} className="text-slate-400" /></button>
                 </div>
                 
                 <div className="p-6 overflow-y-auto custom-scrollbar space-y-6">
                     <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-2">模块名称 (即文件夹名)</label>
                        <input 
                           type="text" 
                           value={tempRule.name}
                           onChange={(e) => setTempRule({...tempRule, name: e.target.value})}
                           className="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none font-bold text-sm"
                        />
                     </div>
                     
                     <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Genre Selection */}
                        <div className="space-y-2">
                           <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-700 pb-2">
                              <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-1"><LayoutList size={12}/> 类型</label>
                           </div>
                           <div className="max-h-60 overflow-y-auto pr-1 custom-scrollbar space-y-1">
                               {GENRES.map(g => (
                                  <label key={g.id} className={`flex items-center gap-2 p-2 rounded cursor-pointer transition-colors border ${isSelected('genre_ids', g.id) ? 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800' : 'border-transparent hover:bg-slate-50 dark:hover:bg-slate-700/50'}`}>
                                      <input type="checkbox" className="rounded text-indigo-600" checked={isSelected('genre_ids', g.id)} onChange={() => toggleTempCondition('genre_ids', g.id)} />
                                      <span className="text-xs font-medium text-slate-700 dark:text-slate-300">{g.name}</span>
                                  </label>
                               ))}
                           </div>
                        </div>
                        
                         {/* Region Selection */}
                        <div className="space-y-2">
                           <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-700 pb-2">
                              <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-1"><Globe size={12}/> 地区</label>
                              <button 
                                 onClick={() => toggleExclusive('origin_country')} 
                                 className={`text-[10px] px-2 py-0.5 rounded border transition-colors ${isExclusiveMode('origin_country') ? 'bg-red-50 text-red-600 border-red-200 dark:bg-red-900/20 dark:border-red-800' : 'bg-slate-50 text-slate-400 border-slate-200 dark:bg-slate-700 dark:border-slate-600'}`}
                              >
                                 {isExclusiveMode('origin_country') ? '模式: 排除所选' : '模式: 包含所选'}
                              </button>
                           </div>
                           <div className="max-h-60 overflow-y-auto pr-1 custom-scrollbar space-y-1">
                               {COUNTRIES.map(c => (
                                  <label key={c.id} className={`flex items-center gap-2 p-2 rounded cursor-pointer transition-colors border ${isSelected('origin_country', c.id) ? 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800' : 'border-transparent hover:bg-slate-50 dark:hover:bg-slate-700/50'}`}>
                                      <input type="checkbox" className="rounded text-indigo-600" checked={isSelected('origin_country', c.id)} onChange={() => toggleTempCondition('origin_country', c.id)} />
                                      <span className="text-xs font-medium text-slate-700 dark:text-slate-300">{c.name}</span>
                                  </label>
                               ))}
                           </div>
                        </div>

                         {/* Language Selection */}
                         <div className="space-y-2">
                           <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-700 pb-2">
                              <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-1"><Type size={12}/> 语言</label>
                              <button 
                                 onClick={() => toggleExclusive('original_language')} 
                                 className={`text-[10px] px-2 py-0.5 rounded border transition-colors ${isExclusiveMode('original_language') ? 'bg-red-50 text-red-600 border-red-200 dark:bg-red-900/20 dark:border-red-800' : 'bg-slate-50 text-slate-400 border-slate-200 dark:bg-slate-700 dark:border-slate-600'}`}
                              >
                                 {isExclusiveMode('original_language') ? '模式: 排除所选' : '模式: 包含所选'}
                              </button>
                           </div>
                           <div className="max-h-60 overflow-y-auto pr-1 custom-scrollbar space-y-1">
                               {LANGUAGES.map(l => (
                                  <label key={l.id} className={`flex items-center gap-2 p-2 rounded cursor-pointer transition-colors border ${isSelected('original_language', l.id) ? 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800' : 'border-transparent hover:bg-slate-50 dark:hover:bg-slate-700/50'}`}>
                                      <input type="checkbox" className="rounded text-indigo-600" checked={isSelected('original_language', l.id)} onChange={() => toggleTempCondition('original_language', l.id)} />
                                      <span className="text-xs font-medium text-slate-700 dark:text-slate-300">{l.name}</span>
                                  </label>
                               ))}
                           </div>
                        </div>
                     </div>
                 </div>

                 <div className="p-4 border-t border-slate-100 dark:border-slate-700 flex justify-end gap-3 bg-slate-50 dark:bg-slate-900/50">
                    <button onClick={() => setEditingRuleId(null)} className="px-4 py-2 text-slate-500 hover:text-slate-700 text-sm font-medium">取消</button>
                    <button onClick={handleSaveRule} className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-bold flex items-center gap-2 shadow-lg shadow-indigo-500/20 transition-all active:scale-95">
                       <Check size={16} /> 保存模块
                    </button>
                 </div>
             </div>
         </div>
      )}

      <FileSelector 
         isOpen={fileSelectorOpen} 
         onClose={() => setFileSelectorOpen(false)} 
         onSelect={handleDirSelect} 
         title={`选择 ${selectorTarget === 'target' ? '存放目录' : selectorTarget === 'source' ? '源目录' : '下载目录'}`}
         mode={activeTab === 'openlist' ? 'openlist' : (activeTab === '123' ? '123' : '115')}
      />
    </div>
  );
};
