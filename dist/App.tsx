
import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { UserCenterView } from './views/UserCenterView';
import { BotSettingsView } from './views/BotSettingsView';
import { CloudOrganizeView } from './views/CloudOrganizeView';
import { EmbyView } from './views/EmbyView';
import { StrmView } from './views/StrmView';
import { LogsView } from './views/LogsView';
import { LoginView } from './views/LoginView';
import { ViewState } from './types';
import { checkAuth, logout } from './services/auth';
import { loadConfig } from './services/mockConfig';
import { Menu } from 'lucide-react';

// High-quality Sci-Fi/Tech/Cinematic backdrops suitable for a Bot Admin Interface
const FALLBACK_BACKDROPS = [
  'https://image.tmdb.org/t/p/original/ilRyazdMJwN05exqhwK4tMKBYZs.jpg', // Blade Runner 2049 (Orange/Teal)
  'https://image.tmdb.org/t/p/original/kjFonKwBSNYiQ8fVvnYhBL9s9E7.jpg', // Tron: Legacy (Blue/Tech)
  'https://image.tmdb.org/t/p/original/jYEW5xZkZk2WTrdbMGAPFuBqbDc.jpg', // Dune (Minimalist/Sand)
  'https://image.tmdb.org/t/p/original/rAiYTfKGqDCRIIqo664sY9XZIVQ.jpg', // Interstellar (Space)
  'https://image.tmdb.org/t/p/original/5p3aIQUw425L5VdFtO9TysVwN5G.jpg', // The Creator (Modern Sci-Fi)
  'https://image.tmdb.org/t/p/original/8rpDcsfLJypbO6vREc0547FVq5q.jpg', // Avatar (Blue/Nature)
  'https://image.tmdb.org/t/p/original/tmU7GeKVybMWFButWEGl2Mdbj47.jpg', // The Godfather (Dark/Classic)
];

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [currentView, setCurrentView] = useState<ViewState>(ViewState.USER_CENTER);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Background State
  const [backdrops, setBackdrops] = useState<string[]>([]);
  const [currentBackdropIndex, setCurrentBackdropIndex] = useState(0);

  // Theme State
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

  // Theme Effect
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

  // Global Background Fetching (TMDB High Quality)
  useEffect(() => {
    const fetchBackdrops = async () => {
        const config = loadConfig();
        const apiKey = config.tmdb.apiKey;
        
        let loaded = false;
        if (apiKey && apiKey.length > 10) {
            try {
                // Use 'discover' to filter for high quality (High popularity + High vote count)
                // Added with_genres=878 (Science Fiction) to match the Bot/Tech theme better
                const res = await fetch(`https://api.themoviedb.org/3/discover/movie?api_key=${apiKey}&language=zh-CN&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&vote_count.gte=1000&vote_average.gte=7&with_genres=878`);
                
                if (res.ok) {
                    const data = await res.json();
                    if (data.results && data.results.length > 0) {
                         const paths = data.results
                            .filter((m: any) => m.backdrop_path)
                            .slice(0, 8) // Top 8 High Quality
                            .map((m: any) => `https://image.tmdb.org/t/p/original${m.backdrop_path}`);
                         
                         if (paths.length > 0) {
                             setBackdrops(paths);
                             loaded = true;
                         }
                    }
                }
            } catch (e) {
                console.warn('Failed to fetch TMDB backdrops', e);
            }
        }
        
        if (!loaded) {
            setBackdrops(FALLBACK_BACKDROPS);
        }
    };

    fetchBackdrops();
  }, []);

  // Slideshow Timer
  useEffect(() => {
    if (backdrops.length <= 1) return;
    const interval = setInterval(() => {
        setCurrentBackdropIndex(prev => (prev + 1) % backdrops.length);
    }, 15000); // Slower transition (15s) for better ambiance
    return () => clearInterval(interval);
  }, [backdrops]);

  const toggleTheme = () => setIsDark(!isDark);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    logout(); 
    setIsAuthenticated(false); 
    setMobileMenuOpen(false);
    setCurrentView(ViewState.USER_CENTER); 
  };

  const renderContent = () => {
    switch (currentView) {
      case ViewState.USER_CENTER: return <UserCenterView />;
      case ViewState.BOT_SETTINGS: return <BotSettingsView />;
      case ViewState.CLOUD_ORGANIZE: return <CloudOrganizeView />;
      case ViewState.EMBY_INTEGRATION: return <EmbyView />;
      case ViewState.STRM_GENERATION: return <StrmView />;
      case ViewState.LOGS: return <LogsView />;
      default: return <UserCenterView />;
    }
  };

  if (isChecking) {
    return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-slate-500">Loading...</div>;
  }

  return (
    <div className="min-h-screen font-sans transition-colors duration-300 relative overflow-x-hidden">
      {/* Global Background Layer */}
      <div className="fixed inset-0 z-0 bg-slate-900">
         {backdrops.map((img, idx) => (
            <div 
               key={idx}
               className={`absolute inset-0 bg-cover bg-center bg-no-repeat bg-fixed transition-opacity duration-[3000ms] ease-in-out ${idx === currentBackdropIndex ? 'opacity-100' : 'opacity-0'}`}
               style={{ backgroundImage: `url(${img})` }}
            />
         ))}
         
         {/* Theme Overlays - Removed Blur for HD Clarity */}
         {/* Light Mode: Very subtle white gradient to keep text readable but show image clearly */}
         <div className={`absolute inset-0 transition-all duration-1000 ${isDark ? 'opacity-0' : 'opacity-100 bg-gradient-to-br from-white/80 via-white/40 to-white/10'}`}></div>
         
         {/* Dark Mode: Subtle dark gradient */}
         <div className={`absolute inset-0 transition-all duration-1000 ${isDark ? 'opacity-100 bg-gradient-to-br from-slate-950/80 via-slate-900/60 to-slate-900/20' : 'opacity-0'}`}></div>
      </div>

      <div className="relative z-10 h-full">
        {!isAuthenticated ? (
          <LoginView onLoginSuccess={handleLoginSuccess} />
        ) : (
          <div className="min-h-screen text-slate-900 dark:text-slate-100 flex flex-col md:flex-row">
            {/* Mobile Header */}
            <div className="md:hidden bg-white/90 dark:bg-slate-900/90 backdrop-blur-md text-slate-800 dark:text-white p-4 flex justify-between items-center sticky top-0 z-50 shadow-md border-b border-slate-200 dark:border-white/5 w-full">
              <span className="font-bold text-lg">115 Bot Admin</span>
              <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
                <Menu size={24} />
              </button>
            </div>

            {/* Mobile Menu Overlay */}
            {mobileMenuOpen && (
              <div className="fixed inset-0 bg-white/98 dark:bg-slate-950/98 z-50 md:hidden pt-20 px-6 backdrop-blur-sm animate-in slide-in-from-top-10 duration-200 overflow-y-auto">
                <nav className="space-y-4">
                  <button onClick={() => { setCurrentView(ViewState.USER_CENTER); setMobileMenuOpen(false); }} className="block w-full text-left text-xl text-slate-700 dark:text-white py-2 font-medium hover:text-brand-600">用户中心</button>
                  <button onClick={() => { setCurrentView(ViewState.BOT_SETTINGS); setMobileMenuOpen(false); }} className="block w-full text-left text-xl text-slate-700 dark:text-white py-2 font-medium hover:text-brand-600">Bot 设置</button>
                  <button onClick={() => { setCurrentView(ViewState.CLOUD_ORGANIZE); setMobileMenuOpen(false); }} className="block w-full text-left text-xl text-slate-700 dark:text-white py-2 font-medium hover:text-brand-600">网盘整理</button>
                  <button onClick={() => { setCurrentView(ViewState.EMBY_INTEGRATION); setMobileMenuOpen(false); }} className="block w-full text-left text-xl text-slate-700 dark:text-white py-2 font-medium hover:text-brand-600">Emby 联动</button>
                  <button onClick={() => { setCurrentView(ViewState.STRM_GENERATION); setMobileMenuOpen(false); }} className="block w-full text-left text-xl text-slate-700 dark:text-white py-2 font-medium hover:text-brand-600">STRM 生成</button>
                  <button onClick={() => { setCurrentView(ViewState.LOGS); setMobileMenuOpen(false); }} className="block w-full text-left text-xl text-slate-700 dark:text-white py-2 font-medium hover:text-brand-600">运行日志</button>
                  <div className="border-t border-slate-200 dark:border-slate-800 my-4"></div>
                  <button onClick={toggleTheme} className="block w-full text-left text-xl text-slate-700 dark:text-white py-2 font-medium hover:text-brand-600">{isDark ? '切换亮色模式' : '切换暗色模式'}</button>
                  <button onClick={handleLogout} className="block w-full text-left text-xl text-red-500 py-2 font-medium hover:text-red-600">退出登录</button>
                </nav>
              </div>
            )}

            <Sidebar 
              currentView={currentView} 
              onChangeView={setCurrentView} 
              isDark={isDark}
              toggleTheme={toggleTheme}
              onLogout={handleLogout}
              collapsed={sidebarCollapsed}
              toggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
            />

            {/* Main Content Area */}
            <main className={`flex-1 min-h-screen transition-all duration-300 w-full ${sidebarCollapsed ? 'md:pl-20' : 'md:pl-64'}`}>
              <div className="w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-24">
                {renderContent()}
              </div>
            </main>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
