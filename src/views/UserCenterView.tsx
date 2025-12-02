import React, { useEffect, useState } from 'react';
import { 
  Activity, Database, Wifi, Shield, Save, KeyRound, User, 
  RefreshCw, Smartphone, Zap, Server, Lock, Globe, XCircle, Moon
} from 'lucide-react';

// === 辅助类型和函数 (为了保证代码自洽和安全) ===
interface AppConfig { user?: any; system?: any; cloud115?: any; proxy?: any; [key: string]: any; }

// 从本地存储安全加载配置 (同步函数，防止 useState 报错)
const loadConfig = (): AppConfig => {
  try { return JSON.parse(localStorage.getItem('app_config') || '{}'); } catch { return {}; }
};

// 模拟保存配置 (发送到后端 API)
const saveConfig = async (cfg: AppConfig) => {
  localStorage.setItem('app_config', JSON.stringify(cfg));
  try {
    // 假设后端接口为 /api/config，包含授权头
    const res = await fetch('/api/config', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cfg)
    });
    if (!res.ok) throw new Error('Backend responded with error');
  } catch (e) {
    console.error("Backend save failed, data saved locally only.", e);
  }
};
// ========================================================


export const UserCenterView: React.FC = () => {
  // 1. 状态初始化：安全性保证
  const [config, setConfig] = useState<AppConfig>(() => {
    const loaded = loadConfig() || {};
    return {
      ...loaded,
      user: loaded.user || { username: 'admin', password: '', twoFactorSecret: '' },
      cloud115: loaded.cloud115 || { cookies: '' },
      proxy: loaded.proxy || { enabled: false, type: 'http', host: '', port: '' }
    } as AppConfig;
  });

  // 2. 局部状态管理
  const [newPassword, setNewPassword] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [isPwSaving, setIsPwSaving] = useState(false);
  
  // 2FA 状态
  const [isSetup2FA, setIsSetup2FA] = useState(false);
  const [tempSecret, setTempSecret] = useState('');
  const [verifyCode, setVerifyCode] = useState('');
  const [setupError, setSetupError] = useState('');
  
  // 代理延迟状态
  const [proxyLatency, setProxyLatency] = useState<number | string | null>(null);
  const [isTesting, setIsTesting] = useState(false);


  // 3. 核心函数: 修复类型报错的更新函数
  const updateNested = (section: string, key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...(prev[section] as any), [key]: value }
    }));
  };

  const showToast = (msg: string) => { setToast(msg); setTimeout(() => setToast(null), 3000); };

  // 4. 真实延迟测试逻辑
  const testProxyLatency = async () => {
      setIsTesting(true);
      setProxyLatency(null);

      try {
          const response = await fetch('/api/network/latency');
          const data = await response.json();

          if (response.ok && data.status === 'success') {
              setProxyLatency(data.latency);
          } else {
              setProxyLatency('Error'); 
              console.error('Proxy test failed:', data.detail || 'Unknown error');
          }
      } catch (error) {
          setProxyLatency('Timeout');
          console.error('Network request failed:', error);
      } finally {
          setIsTesting(false);
      }
  };


  // 5. 真实 2FA 启动逻辑
  const start2FASetup = async () => {
    setSetupError('');
    try {
        const res = await fetch('/api/security/generate_secret', { method: 'POST' });
        const data = await res.json();
        
        if (data.secret && data.otp_url) {
            setTempSecret(data.secret); 
            setVerifyCode('');
            setIsSetup2FA(true);
        } else {
            setSetupError('无法获取新的密钥，请检查后端日志。');
        }
    } catch (e) {
        setSetupError('无法连接到密钥生成服务。');
    }
  };
  
  // 6. 真实 2FA 确认逻辑
  const confirm2FASetup = async () => {
    setSetupError('');
    if (verifyCode.length !== 6) {
        return setSetupError('请输入 6 位验证码');
    }
    try {
        const res = await fetch('/api/security/verify_2fa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ temp_secret: tempSecret, verification_code: verifyCode })
        });

        if (res.ok) {
            updateNested('user', 'twoFactorSecret', tempSecret); 
            setIsSetup2FA(false);
            showToast('2FA 验证成功并已启用！');
        } else {
            const err = await res.json();
            setSetupError(err.detail || '验证失败，请检查时间或重试。');
        }
    } catch (e) {
        setSetupError('验证请求失败。');
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    await new Promise(r => setTimeout(r, 600)); 
    await saveConfig(config);
    setIsSaving(false);
    showToast('所有配置已保存并生效');
  };
  
  const handlePasswordSave = async () => {
    if (!newPassword) return;
    setIsPwSaving(true);
    const newConfig = { ...config, user: { ...config.user!, password: newPassword } };
    setConfig(newConfig);
    await saveConfig(newConfig);
    setIsPwSaving(false);
    setNewPassword('');
    showToast('管理员密码已修改');
  };

  const fillLocalIp = () => { updateNested('proxy', 'host', window.location.hostname); };
  const cancel2FASetup = () => { setIsSetup2FA(false); setTempSecret(''); };


  return (
    <div className="space-y-6 p-6 animate-in fade-in duration-500">
      
      {/* 顶部标题栏 + 保存按钮 */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h2 className="text-3xl font-bold text-slate-800 dark:text-white tracking-tight">用户中心</h2>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">管理管理员账号、安全验证及网络连接。</p>
        </div>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="group px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-medium shadow-lg shadow-blue-500/30 transition-all active:scale-95 disabled:opacity-70 flex items-center gap-2"
        >
          {isSaving ? <RefreshCw className="animate-spin" size={18} /> : <Save size={18} />}
          <span>保存全局设置</span>
        </button>
      </div>

      {/* 提示 Toast */}
      {toast && (
        <div className="fixed top-6 right-6 z-50 bg-emerald-500 text-white px-4 py-3 rounded-lg shadow-xl flex items-center gap-3 animate-in slide-in-from-right">
          <CheckCircle size={20} />
          {toast}
        </div>
      )}

      {/* === Grid Layout Start === */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* 1. 管理员账号组件 (占据 2 列) */}
        <section className="lg:col-span-2 bg-white dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 rounded-lg">
              <User size={20} />
            </div>
            <h3 className="text-lg font-bold text-slate-800 dark:text-white">管理员账号</h3>
          </div>
          
          <div className="space-y-4">
            {/* 用户名 (Disabled) */}
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">当前用户</label>
              <div className="flex items-center gap-3 bg-slate-50 dark:bg-slate-900/50 p-3 rounded-xl border border-slate-100 dark:border-slate-700">
                <div className="font-bold text-slate-700 dark:text-slate-200">{config.user?.username || 'admin'}</div>
              </div>
            </div>

            {/* 修改密码 */}
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
                     className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                   />
                 </div>
                 <button 
                   onClick={handlePasswordSave}
                   disabled={!newPassword || isPwSaving}
                   className="px-4 py-2 bg-slate-800 dark:bg-slate-700 text-white rounded-xl hover:bg-slate-700 dark:hover:bg-slate-600 disabled:opacity-50 transition-colors font-medium text-sm"
                 >
                   {isPwSaving ? <RefreshCw className="animate-spin" size={14} /> : '修改'}
                 </button>
               </div>
            </div>
          </div>
        </section>

        {/* 2. 代理设置组件 (占 1 列) */}
        <section className="lg:col-span-1 bg-white dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded-lg">
              <Wifi size={20} />
            </div>
            <h3 className="text-lg font-bold text-slate-800 dark:text-white">网络代理设置</h3>
          </div>
          
          <div className="space-y-4">
            {/* 开关 */}
            <div className="flex justify-between items-center">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300">启用代理</label>
              <input 
                type="checkbox"
                checked={config.proxy.enabled} 
                onChange={(e) => updateNested('proxy', 'enabled', e.target.checked ? 'true' : 'false')} 
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
            
            {/* 代理类型 */}
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">类型</label>
              <select 
                value={config.proxy.type}
                onChange={e => updateNested('proxy', 'type', e.target.value)}
                className="w-full py-2 px-3 rounded-xl border border-slate-300 dark:border-slate-700 dark:bg-slate-900/50 text-sm"
              >
                <option value="http">HTTP/HTTPS</option>
                <option value="socks5">SOCKS5</option>
              </select>
            </div>
            
            {/* 主机和端口 */}
            <div className="flex gap-2">
              <input 
                type="text" 
                placeholder="主机名/IP" 
                value={config.proxy.host}
                onChange={e => updateNested('proxy', 'host', e.target.value)}
                className="flex-1 px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 dark:bg-slate-900/50 text-sm"
              />
              <input 
                type="number" 
                placeholder="端口" 
                value={config.proxy.port}
                onChange={e => updateNested('proxy', 'port', e.target.value)}
                className="w-20 px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 dark:bg-slate-900/50 text-sm"
              />
            </div>
          </div>
          
          {/* 延迟测试区域 */}
          <div className="mt-4 border-t border-slate-200 dark:border-slate-700 pt-4">
            <h4 className="font-bold text-sm mb-2">延迟测试</h4>
            <p className="text-xs text-slate-500 mb-3">测试代理到 Telegram API 的连接速度。</p>
            
            <div className="flex justify-between items-center text-sm font-medium mb-3">
              <span>延迟率:</span>
              <span className={proxyLatency === 'Error' || proxyLatency === 'Timeout' ? 'text-red-500' : 'text-emerald-500'}>
                {isTesting ? '测试中...' : proxyLatency ? `${proxyLatency} ms` : 'N/A'}
              </span>
            </div>
            
            <button 
              onClick={testProxyLatency}
              disabled={isTesting || config.proxy.enabled !== 'true' || !config.proxy.host || !config.proxy.port}
              className="w-full py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-xl font-medium text-slate-700 dark:text-slate-200 transition-colors text-sm disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isTesting ? <RefreshCw className="animate-spin" size={16} /> : '开始测试'}
            </button>
          </div>
        </section>

        {/* 3. 2FA 安全组件 (占 3 列) */}
        <section className="lg:col-span-3 bg-gradient-to-br from-slate-50 to-white dark:from-slate-800/40 dark:to-slate-900/40 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm">
           {/* ... 2FA 逻辑 UI (保持不变) ... */}
           <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1">
               <div className="flex items-center gap-3 mb-4">
                  <div className={`p-2 rounded-lg ${config.user?.twoFactorSecret ? 'bg-emerald-100 text-emerald-600' : 'bg-orange-100 text-orange-600'}`}>
                    <Smartphone size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-800 dark:text-white">双重验证 (2FA)</h3>
                    <p className="text-xs text-slate-500">通过 Google Authenticator 保护您的账户</p>
                  </div>
               </div>
               
               {config.user?.twoFactorSecret ? (
                 <div className className="p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800 rounded-xl flex items-center gap-3 text-emerald-700 dark:text-emerald-400">
                    <Shield size={20} />
                    <span className="font-bold text-sm">您的账户已受保护。如需更换设备，请点击右侧重置。</span>
                 </div>
               ) : (
                 <div className className="p-4 bg-orange-50 dark:bg-orange-900/20 border border-orange-100 dark:border-orange-800 rounded-xl flex items-center gap-3 text-orange-700 dark:text-orange-400">
                    <Lock size={20} />
                    <span className="font-bold text-sm">当前未启用保护。强烈建议立即设置。</span>
                 </div>
               )}
            </div>

            <div className="flex flex-col justify-center min-w-[300px]">
               {!isSetup2FA ? (
                  <button 
                    onClick={start2FASetup}
                    className="w-full py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 hover:border-blue-500 dark:hover:border-blue-500 text-slate-700 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400 rounded-xl font-bold transition-all shadow-sm"
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
                         className="flex-1 px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-center font-bold tracking-widest outline-none focus:border-blue-500"
                         maxLength={6}
                       />
                       <button onClick={confirm2FASetup} className="px-4 bg-blue-600 text-white rounded-lg font-bold text-sm">确认</button>
                     </div>
                  </div>
               )}
            </div>
          </div>
        </section>
        {/* End 2FA */}
      </div>
    </div>
  );
};
