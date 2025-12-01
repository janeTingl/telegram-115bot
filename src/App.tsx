import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { UserCenterView } from './views/UserCenterView';
import { BotSettingsView } from './views/BotSettingsView';
import { CloudOrganizeView } from './views/CloudOrganizeView';
import { EmbyView } from './views/EmbyView';
import { StrmView } from './views/StrmView';
import { LogsView } from './views/LogsView';
import { LoginView } from './views/LoginView';
import { checkAuth, logout } from './services/auth';
import { loadConfig } from './services/mockConfig';
import { Menu, X } from 'lucide-react';

// 备用背景图
const FALLBACK_BACKDROPS = [
  'https://image.tmdb.org/t/p/original/8rpDcsfLJypbO6vREc0547FVq5q.jpg',
  'https://image.tmdb.org/t/p/original/tmU7GeKVybMWFButWEGl2Mdbj47.jpg',
  'https://image.tmdb.org/t/p/original/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg',
];

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  
  // 视图状态
  const [currentView, setCurrentView] = useState('user');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // 背景图状态
  const [backdrops, setBackdrops] = useState<string[]>([]);
  const [currentBackdropIndex, setCurrentBackdropIndex] = useState(0);

  // 主题状态
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme');
      return saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
    return false;
  });

  useEffect(() => {
    setIsAuthenticated(checkAuth());
    setIsChecking(false);
  }, []);

  useEffect(() => {
    const root = window.document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  // TMDB 背景图
  useEffect(() => {
    const fetchBackdrops = async () => {
        const config = loadConfig() || {}; 
        const apiKey = config.tmdb?.apiKey;
        
        let loaded = false;
        if (apiKey && apiKey.length > 10) {
            try {
                const res = await fetch(`https://api.themoviedb.org/3/trending/all/week?api_key=${apiKey}&language=zh-CN`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.results?.length > 0) {
                         const paths = data.results
                            .filter((m: any) => m.backdrop_path)
                            .slice(0, 5)
                            .map((m: any) => `https://image.tmdb.org/t/p/original${m.backdrop_path}`);
                         if (paths.length > 0) {
                             setBackdrops(paths);
                             loaded = true;
                         }
                    }
                }
            } catch (e) {
                console.warn('TMDB Error', e);
            }
        }
        if (!loaded) setBackdrops(FALLBACK_BACKDROPS);
    };
    fetchBackdrops();
  }, []);

  // 轮播
  useEffect(() => {
    if (backdrops.length <= 1) return;
    const interval = setInterval(() => {
        setCurrentBackdropIndex(prev => (prev + 1) % backdrops.length);
    }, 10000); 
    return () => clearInterval(interval);
  }, [backdrops]);

  const toggleTheme = () => setIsDark(!isDark);
  const handleLoginSuccess = () => setIsAuthenticated(true);
  
  const handleLogout = () => {
    logout();
    setIsAuthenticated(false);
    setMobileMenuOpen(false);
    setCurrentView('user');
  };

  const handleMobileNavClick = (view: string) => {
    setCurrentView(view);
    setMobileMenuOpen(false);
  };

  const renderContent = () => {
    switch (currentView) {
      case 'user': return <UserCenterView />;
      case 'bot': return <BotSettingsView />;
      case 'cloud': return <CloudOrganizeView />;
      case 'emby': return <EmbyView />;
      case 'strm': return <StrmView />;
      case 'logs': return <LogsView />;
      default: return <UserCenterView />;
    }
  };

  if (isChecking) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-slate-500">Loading...</div>;

  return (
    <div className="h-screen w-full overflow-hidden font-sans relative flex flex-col text-slate-900 dark:text-slate-100">
      
      {/* === 全局背景层 === */}
      <div className="fixed inset-0 z-0 bg-slate-900 pointer-events-none">
        {backdrops.map((img, idx) => (
          <div
            key={idx}
            className={`absolute inset-0 bg-cover bg-center transition-opacity duration-[3000ms] ease-in-out ${idx === currentBackdropIndex ? 'opacity-100' : 'opacity-0'}`}
            style={{ backgroundImage: `url(${img})` }}
          />
        ))}
        <div className={`absolute inset-0 transition-all duration-1000 ${isAuthenticated ? 'bg-slate-50/80 dark:bg-slate-900/80 backdrop-blur-md' : 'bg-slate-900/40 backdrop-blur-sm'}`}></div>
      </div>

      <div className="relative z-10 flex h-full w-full">
        {!isAuthenticated ? (
          <div className="w-full h-full overflow-y-auto"><LoginView onLoginSuccess={handleLoginSuccess} /></div>
        ) : (
          <>
            {/* === 桌面端侧边栏 (固定) === */}
            <div className="hidden md:flex w-64 flex-col fixed inset-y-0 z-50">
              <Sidebar 
                currentView={currentView} 
                onChangeView={setCurrentView} 
                isDark={isDark}
                toggleTheme={toggleTheme}
                onLogout={handleLogout}
              />
            </div>

            {/* === 移动端菜单 === */}
            {mobileMenuOpen && (
              <div className="fixed inset-0 z-50 md:hidden flex">
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)}></div>
                <div className="relative flex-1 bg-slate-900/95 border-r border-slate-800 w-[80%] max-w-sm h-full p-6 shadow-2xl animate-in slide-in-from-left backdrop-blur-xl">
                  <div className="flex justify-between items-center mb-8">
                    <span className="font-bold text-xl text-white">导航</span>
                    <button onClick={() => setMobileMenuOpen(false)}><X size={24} className="text-slate-400" /></button>
                  </div>
                  <nav className="space-y-2">
                    <MobileNavItem label="用户中心" active={currentView === 'user'} onClick={() => handleMobileNavClick('user')} />
                    <MobileNavItem label="Bot 设置" active={currentView === 'bot'} onClick={() => handleMobileNavClick('bot')} />
                    <MobileNavItem label="网盘整理" active={currentView === 'cloud'} onClick={() => handleMobileNavClick('cloud')} />
                    <MobileNavItem label="运行日志" active={currentView === 'logs'} onClick={() => handleMobileNavClick('logs')} />
                    <div className="border-t border-slate-700 my-4 pt-4"></div>
                    <button onClick={toggleTheme} className="w-full text-left px-4 py-3 text-slate-300">切换主题</button>
                    <button onClick={handleLogout} className="w-full text-left px-4 py-3 text-red-400">退出登录</button>
                  </nav>
                </div>
              </div>
            )}

            {/* === 主内容区 === */}
            <div className="flex-1 flex flex-col h-full md:pl-64 transition-all duration-300">
              {/* 移动端 Topbar */}
              <div className="md:hidden sticky top-0 z-40 bg-slate-900/80 backdrop-blur-md border-b border-white/10 px-4 h-16 flex items-center justify-between shrink-0">
                <span className="font-bold text-lg text-white">115 Bot Admin</span>
                <button onClick={() => setMobileMenuOpen(true)} className="p-2 text-slate-300"><Menu size={24} /></button>
              </div>
              
              {/* 关键修改：
                 pb-48 (约192px): 这里的底部边距非常大
                 目的是为了让内容的底部，和侧边栏抬高后的按钮保持视觉上的平行
              */}
              <main className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-8 scroll-smooth custom-scrollbar">
                <div className="max-w-6xl mx-auto min-h-full pb-48">
                  {renderContent()}
                </div>
              </main>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

const MobileNavItem: React.FC<{ label: string; active: boolean; onClick: () => void }> = ({ label, active, onClick }) => (
  <button onClick={onClick} className={`w-full text-left px-4 py-3 rounded-lg font-medium transition-all ${active ? 'bg-blue-600 text-white' : 'text-slate-400'}`}>{label}</button>
);

export default App;
