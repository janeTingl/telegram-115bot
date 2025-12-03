import React, { useState, useEffect, useRef } from 'react';
import { 
  Save, RefreshCw, Eye, EyeOff, Cookie, QrCode, 
  Smartphone, Gauge, AlertTriangle, CheckCircle2, 
  Server, Send, ShieldAlert 
} from 'lucide-react';

// 假设这是你的类型定义，根据实际情况调整
interface AppConfig {
  cloud115: {
    cookies: string;
    uid: string;
  };
  emby: {
    host: string;
    api_key: string;
    qps: number;
  };
  telegram: {
    bot_token: string;
    chat_id: string;
  };
}

export const SettingsView: React.FC = () => {
  // 状态管理
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  // UI 交互状态
  const [showEmbyKey, setShowEmbyKey] = useState(false);
  const [showTgToken, setShowTgToken] = useState(false);
  const [toast, setToast] = useState<{msg: string, type: 'success' | 'error'} | null>(null);

  // 115 扫码登录状态
  const [qrState, setQrState] = useState<'idle' | 'loading' | 'waiting' | 'success' | 'expired'>('idle');
  const [qrData, setQrData] = useState<{ uid: string, time: number, sign: string, img: string } | null>(null);
  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);

  // --- 1. 初始化：从后端加载配置 ---
  useEffect(() => {
    fetchConfig();
    return () => stopPolling(); // 组件卸载时停止轮询
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await fetch('/api/config');
      if (!res.ok) throw new Error('加载配置失败');
      const data = await res.json();
      setConfig(data);
    } catch (err) {
      showToast('无法连接到后端服务器', 'error');
    } finally {
      setLoading(false);
    }
  };

  // --- 2. 保存配置 ---
  const handleSave = async () => {
    if (!config) return;
    setIsSaving(true);
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      if (res.ok) {
        showToast('配置已保存并生效', 'success');
      } else {
        showToast('保存失败', 'error');
      }
    } catch (err) {
      showToast('网络请求错误', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  // --- 3. 115 登录逻辑 (真实交互) ---
  const start115Login = async () => {
    setQrState('loading');
    try {
      // 请求后端获取二维码数据
      const res = await fetch('/api/115/qrcode');
      const data = await res.json();
      
      if (data.code === 0) { // 假设后端返回 code=0 成功
        setQrData(data.data); // data 包含 base64 图片和 uid
        setQrState('waiting');
        startPolling(data.data.uid, data.data.time, data.data.sign);
      } else {
        showToast(data.msg || '获取二维码失败', 'error');
        setQrState('idle');
      }
    } catch (e) {
      setQrState('idle');
      showToast('请求 115 接口失败', 'error');
    }
  };

  const startPolling = (uid: string, time: number, sign: string) => {
    if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    
    pollTimerRef.current = setInterval(async () => {
      try {
        const res = await fetch(`/api/115/status?uid=${uid}&time=${time}&sign=${sign}`);
        const data = await res.json();
        
        // 假设后端返回: status 0=等待, 1=扫码成功/登录中, 2=成功获取cookie
        if (data.status === 2) { 
          stopPolling();
          setQrState('success');
          // 更新本地配置显示
          updateConfigNested('cloud115', 'cookies', data.cookies);
          showToast('115 登录成功！请记得保存配置', 'success');
        } else if (data.status === -1) {
          stopPolling();
          setQrState('expired');
        }
      } catch (e) {
        // 忽略网络波动
      }
    }, 2000); // 每2秒轮询一次
  };

  const stopPolling = () => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
  };

  // --- 4. Emby 连接测试 ---
  const testEmbyConnection = async () => {
    if (!config?.emby.host || !config?.emby.api_key) {
      showToast('请先填写 Emby Host 和 Key', 'error');
      return;
    }
    const toastId = showToast('正在连接 Emby...', 'success'); // 简单提示
    try {
        // 这里可以直接发送当前的 config.emby 字段给后端测试，而不必先保存
        const res = await fetch('/api/emby/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config.emby)
        });
        const data = await res.json();
        if (data.success) {
            showToast(`连接成功: ${data.serverName} (v${data.version})`, 'success');
        } else {
            showToast(`连接失败: ${data.error}`, 'error');
        }
    } catch (e) {
        showToast('测试请求发送失败', 'error');
    }
  };

  // 辅助函数
  const updateConfigNested = (section: keyof AppConfig, key: string, value: any) => {
    setConfig(prev => prev ? ({
      ...prev,
      [section]: { ...prev[section], [key]: value }
    }) : null);
  };

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  if (loading) return <div className="p-10 text-center text-slate-400 animate-pulse">正在从服务器加载配置...</div>;
  if (!config) return <div className="p-10 text-center text-red-400">配置加载失败</div>;

  return (
    <div className="max-w-4xl mx-auto pb-24 space-y-6">
      
      {/* 顶部标题栏 */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">系统设置</h1>
          <p className="text-sm text-slate-400">配置 115 账号、Emby 连接及通知服务</p>
        </div>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`flex items-center space-x-2 px-6 py-2.5 rounded-lg font-medium transition-all ${
            isSaving 
              ? 'bg-blue-600/50 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-900/20'
          }`}
        >
          {isSaving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          <span>{isSaving ? '保存中...' : '保存更改'}</span>
        </button>
      </div>

      {/* 115 网盘设置卡片 */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <div className="flex items-center space-x-3 mb-6 border-b border-slate-700/50 pb-4">
          <div className="p-2 bg-orange-500/10 rounded-lg">
            <Cookie className="w-5 h-5 text-orange-500" />
          </div>
          <h2 className="text-lg font-semibold text-slate-200">115 网盘授权</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-4">
            <label className="block text-sm font-medium text-slate-400">Cookie (UID/CID/SEID)</label>
            <textarea
              value={config.cloud115.cookies}
              onChange={(e) => updateConfigNested('cloud115', 'cookies', e.target.value)}
              className="w-full h-32 bg-slate-900/50 border border-slate-700 rounded-lg p-3 text-xs font-mono text-slate-300 focus:ring-2 focus:ring-orange-500/50 outline-none resize-none"
              placeholder="UID=...; CID=...; SEID=..."
            />
            <p className="text-xs text-slate-500">
              * 推荐使用扫码登录自动获取，手动填写请确保格式正确。
            </p>
          </div>

          {/* 扫码区域 */}
          <div className="flex flex-col items-center justify-center p-6 bg-slate-900/30 rounded-xl border border-dashed border-slate-700">
            {qrState === 'idle' && (
              <div className="text-center space-y-3">
                <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto">
                  <QrCode className="w-8 h-8 text-slate-400" />
                </div>
                <button 
                  onClick={start115Login}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-white transition-colors"
                >
                  获取登录二维码
                </button>
              </div>
            )}

            {qrState === 'loading' && (
              <div className="flex flex-col items-center text-slate-400">
                <RefreshCw className="w-8 h-8 animate-spin mb-2" />
                <span className="text-sm">正在请求 115 接口...</span>
              </div>
            )}

            {qrState === 'waiting' && qrData && (
              <div className="text-center space-y-3">
                <div className="relative group">
                    {/* 使用 Base64 图片 */}
                    <img src={qrData.img} alt="Scan QR" className="w-40 h-40 rounded-lg shadow-lg mx-auto" />
                    <div className="text-xs text-slate-400 mt-2 flex items-center justify-center space-x-1">
                        <Smartphone className="w-3 h-3" />
                        <span>请使用 115 App 扫码</span>
                    </div>
                </div>
              </div>
            )}

            {qrState === 'success' && (
              <div className="text-center text-green-400 space-y-2">
                <CheckCircle2 className="w-12 h-12 mx-auto" />
                <div className="font-medium">登录成功</div>
                <div className="text-xs text-slate-500">Cookie 已自动填入左侧</div>
                <button onClick={() => setQrState('idle')} className="text-xs underline mt-2">重新登录</button>
              </div>
            )}
             
             {qrState === 'expired' && (
              <div className="text-center text-red-400 space-y-2">
                <ShieldAlert className="w-12 h-12 mx-auto" />
                <div className="font-medium">二维码已过期</div>
                <button 
                  onClick={start115Login}
                  className="px-3 py-1 bg-red-500/10 hover:bg-red-500/20 rounded text-xs transition-colors"
                >
                  刷新二维码
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Emby 设置卡片 */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-6 border-b border-slate-700/50 pb-4">
            <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-500/10 rounded-lg">
                    <Server className="w-5 h-5 text-green-500" />
                </div>
                <h2 className="text-lg font-semibold text-slate-200">Emby 服务器</h2>
            </div>
            <button 
                onClick={testEmbyConnection}
                className="text-xs bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded text-slate-300 flex items-center space-x-1"
            >
                <Gauge className="w-3 h-3" />
                <span>测试连接</span>
            </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400">Host 地址</label>
            <input
              type="text"
              value={config.emby.host}
              onChange={(e) => updateConfigNested('emby', 'host', e.target.value)}
              placeholder="http://192.168.1.x:8096"
              className="w-full bg-slate-900/50 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 focus:ring-2 focus:ring-green-500/50 outline-none"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400">API Key</label>
            <div className="relative">
              <input
                type={showEmbyKey ? "text" : "password"}
                value={config.emby.api_key}
                onChange={(e) => updateConfigNested('emby', 'api_key', e.target.value)}
                className="w-full bg-slate-900/50 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 focus:ring-2 focus:ring-green-500/50 outline-none pr-10"
              />
              <button
                onClick={() => setShowEmbyKey(!showEmbyKey)}
                className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
              >
                {showEmbyKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="md:col-span-2 space-y-2">
            <label className="text-sm font-medium text-slate-400 flex items-center space-x-2">
                <span>请求频率限制 (QPS)</span>
                <span className="text-xs bg-slate-700 px-2 py-0.5 rounded text-slate-400">建议值: 1-3</span>
            </label>
            <div className="flex items-center space-x-4">
                <input 
                    type="range" 
                    min="1" max="10" step="1"
                    value={config.emby.qps}
                    onChange={(e) => updateConfigNested('emby', 'qps', parseInt(e.target.value))}
                    className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-green-500"
                />
                <span className="w-12 text-center font-mono text-slate-200">{config.emby.qps} req/s</span>
            </div>
          </div>
        </div>
      </div>

      {/* Telegram 通知设置 */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <div className="flex items-center space-x-3 mb-6 border-b border-slate-700/50 pb-4">
          <div className="p-2 bg-blue-500/10 rounded-lg">
            <Send className="w-5 h-5 text-blue-400" />
          </div>
          <h2 className="text-lg font-semibold text-slate-200">Telegram 通知</h2>
        </div>

        <div className="grid grid-cols-1 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400">Bot Token</label>
            <div className="relative">
                <input
                    type={showTgToken ? "text" : "password"}
                    value={config.telegram.bot_token}
                    onChange={(e) => updateConfigNested('telegram', 'bot_token', e.target.value)}
                    placeholder="123456789:ABCdefGHIjklMno..."
                    className="w-full bg-slate-900/50 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500/50 outline-none pr-10"
                />
                <button
                    onClick={() => setShowTgToken(!showTgToken)}
                    className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
                >
                    {showTgToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400">Chat ID</label>
            <input
              type="text"
              value={config.telegram.chat_id}
              onChange={(e) => updateConfigNested('telegram', 'chat_id', e.target.value)}
              placeholder="-100xxxxxxxxx"
              className="w-full bg-slate-900/50 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 focus:ring-2 focus:ring-blue-500/50 outline-none"
            />
            <p className="text-xs text-slate-500">
                * 建议先在 Bot 中发送 /start，然后填写获取到的 ID。
            </p>
          </div>
        </div>
      </div>

      {/* 全局 Toast 提示 */}
      {toast && (
        <div className={`fixed bottom-8 right-8 px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2 animate-fade-in-up ${
          toast.type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
        }`}>
          {toast.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5" />}
          <span>{toast.msg}</span>
        </div>
      )}
    </div>
  );
};