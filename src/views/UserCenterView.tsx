// views/UserCenterView.tsx
import React, { useState } from 'react';
import { AppConfig } from '../types';
import { loadConfig, saveConfig } from '../services/mockConfig';
import { saveAdminPassword, saveProxyConfig } from '../services/config';
import { Save, RefreshCw, KeyRound, User, Smartphone, Wifi, Shield, HardDrive, Cloud, Globe, Film, Bot, CheckCircle2, AlertCircle, Zap } from 'lucide-react';
import { SensitiveInput } from '../components/SensitiveInput';

export const UserCenterView: React.FC = () => {
  const [config, setConfig] = useState<AppConfig>(loadConfig());
  const [newPassword, setNewPassword] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isPwSaving, setIsPwSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  
  const [isSetup2FA, setIsSetup2FA] = useState(false);
  const [tempSecret, setTempSecret] = useState('');
  const [verifyCode, setVerifyCode] = useState('');
  const [setupError, setSetupError] = useState('');

  const updateNested = (section: keyof AppConfig, key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], [key]: value }
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setToast('正在保存代理配置...');
    
    try {
        await saveProxyConfig({
            ...config.proxy,
            port: String(config.proxy.port)
        }); 
        
        saveConfig(config); 
        setToast('代理配置已更新');
    } catch (e) {
        setToast(`保存失败: ${e.message}`);
    } finally {
        setIsSaving(false);
        setTimeout(() => setToast(null), 3000);
    }
  };

  const handlePasswordSave = async () => {
    if (!newPassword) return;
    setIsPwSaving(true);
    setToast('正在修改管理员密码...');
    
    try {
        await saveAdminPassword(newPassword); 
        setNewPassword('');
        setToast('管理员密码已修改');
    } catch (e) {
        setToast(`修改失败: ${e.message}`);
    } finally {
        setIsPwSaving(false);
        setTimeout(() => setToast(null), 3000);
    }
  };

  const fillLocalIp = () => {
      updateNested('proxy', 'host', window.location.hostname);
  };

  const start2FASetup = () => {
      const randomSecret = 'JBSWY3DPEHPK3PXP' + Math.floor(Math.random() * 10000).toString();
      setTempSecret(randomSecret);
      setVerifyCode('');
      setSetupError('');
      setIsSetup2FA(true);
  };

  const cancel2FASetup = () => {
      setIsSetup2FA(false);
      setTempSecret('');
  };

  const confirm2FASetup = () => {
      if (verifyCode === '123456') {
          setConfig(prev => ({ ...prev, twoFactorSecret: tempSecret }));
          setIsSetup2FA(false);
          setToast('2FA 配置已更新');
          setTimeout(() => setToast(null), 3000);
          saveConfig({ ...config, twoFactorSecret: tempSecret });
      } else {
          setSetupError('验证码错误 (测试用: 123456)');
      }
  };

  const services = [
    {
        name: '115 网盘',
        isConnected: !!config.cloud115.cookies,
        icon: HardDrive,
        colorClass: 'text-orange-600 dark:text-orange-400',
        bgClass: 'bg-orange-50 dark:bg-orange-900/20'
    },
    {
        name: '123 云盘',
        isConnected: config.cloud123.enabled && !!config.cloud123.clientId,
        icon: Cloud,
        colorClass: 'text-blue-600 dark:text-blue-400',
        bgClass: 'bg-blue-50 dark:bg-blue-900/20'
    },
    {
        name: 'OpenList',
        isConnected: config.openList.enabled && !!config.openList.url,
        icon: Globe,
        colorClass: 'text-cyan-600 dark:text-cyan-400',
        bgClass: 'bg-cyan-50 dark:bg-cyan-900/20'
    },
    {
        name: 'TMDB',
        isConnected: !!config.tmdb.apiKey,
        icon: Film,
        colorClass: 'text-pink-600 dark:text-pink-400',
        bgClass: 'bg-pink-50 dark:bg-pink-900/20'
    },
    {
        name: 'TG 机器人',
        isConnected: !!config.telegram.botToken,
        icon: Bot,
        colorClass: 'text-sky-600 dark:text-sky-400',
        bgClass: 'bg-sky-50 dark:bg-sky-900/20'
    }
  ];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
      {toast && (
        <div className="fixed top-6 right-6 bg-slate-800/90 backdrop-blur-md text-white px-6 py-3 rounded-xl shadow-2xl z-50 flex items-center gap-3 font-medium border border-slate-700/50">
          <RefreshCw size={18} className="animate-spin text-brand-400" />
          {toast}
        </div>
      )}

      <div className="flex flex-col md:flex-row justify-between items-center pb-2 gap-4">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white tracking-tight drop-shadow-sm">用户中心</h2>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {services.map((service) => (
            <div key={service.name} className="bg-white/70 dark:bg-slate-900/50 backdrop-blur-md rounded-xl border border-white/50 dark:border-slate-700/50 p-4 shadow-sm flex flex-col items-center justify-center gap-3 relative overflow-hidden group hover:bg-white/90 dark:hover:bg-slate-800/60 transition-all duration-300">
                <div className={`p-3 rounded-xl ${service.bgClass} ${service.colorClass} mb-1 shadow-inner`}>
                    <service.icon size={24} strokeWidth={1.5} />
                </div>
                <div className="text-center">
                    <div className="text-sm font-bold text-slate-700 dark:text-slate-200">{service.name}</div>
                    <div className={`text-[10px] font-medium mt-1 flex items-center justify-center gap-1.5 ${service.isConnected ? 'text-green-600 dark:text-green-400' : 'text-slate-400'}`}>
                        {service.isConnected ? (
                            <>
                                <CheckCircle2 size={12} /> 已连接
                            </>
                        ) : (
                            <>
                                <AlertCircle size={12} /> 未配置
                            </>
                        )}
                    </div>
                </div>
                {service.isConnected && (
                    <div className="absolute top-3 right-3 w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                )}
            </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section className="bg-white/70 dark:bg-slate-900/50 backdrop-blur-md rounded-xl border border-white/50 dark:border-slate-700/50 shadow-sm flex flex-col">
           <div className="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50 flex items-center gap-3">
              <User size={18} className="text-slate-400" />
              <h3 className="font-bold text-slate-700 dark:text-slate-200">管理员账号</h3>
           </div>
           <div className="p-6 space-y-5 flex-1">
              <div>
                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1.5">用户名</label>
                <input
                  type="text"
                  value="admin"
                  disabled
                  className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700/50 bg-slate-50/50 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400 cursor-not-allowed text-sm backdrop-blur-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1.5">
                  修改密码
                </label>
                <div className="flex gap-3">
                   <div className="relative flex-1">
                      <KeyRound className="absolute left-3.5 top-2.5 text-slate-400" size={16} />
                      <SensitiveInput
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="输入新密码"
                        className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-slate-500 outline-none transition-all placeholder:text-slate-400 text-sm backdrop-blur-sm"
                      />
                   </div>
                   <button 
                      onClick={handlePasswordSave}
                      disabled={!newPassword || isPwSaving}
                      className="px-4 py-2 bg-brand-600/90 hover:bg-brand-600 backdrop-blur-md border border-white/10 text-white rounded-lg font-medium transition-all disabled:opacity-50 flex items-center gap-2 whitespace-nowrap text-sm shadow-lg shadow-brand-500/20 active:scale-95"
                   >
                     {isPwSaving ? <RefreshCw className="animate-spin" size={14} /> : <Save size={14} />}
                     保存设置
                   </button>
                </div>
              </div>
           </div>
        </section>

        <section className="bg-white/70 dark:bg-slate-900/50 backdrop-blur-md rounded-xl border border-white/50 dark:border-slate-700/50 shadow-sm flex flex-col">
           <div className="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50 flex items-center gap-3">
              <Smartphone size={18} className="text-slate-400" />
              <h3 className="font-bold text-slate-700 dark:text-slate-200">双重验证 (2FA)</h3>
           </div>
           
           {!isSetup2FA ? (
               <div className="p-6 flex-1 flex flex-col justify-between">
                   <div className="flex items-center gap-4 mb-6">
                        <div className={`p-3 rounded-full shadow-inner ${config.twoFactorSecret ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400' : 'bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500'}`}>
                            <Shield size={24} />
                        </div>
                        <div>
                            <h4 className="font-bold text-slate-800 dark:text-white text-base">
                                {config.twoFactorSecret ? '已启用保护' : '未启用保护'}
                            </h4>
                            <p className="text-xs text-slate-500 mt-0.5">
                                {config.twoFactorSecret ? '您的账户非常安全' : '建议启用以保护敏感信息'}
                            </p>
                        </div>
                   </div>

                  <div className="mb-5">
                      <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1.5">当前密钥 (Secret Key)</label>
                      <SensitiveInput
                          value={config.twoFactorSecret || ''}
                          onChange={(e) => {}}
                          className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-slate-500 outline-none font-mono text-sm backdrop-blur-sm"
                       />
                  </div>

                  <button 
                    onClick={start2FASetup}
                    className="w-full py-2.5 bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg text-sm font-bold hover:border-brand-500 hover:text-brand-600 transition-colors"
                  >
                      {config.twoFactorSecret ? '重置 / 配置验证' : '立即设置验证'}
                  </button>
               </div>
           ) : (
               <div className="p-6 flex-1">
                  <h4 className="font-bold text-slate-800 dark:text-white mb-4 text-sm">设置步骤</h4>
                  
                  <div className="bg-white/50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700/50 flex flex-col items-center mb-4">
                      <img 
                        src={`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=otpauth://totp/115BotAdmin?secret=${tempSecret}&issuer=115Bot`}
                        alt="2FA QR"
                        className="w-28 h-28 mb-4 rounded-lg mix-blend-multiply dark:mix-blend-normal opacity-90"
                      />
                      <div className="text-center w-full">
                          <code className="bg-slate-100/80 dark:bg-slate-800/80 px-3 py-1.5 rounded-lg text-xs font-mono text-slate-600 dark:text-slate-300 block break-all tracking-wider">
                              {tempSecret}
                          </code>
                      </div>
                  </div>

                  <div className="space-y-4">
                      <input 
                          type="text"
                          maxLength={6}
                          value={verifyCode}
                          onChange={(e) => setVerifyCode(e.target.value)}
                          placeholder="输入 6 位验证码"
                          className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-center font-mono text-lg tracking-[0.5em] focus:ring-2 focus:ring-brand-500 outline-none backdrop-blur-sm"
                      />
                      {setupError && <p className="text-xs text-red-500 text-center font-bold">{setupError}</p>}

                      <div className="flex gap-3">
                          <button 
                             onClick={cancel2FASetup}
                             className="flex-1 py-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/50 rounded-lg text-xs font-medium transition-colors"
                          >
                             取消
                          </button>
                          <button 
                             onClick={confirm2FASetup}
                             className="flex-1 py-2 bg-brand-600/90 hover:bg-brand-600 backdrop-blur-sm border border-white/10 text-white rounded-lg text-xs font-bold shadow-sm transition-all active:scale-95"
                          >
                             确认启用
                          </button>
                      </div>
                  </div>
               </div>
           )}
        </section>

        <section className="bg-white/70 dark:bg-slate-900/50 backdrop-blur-md rounded-xl border border-white/50 dark:border-slate-700/50 shadow-sm lg:col-span-2">
          <div className="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50 flex items-center justify-between">
            <div className="flex items-center gap-3">
               <Wifi size={18} className="text-slate-400" />
               <h3 className="font-bold text-slate-700 dark:text-slate-200">网络代理</h3>
            </div>
            
            <div className="flex items-center gap-4">
                {config.proxy.enabled && (
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100/50 dark:bg-slate-700/30 border border-slate-200/50 dark:border-slate-600/50">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                        <span className="text-[10px] font-mono font-medium text-slate-500 dark:text-slate-400">128ms</span>
                    </div>
                )}
                <div className="relative inline-block w-9 h-5 transition duration-200 ease-in-out rounded-full cursor-pointer">
                    <input 
                        id="proxyEnabled" 
                        type="checkbox" 
                        className="peer sr-only"
                        checked={config.proxy.enabled}
                        onChange={(e) => updateNested('proxy', 'enabled', e.target.checked)}
                    />
                    <label htmlFor="proxyEnabled" className="block h-5 overflow-hidden bg-slate-200 dark:bg-slate-700 rounded-full cursor-pointer peer-checked:bg-slate-900 dark:peer-checked:bg-white after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white dark:after:bg-slate-900 after:w-4 after:h-4 after:rounded-full after:shadow-sm after:transition-all peer-checked:after:translate-x-full"></label>
                </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className={`space-y-6 transition-all duration-300 ${config.proxy.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none grayscale'}`}>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                 <div className="md:col-span-1">
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">类型 (Type)</label>
                    <select 
                      value={config.proxy.type}
                      onChange={(e) => updateNested('proxy', 'type', e.target.value)}
                      className="w-full px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-slate-500 outline-none text-sm backdrop-blur-sm"
                    >
                      <option value="http">HTTP</option>
                      <option value="socks5">SOCKS5</option>
                    </select>
                 </div>
                 <div className="md:col-span-2">
                    <div className="flex justify-between items-center mb-2">
                      <label className="block text-xs font-bold text-slate-500 uppercase">代理地址 (Host:Port)</label>
                      <button onClick={fillLocalIp} className="text-xs text-brand-600 hover:text-brand-500 flex items-center gap-1 font-medium"><Zap size={12} /> 自动填入</button>
                    </div>
                    <div className="flex gap-3">
                       <input
                        type="text"
                        value={config.proxy.host}
                        onChange={(e) => updateNested('proxy', 'host', e.target.value)}
                        placeholder="192.168.1.5"
                        className="flex-1 px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-slate-500 outline-none font-mono text-sm backdrop-blur-sm"
                      />
                      <input
                        type="text"
                        value={config.proxy.port}
                        onChange={(e) => updateNested('proxy', 'port', e.target.value)}
                        placeholder="7890"
                        className="w-24 px-4 py-2.5 rounded-lg border border-slate-300/50 dark:border-slate-600/50 bg-white/50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-100 focus:ring-2 focus:ring-slate-500 outline-none font-mono text-sm backdrop-blur-sm"
                      />
                    </div>
                 </div>
              </div>
            </div>
            
            <div className="flex justify-end mt-6">
                <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="bg-brand-600/90 hover:bg-brand-600 backdrop-blur-md border border-white/10 text-white disabled:opacity-70 px-5 py-2 rounded-lg font-medium text-sm flex items-center gap-2 shadow-lg transition-all active:scale-95 shadow-brand-500/20"
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