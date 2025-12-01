import React from 'react';
import { UserCog, Bot, CloudCog, Tv, FileVideo, Terminal, LogOut, Sun, Moon, LayoutDashboard, Radio } from 'lucide-react';

interface SidebarProps {
  currentView: string;
  onChangeView: (view: string) => void;
  isDark: boolean;
  toggleTheme: () => void;
  onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onChangeView, isDark, toggleTheme, onLogout }) => {
  const navItems = [
    { id: 'user', label: '用户中心', icon: UserCog },
    { id: 'bot', label: '机器人设置', icon: Bot },
    { id: 'cloud', label: '网盘整理', icon: CloudCog },
    { id: 'emby', label: 'Emby 联动', icon: Tv },
    { id: 'strm', label: 'STRM 生成', icon: FileVideo },
    { id: 'logs', label: '运行日志', icon: Terminal },
  ];

  return (
    <div className="
      hidden md:flex flex-col w-64
      /* 这里的样式是你喜欢的磨砂质感 */
      bg-slate-100/90 dark:bg-slate-900/90 
      backdrop-blur-xl 
      text-slate-700 dark:text-slate-300
      h-screen fixed left-0 top-0 shadow-2xl z-30
      border-r border-white/20 dark:border-slate-700/50
      overflow-y-auto custom-scrollbar
    ">
      {/* Logo */}
      <div className="p-6 border-b border-slate-200/50 dark:border-slate-700/50 shrink-0">
        <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-lg shadow-lg shadow-indigo-500/30">
                <LayoutDashboard className="text-white" size={24} />
            </div>
            <div>
                <h1 className="font-bold text-lg tracking-tight text-slate-800 dark:text-white leading-none">
                    115 Bot
                </h1>
                <span className="text-[10px] font-semibold text-indigo-500 dark:text-indigo-400 tracking-wider uppercase">
                    Admin Panel
                </span>
            </div>
        </div>
      </div>

      {/* 菜单 */}
      <nav className="p-4 space-y-1 shrink-0">
        <div className="text-[10px] font-bold text-slate-500/70 dark:text-slate-500 uppercase tracking-widest mb-3 px-3 mt-2">
          功能菜单
        </div>

        {navItems.map((item) => {
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onChangeView(item.id)}
              className={`
                w-full flex items-center gap-3 px-3 py-3 rounded-xl
                transition-all duration-200 group relative overflow-hidden
                ${isActive 
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20' 
                  : 'hover:bg-white/50 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-white'
                }
              `}
            >
              <item.icon
                size={18}
                className={`transition-colors ${isActive ? 'text-white' : 'text-slate-500 group-hover:text-slate-800 dark:group-hover:text-white'}`}
              />
              <span className={`font-medium text-sm tracking-wide ${isActive ? 'font-bold' : ''}`}>
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      {/* 占位符 - 把按钮推到底部 */}
      <div className="flex-1 min-h-[40px]"></div>

      {/* 分割线 */}
      <div className="mx-6 border-t border-slate-200/50 dark:border-slate-700/50"></div>

      {/* 底部按钮 (padding-bottom 40 = 160px) */}
      <div className="p-4 pt-4 pb-40 shrink-0">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-white/50 dark:bg-black/20 border border-white/20 dark:border-white/5 mb-3">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)] animate-pulse"></div>
          <span className="text-xs font-medium text-slate-600 dark:text-slate-300">端口:12808</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <button 
            onClick={toggleTheme}
            className="flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-white/10 rounded-lg transition-colors border border-transparent hover:border-slate-200 dark:hover:border-slate-700"
          >
            {isDark ? <Sun size={14} /> : <Moon size={14} />}
            主题
          </button>
          
          <button 
            onClick={onLogout}
            className="flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors border border-transparent hover:border-red-100 dark:hover:border-red-900/30"
          >
            <LogOut size={14} />
            退出
          </button>
        </div>
      </div>
    </div>
  );
};
