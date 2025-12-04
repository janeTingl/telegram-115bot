import React, { useState, useEffect, useCallback } from 'react';
import { Folder, ChevronRight, Check, X, HardDrive, ArrowLeft, Loader2 } from 'lucide-react';
// 假设这是你的 API 客户端服务，请根据你的项目路径修改
import { api } from '../services/api'; 

interface FileSelectorProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (cid: string, name: string) => void;
  title?: string;
}

// 定义前端期望的数据结构
interface FileItem {
  id: string;
  name: string;
  children: boolean;
  date: string;
}

export const FileSelector: React.FC<FileSelectorProps> = ({ isOpen, onClose, onSelect, title = "选择文件夹" }) => {
  const [history, setHistory] = useState<Array<{id: string, name: string}>>([{id: '0', name: '根目录'}]);
  const [currentFiles, setCurrentFiles] = useState<FileItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedName, setSelectedName] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFiles = useCallback(async (cid: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // **【关键修改点：适配后端路由 /api/file/list?path=cid】**
      const response = await api.get(`/api/file/list?path=${cid}`); 
      
      if (response && response.code === 0 && response.data) {
        // 假设后端成功时返回的结构是 { code: 0, data: FileItem[] }
        setCurrentFiles(response.data);
      } else {
        const msg = response?.msg || "获取列表失败，未知错误。";
        setError(`115 接口错误: ${msg}`);
        setCurrentFiles([]);
      }
      setSelectedId(null);
      setSelectedName('');
    } catch (err) {
      console.error("Error fetching 115 files:", err);
      setError("无法连接到后端服务，请检查网络或配置。");
      setCurrentFiles([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      const rootFolder = {id: '0', name: '根目录'};
      setHistory([rootFolder]);
      fetchFiles(rootFolder.id);
    }
  }, [isOpen, fetchFiles]);

  if (!isOpen) return null;

  const handleNavigate = (folder: {id: string, name: string}) => {
    setHistory(prev => [...prev, folder]);
    fetchFiles(folder.id);
  };

  const handleUp = () => {
    if (history.length > 1) {
      const newHistory = history.slice(0, -1);
      const prevFolderId = newHistory[newHistory.length - 1].id;
      setHistory(newHistory);
      fetchFiles(prevFolderId);
    }
  };

  const handleConfirm = () => {
    if (selectedId) {
      onSelect(selectedId, selectedName);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-200 dark:border-slate-700 flex flex-col h-[500px]">
        {/* Header */}
        <div className="p-4 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
          <div className="flex items-center gap-2">
             <HardDrive size={18} className="text-brand-500"/>
             <h3 className="font-bold text-slate-700 dark:text-slate-200">{title}</h3>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-full transition-colors">
            <X size={20} className="text-slate-400" />
          </button>
        </div>

        {/* Breadcrumb / Navigation */}
        <div className="p-3 bg-slate-100 dark:bg-slate-900/30 flex items-center gap-2 text-sm border-b border-slate-200 dark:border-slate-700">
           <button 
             onClick={handleUp} 
             disabled={history.length <= 1}
             className="p-1.5 bg-white dark:bg-slate-700 rounded-md text-slate-600 dark:text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
           >
             <ArrowLeft size={16} />
           </button>
           <div className="flex-1 overflow-x-auto scrollbar-hide flex items-center whitespace-nowrap">
             {history.map((p, idx) => (
               <div key={p.id} className="flex items-center">
                  <span className={`font-medium ${idx === history.length - 1 ? 'text-brand-600 dark:text-brand-400' : 'text-slate-500'}`}>{p.name}</span>
                  {idx < history.length - 1 && <ChevronRight size={14} className="mx-1 text-slate-300" />}
               </div>
             ))}
           </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-2 relative">
           {isLoading ? (
             <div className="absolute inset-0 flex items-center justify-center bg-white/50 dark:bg-slate-800/50 z-10">
               <Loader2 size={32} className="text-brand-600 animate-spin" />
             </div>
           ) : (
             <>
               {error ? (
                 <div className="h-full flex flex-col items-center justify-center text-red-500 text-sm p-4">
                     <X size={48} className="mb-2 opacity-50" />
                     {error}
                 </div>
               ) : currentFiles.length === 0 ? (
                 <div className="h-full flex flex-col items-center justify-center text-slate-400">
                    <Folder size={48} className="mb-2 opacity-20" />
                    <span className="text-sm">空文件夹或数据加载失败</span>
                 </div>
               ) : (
                 currentFiles.map((folder) => (
                   <div 
                      key={folder.id}
                      onClick={() => { setSelectedId(folder.id); setSelectedName(folder.name); }}
                      onDoubleClick={() => folder.children && handleNavigate(folder)}
                      className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors mb-1 group ${selectedId === folder.id ? 'bg-brand-50 dark:bg-brand-900/20 border border-brand-200 dark:border-brand-800' : 'hover:bg-slate-50 dark:hover:bg-slate-700/50 border border-transparent'}`}
                   >
                      <div className="flex items-center gap-3">
                         <div className={`p-2 rounded-lg transition-colors ${selectedId === folder.id ? 'bg-brand-100 text-brand-600' : 'bg-slate-100 dark:bg-slate-700 text-slate-500 group-hover:bg-slate-200 dark:group-hover:bg-slate-600'}`}>
                            <Folder size={20} />
                         </div>
                         <div>
                            <div className={`text-sm font-medium ${selectedId === folder.id ? 'text-brand-700 dark:text-brand-300' : 'text-slate-700 dark:text-slate-200'}`}>{folder.name}</div>
                            <div className="text-[10px] text-slate-400">{folder.date}</div>
                         </div>
                      </div>
                      {folder.children && <ChevronRight size={16} className="text-slate-300" />}
                   </div>
                 ))
               )}
             </>
           )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
           <div className="text-xs text-slate-400">
              {selectedId ? `已选择: ${selectedName} (CID: ${selectedId})` : '请选择一个目录'}
           </div>
           <div className="flex gap-3">
             <button onClick={onClose} className="px-4 py-2 text-slate-500 hover:text-slate-700 text-sm font-medium">取消</button>
             <button 
               onClick={handleConfirm}
               disabled={!selectedId}
               className="px-6 py-2 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white rounded-lg text-sm font-bold flex items-center gap-2 shadow-lg shadow-brand-500/20 transition-all active:scale-95"
             >
               <Check size={16} /> 确认
             </button>
           </div>
        </div>
      </div>
    </div>
  );
};