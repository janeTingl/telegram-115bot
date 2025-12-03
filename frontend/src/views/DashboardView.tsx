
import React from 'react';
import { CommandCard } from '../components/CommandCard';
import { Activity, Server, Database, Wifi, Zap, Wand2 } from 'lucide-react';

export const DashboardView: React.FC = () => {
  const commands = [
    { cmd: '/start', desc: '初始化机器人并检查 115 账号连接状态', example: '/start' },
    { cmd: '/magnet', desc: '添加磁力/Ed2k/HTTP 链接离线任务 (115)', example: '/magnet magnet:?xt=urn:btih:...' },
    { cmd: '/123_offline', desc: '添加 123 云盘离线下载任务', example: '/123_offline http://example.com/file.mp4' },
    { cmd: '/link', desc: '转存 115 分享链接 (支持加密)', example: '/link https://115.com/s/...' },
    { cmd: '/organize', desc: '对 115 默认目录执行自动分类整理', example: '/organize' },
    { cmd: '/123_organize', desc: '对 123 云盘目录执行自动分类整理', example: '/123_organize' },
    { cmd: '/rename', desc: '手动重命名指定文件 (TMDB 匹配)', example: '/rename <file_id> <tmdb_id>' },
    { cmd: '/quota', desc: '查看账号离线配额和空间使用情况', example: '/quota' },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white">系统概览</h2>
        <p className="text-slate-500 dark:text-slate-400">运行状态监测与指令速查</p>
      </div>

      {/* Status Widgets */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-brand-500 to-brand-600 rounded-xl p-6 text-white shadow-lg shadow-brand-500/20">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-white/20 rounded-lg">
              <Activity size={24} />
            </div>
            <span className="bg-green-400 text-xs font-bold px-2 py-1 rounded-full text-brand-900 uppercase">运行中</span>
          </div>
          <div className="text-3xl font-bold mb-1">活跃</div>
          <div className="text-brand-100 text-sm">Docker 服务运行正常</div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-lg">
              <Database size={24} />
            </div>
            <span className="text-xs text-slate-400 dark:text-slate-500">115 API</span>
          </div>
          <div className="text-3xl font-bold text-slate-800 dark:text-white mb-1">已连接</div>
          <div className="text-slate-500 dark:text-slate-400 text-sm flex items-center gap-1">
             <Wifi size={14} className="text-green-500" /> Ping: 45ms
          </div>
        </div>
        
         <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-teal-100 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400 rounded-lg">
              <Wand2 size={24} />
            </div>
            <span className="text-xs text-slate-400 dark:text-slate-500">自动整理</span>
          </div>
          <div className="text-3xl font-bold text-slate-800 dark:text-white mb-1">开启</div>
          <div className="text-slate-500 dark:text-slate-400 text-sm">TMDB 插件正常工作中</div>
        </div>

         <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg">
              <Zap size={24} />
            </div>
            <span className="text-xs text-slate-400 dark:text-slate-500">队列任务</span>
          </div>
          <div className="text-3xl font-bold text-slate-800 dark:text-white mb-1">0</div>
          <div className="text-slate-500 dark:text-slate-400 text-sm">当前无正在进行的下载</div>
        </div>
      </div>

      {/* Commands Grid */}
      <div>
        <div className="flex items-center gap-2 mb-4">
           <Server size={20} className="text-slate-400" />
           <h3 className="text-lg font-bold text-slate-700 dark:text-slate-200">指令速查表</h3>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {commands.map((c) => (
            <CommandCard 
              key={c.cmd} 
              command={c.cmd} 
              description={c.desc} 
              example={c.example} 
            />
          ))}
        </div>
      </div>

      {/* Quick Help */}
      <div className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-6">
        <h4 className="font-bold text-slate-800 dark:text-white mb-2">使用提示</h4>
        <ul className="list-disc list-inside text-sm text-slate-600 dark:text-slate-400 space-y-1">
            <li>直接发送磁力链接、ed2k 链接或 HTTP 链接给机器人，它会自动识别并添加任务。</li>
            <li>发送 115 分享链接 (如 115.com/s/...)，机器人会自动转存到默认目录。</li>
            <li>如果启用了自动整理，任务完成后机器人会尝试匹配 TMDB 信息并按规则移动文件。</li>
            <li>对于识别错误的文件，可以使用 <code>/rename</code> 手动修正。</li>
        </ul>
      </div>
    </div>
  );
};
