// services/file.ts - 文件管理服务层

export interface FileItem {
  id: string;
  name: string;
  children?: boolean;
  date?: string;
}

export const fileService = {
  /**
   * 列出文件
   * @param path 文件路径或 CID（默认 '0' 为根目录）
   * @param limit 返回数量限制
   */
  async listFiles(path: string = '0', limit: number = 200): Promise<FileItem[]> {
    const response = await fetch(`/api/file/list?path=${encodeURIComponent(path)}&limit=${limit}`);
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('115 Cookie 未设置，请先登录');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    if (data.code !== 0) {
      throw new Error(data.msg || data.detail || '获取文件列表失败');
    }
    
    return data.data as FileItem[];
  },

  /**
   * 移动文件
   * @param src 源路径
   * @param dst 目标路径
   */
  async moveFile(src: string, dst: string): Promise<any> {
    const formData = new FormData();
    formData.append('src', src);
    formData.append('dst', dst);
    
    const response = await fetch('/api/file/move', {
      method: 'POST',
      body: formData,
    });
    
    const data = await response.json();
    if (data.code !== 0) {
      throw new Error(data.msg || '移动文件失败');
    }
    
    return data.data;
  },

  /**
   * 重命名文件
   * @param path 文件路径
   * @param newName 新文件名
   */
  async renameFile(path: string, newName: string): Promise<any> {
    const formData = new FormData();
    formData.append('path', path);
    formData.append('new_name', newName);
    
    const response = await fetch('/api/file/rename', {
      method: 'POST',
      body: formData,
    });
    
    const data = await response.json();
    if (data.code !== 0) {
      throw new Error(data.msg || '重命名失败');
    }
    
    return data.data;
  },

  /**
   * 通知 Emby 刷新
   * @param path 文件路径
   */
  async notifyEmby(path: string): Promise<void> {
    const formData = new FormData();
    formData.append('path', path);
    
    const response = await fetch('/api/file/notify_emby', {
      method: 'POST',
      body: formData,
    });
    
    const data = await response.json();
    if (data.code !== 0) {
      throw new Error(data.msg || '通知 Emby 失败');
    }
  },

  /**
   * 上传文件
   * @param file 文件对象
   */
  async uploadFile(file: File): Promise<{ filename: string; path: string }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/files/upload', {
      method: 'POST',
      body: formData,
    });
    
    const data = await response.json();
    if (data.code !== 0) {
      throw new Error(data.msg || '上传文件失败');
    }
    
    return data.data;
  },
};
