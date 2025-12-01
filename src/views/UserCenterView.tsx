import React, { useState } from 'react';
import { 
  Activity, Database, Wifi, Shield, Save, KeyRound, User, 
  RefreshCw, Smartphone, Zap, Server, Lock, Globe 
} from 'lucide-react';
// 请确保 types.ts 和 services/api.ts 存在，或者使用之前我在 App.tsx 里教你的内联定义方式
// 这里为了演示，我把 loadConfig/saveConfig 的逻辑内联进来，保证你不报错

// === 类型与模拟 API (如果你有独立文件可删除这部分) ===
interface AppConfig { user?: any; system?: any; cloud115?: any; proxy?: any; [key: string]: any; }
const loadConfig = (): AppConfig => {
  try { return JSON.parse(localStorage.getItem('app_config') || '{}'); } catch { return {}; }
};
const saveConfig = async (cfg: AppConfig) => {
  localStorage.setItem('app_config', JSON.stringify(cfg));
  // await fetch('/api/config', { method: 'POST', body: JSON.stringify(cfg) ... });
};
// ========================================================

export const UserCenterView: React.FC = () => {
  // 1. 初始化配置
  const [config, setConfig] = useState<AppConfig>(() => {
    const loaded = loadConfig();
    return {
      ...loaded,
      user: loaded.user || { username: 'admin', password: '', twoFactorSecret: '' },
      cloud115: loaded.cloud115 || { cookies: '' },
      proxy: loaded.proxy || { enabled: false, type: 'http', host: '', port: '' }
    };
  });

  const [newPassword, setNewPassword] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  
  // 2FA 状态
  const [isSetup2FA, setIsSetup2FA] = useState(false);
  const [tempSecret, setTempSecret] = useState('');
  const [verifyCode, setVerifyCode] = useState('');

  // 通用更新函数
  const updateNested = (section: string, key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...(prev[section] || {}), [key]: value }
    }));
  };

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  const handleSave = async () => {
    setIsSaving(true);
    await new Promise(r => setTimeout(r, 600)); // 模拟延迟
    await saveConfig(config);
    setIsSaving(false);
    showToast('所有配置已保存并生效');
  };

  const handlePasswordSave = async () => {
    if (!newPassword) return;
    const newCfg = { ...config, user: { ...config.user, password: newPassword } };
    setConfig(newCfg);
    await saveConfig(newCfg);
    setNewPassword('');
    showToast('管理员密码已修改');
  };

  // 2FA 逻辑
  const start2FA = () => {
    setTempSecret('JBSWY3DPEHPK3PXP' + Math.floor(Math.random()*1000)); // 模拟生成
    setIsSetup2FA(true);
  };
  const confirm2FA = () => {
    if (verifyCode.length !== 6) return showToast('请输入6位验证码');
    updateNested('user', 'twoFactorSecret', tempSecret);
    setIsSetup2FA(false);
    saveConfig({ ...config, user: { ...config.user, twoFactorSecret: tempSecret }});
    showToast('双重验证已启用');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      
      {/* 顶部标题栏 + 保存按钮 */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h2 className="text-3xl font-bold text-slate-800 dark:text-white tracking-tight">用户中心</h2>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">管理管理员账号、安全验证及网络连接。</p>
        </div>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="group relative px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium shadow-lg shadow-indigo-500/30 transition-all active:scale-95 disabled:opacity-70 disabled:active:scale-100 overflow-hidden"
        >
          <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
          <div className="relative flex items-center gap-2">
            {isSaving ? <RefreshCw className="animate-spin" size={18} /> : <Save size={18} />}
            <span>保存全局设置</span>
          </div>
        </button>
      </div>

      {/* 提示 Toast */}
      {toast && (
        <div className="fixed top-6 right-6 z-50 bg-emerald-500 text-white px-4 py-3 rounded-lg shadow-xl flex items-center gap-3 animate-in slide-in-from-right">
          <RefreshCw size={20} className="animate-spin" />
          {toast}
        </div>
      )}

      {/* === Grid 布局核心：类似 bento box 的小组件布局 === */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* 1. 状态卡片组 (横跨 3 列) */}
        <div className="md:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatusCard 
            icon={<Activity size={24} />} 
            label="系统状态" 
            value="运行中" 
            subValue="Uptime: 3d 12h"
            color="bg-emerald-500" 
          />
          <StatusCard 
            icon={<Database size={24} />} 
            label="115 连接" 
            value={config.cloud115?.cookies ? "已连接" : "未连接"} 
            subValue={config.cloud115?.cookies ? "Cookie 有效" : "请配置 Cookie"}
            color={config.cloud115?.cookies ? "bg-blue-500" : "bg-slate-400"} 
          />
          <StatusCard 
            icon={<Shield size={24} />} 
            label="账户安全" 
            value={config.user?.twoFactorSecret ? "高" : "低"} 
            subValue={config.user?.twoFactorSecret ? "2FA 已启用" : "建议启用 2FA"}
            color={config.user?.twoFactorSecret ? "bg-purple-500" : "bg-orange-500"} 
          />
        </div>

        {/* 2. 管理员账号组件 (占据 2 列) */}
        <div className="md:col-span-2 bg-white dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 rounded-lg">
              <User size={20} />
            </div>
            <h3 className="text-lg font-bold text-slate-800 dark:text-white">管理员设置</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">当前用户</label>
              <div className="flex items-center gap-3 bg-slate-50 dark:bg-slate-900/50 p-3 rounded-xl border border-slate-100 dark:border-slate-700">
                <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold">
                  A
                </div>
                <div>
                  <div className="font-bold text-slate-700 dark:text-slate-200">{config.user?.username || 'admin'}</div>
                  <div className="text-xs text-slate-400">超级管理员权限</div>
                </div>
              </div>
            </div>

            <div className="pt-2">
               <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">修改密码</label>
               <div className="flex gap-2">
                 <div className="relative flex-1">
                   <KeyRound className="absolute left-3 top-3 text-slate-400" size={16} />
                   <input 
                     type="password" 
                     placeholder="输入新密码..." 
                     value={newPassword}
                     onChange={e => setNewPassword(e.target.value)}
                     className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 focus:ring-2 focus:ring-indigo-500 outline-none text-slate-700 dark:text-slate-200 transition-all"
                   />
                 </div>
                 <button 
                   onClick={handlePasswordSave}
                   disabled={!newPassword}
                   className="px-4 py-2 bg-slate-800 dark:bg-slate-700 text-white rounded-xl hover:bg-slate-700 dark:hover:bg-slate-600 disabled:opacity-50 transition-colors font-medium text-sm"
                 >
                   修改
                 </button>
               </div>
            </div>
          </div>
        </div>

        {/* 3. 网络代理组件 (占据 1 列，垂直) */}
        <div className="md:col-span-1 bg-white dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded-lg">
                <Globe size={20} />
              </div>
              <h3 className="text-lg font-bold text-slate-800 dark:text-white">网络代理</h3>
            </div>
            {/* 开关 */}
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" checked={config.proxy?.enabled} onChange={e => updateNested('proxy', 'enabled', e.target.checked)} />
              <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className={`space-y-4 flex-1 transition-opacity ${config.proxy?.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
             <div>
                <label className="text-xs text-slate-500 font-bold mb-1 block">协议类型</label>
                <div className="flex bg-slate-50 dark:bg-slate-900/50 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
                   {['http', 'socks5'].map(t => (
                     <button
                       key={t}
                       onClick={() => updateNested('proxy', 'type', t)}
                       className={`flex-1 py-1.5 text-xs font-bold rounded-md transition-all uppercase ${config.proxy?.type === t ? 'bg-white dark:bg-slate-700 shadow text-blue-600 dark:text-blue-400' : 'text-slate-400 hover:text-slate-600'}`}
                     >
                       {t}
                     </button>
                   ))}
                </div>
             </div>
             
             <div>
                <label className="text-xs text-slate-500 font-bold mb-1 block">服务器地址</label>
                <input 
                  type="text" 
                  value={config.proxy?.host}
                  onChange={e => updateNested('proxy', 'host', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 text-sm font-mono"
                  placeholder="127.0.0.1" 
                />
             </div>
             
             <div>
                <label className="text-xs text-slate-500 font-bold mb-1 block">端口</label>
                <input 
                  type="text" 
                  value={config.proxy?.port}
                  onChange={e => updateNested('proxy', 'port', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 text-sm font-mono"
                  placeholder="7890" 
                />
             </div>
          </div>
        </div>

        {/* 4. 2FA 安全组件 (占据 3 列) */}
        <div className="md:col-span-3 bg-gradient-to-br from-slate-50 to-white dark:from-slate-800/40 dark:to-slate-900/40 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1">
               <div className="flex items-center gap-3 mb-4">
                  <div className={`p-2 rounded-lg ${config.user?.twoFactorSecret ? 'bg-emerald-100 text-emerald-600' : 'bg-orange-100 text-orange-600'}`}>
                    <Smartphone size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-800 dark:text-white">两步验证 (2FA)</h3>
                    <p className="text-xs text-slate-500">通过 Google Authenticator 保护您的账户</p>
                  </div>
               </div>
               
               {config.user?.twoFactorSecret ? (
                 <div className="p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800 rounded-xl flex items-center gap-3 text-emerald-700 dark:text-emerald-400">
                    <Shield size={20} />
                    <span className="font-bold text-sm">您的账户已受保护。如需更换设备，请点击右侧重置。</span>
                 </div>
               ) : (
                 <div className="p-4 bg-orange-50 dark:bg-orange-900/20 border border-orange-100 dark:border-orange-800 rounded-xl flex items-center gap-3 text-orange-700 dark:text-orange-400">
                    <Lock size={20} />
                    <span className="font-bold text-sm">当前未启用保护。强烈建议立即设置。</span>
                 </div>
               )}
            </div>

            <div className="flex flex-col justify-center min-w-[300px]">
               {!isSetup2FA ? (
                  <button 
                    onClick={start2FA}
                    className="w-full py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 hover:border-indigo-500 dark:hover:border-indigo-500 text-slate-700 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 rounded-xl font-bold transition-all shadow-sm"
                  >
                    {config.user?.twoFactorSecret ? '重置 2FA 配置' : '立即启用 2FA'}
                  </button>
               ) : (
                  <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 animate-in fade-in">
                     <div className="text-xs font-mono bg-slate-100 dark:bg-slate-900 p-2 rounded text-center mb-3 select-all">
                       {tempSecret}
                     </div>
                     <div className="flex gap-2">
                       <input 
                         type="text" 
                         placeholder="6位验证码" 
                         value={verifyCode}
                         onChange={e => setVerifyCode(e.target.value)}
                         className="flex-1 px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-center font-bold tracking-widest outline-none focus:border-indigo-500"
                         maxLength={6}
                       />
                       <button onClick={confirm2FA} className="px-4 bg-indigo-600 text-white rounded-lg font-bold text-sm">确认</button>
                     </div>
                  </div>
               )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

// 子组件：状态卡片
const StatusCard = ({ icon, label, value, subValue, color }: any) => (
  <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-4 flex items-center gap-4 shadow-sm hover:shadow-md transition-shadow group">
    <div className={`p-3 rounded-xl text-white shadow-lg shadow-gray-200 dark:shadow-none ${color} group-hover:scale-110 transition-transform`}>
      {icon}
    </div>
    <div>
      <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">{label}</div>
      <div className="text-xl font-bold text-slate-800 dark:text-white leading-tight">{value}</div>
      <div className="text-xs text-slate-400 dark:text-slate-500 mt-1">{subValue}</div>
    </div>
  </div>
);
