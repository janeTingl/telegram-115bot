import React, { useState, useEffect } from 'react';
import { Folder, ChevronRight, Check, X, HardDrive, ArrowLeft, Cloud, Globe } from 'lucide-react';

interface FileSelectorProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (id: string, name: string) => void;
  title?: string;
  mode?: '115' | '123' | 'openlist'; // 新增模式参数
}

interface FileItem {
  id: string;
  name: string;
  children: boolean;
  date?: string;
}

export const FileSelector: React.FC<FileSelectorProps> = ({ 
  isOpen, onClose, onSelect, title = "选择文件夹", mode = '115' 
}) => {
  // 根目录 ID：115/123 是 "0"，OpenList 是 "/"
  const rootId = mode === 'openlist' ? '/' : '0';
  
  const [history, setHistory] = useState<Array<{id: string, name: string}>>([{id: rootId, name: '根目录'}]);
  const [currentFiles, setCurrentFiles] = useState<FileItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedName, setSelectedName] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // 获取当前目录 ID
  const currentFolderId = history[history.length - 1].id;

  // 加载数据
  useEffect(() => {
    if (!isOpen) return;
    
    const fetchFiles = async () => {
      setIsLoading(true);
      try {
        let url = '';
        // 根据模式构建 API URL
        if (mode === '115') url = `/api/115/files?cid=${encodeURIComponent(currentFolderId)}`;
        else if (mode === '123') url = `/api/123/files?parent_id=${encodeURIComponent(currentFolderId)}`;
        else if (mode === 'openlist') url = `/api/openlist/files?path=${encodeURIComponent(currentFolderId)}`;

        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          // 确保数据是数组
          setCurrentFiles(Array.isArray(data) ? data : []);
        } else {
          console.error("Fetch failed");
          setCurrentFiles([]);
        }
      } catch (e) {
        console.error("Network error", e);
        setCurrentFiles([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFiles();
    // 每次当前目录ID变化时重新加载
  }, [isOpen, currentFolderId, mode]);

  // 重置状态
  useEffect(() => {
    if (isOpen) {
      setHistory([{id: rootId, name: '根目录'}]);
      setSelectedId(null);
    }
  }, [isOpen, mode, rootId]);

  if (!isOpen) return null;

  const handleNavigate = (folder: FileItem) => {
    setHistory([...history, { id: folder.id, name: folder.name }]);
    setSelectedId(null); // 进入新目录清除选中
  };

  const handleUp = () => {
    if (history.length > 1) {
      setHistory(history.slice(0, -1));
      setSelectedId(null);
    }
  };

  const handleConfirm = () => {
    if (selectedId) {
      onSelect(selectedId, selectedName);
      onClose();
    }
  };

  // 图标选择
  const ModeIcon = mode === '115' ? HardDrive : (mode === '123' ? Cloud : Globe);

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-200 dark:border-slate-700 flex flex-col h-[500px]">
        {/* Header */}
        <div className="p-4 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
          <div className="flex items-center gap-2">
             <ModeIcon size={18} className="text-brand-500"/>
             <h3 className="font-bold text-slate-700 dark:text-slate-200">{title}</h3>
             <span className="text-[10px] px-1.5 py-0.5 bg-slate-200 dark:bg-slate-700 rounded text-slate-500 uppercase">{mode}</span>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-full transition-colors">
            <X size={20} className="text-slate-400" />
          </button>
        </div>

        {/* Breadcrumb */}
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
               <div key={p.id + idx} className="flex items-center">
                  <span className={`font-medium max-w-[100px] truncate ${idx === history.length - 1 ? 'text-brand-600 dark:text-brand-400' : 'text-slate-500'}`}>{p.name}</span>
                  {idx < history.length - 1 && <ChevronRight size={14} className="mx-1 text-slate-300" />}
               </div>
             ))}
           </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-2 relative custom-scrollbar">
           {isLoading ? (
             <div className="absolute inset-0 flex items-center justify-center bg-white/50 dark:bg-slate-800/50 z-10">
               <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin"></div>
             </div>
           ) : (
             <>
               {currentFiles.length === 0 ? (
                 <div className="h-full flex flex-col items-center justify-center text-slate-400">
                    <Folder size={48} className="mb-2 opacity-20" />
                    <span className="text-sm">空文件夹</span>
                 </div>
               ) : (
                 currentFiles.map((folder) => (
                   <div 
                      key={folder.id}
                      onClick={() => { setSelectedId(folder.id); setSelectedName(folder.name); }}
                      onDoubleClick={() => folder.children && handleNavigate(folder)}
                      className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors mb-1 group ${selectedId === folder.id ? 'bg-brand-50 dark:bg-brand-900/20 border border-brand-200 dark:border-brand-800' : 'hover:bg-slate-50 dark:hover:bg-slate-700/50 border border-transparent'}`}
                   >
                      <div className="flex items-center gap-3 overflow-hidden">
                         <div className={`p-2 rounded-lg transition-colors shrink-0 ${selectedId === folder.id ? 'bg-brand-100 text-brand-600' : 'bg-slate-100 dark:bg-slate-700 text-slate-500 group-hover:bg-slate-200 dark:group-hover:bg-slate-600'}`}>
                            <Folder size={20} />
                         </div>
                         <div className="truncate">
                            <div className={`text-sm font-medium truncate ${selectedId === folder.id ? 'text-brand-700 dark:text-brand-300' : 'text-slate-700 dark:text-slate-200'}`}>{folder.name}</div>
                            {folder.date && <div className="text-[10px] text-slate-400">{new Date(folder.date * 1000).toLocaleString()}</div>}
                         </div>
                      </div>
                      {folder.children && <ChevronRight size={16} className="text-slate-300 shrink-0" />}
                   </div>
                 ))
               )}
             </>
           )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
           <div className="text-xs text-slate-400 truncate max-w-[200px]">
              {selectedId ? `ID: ${selectedId}` : '请选择一个目录'}
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
