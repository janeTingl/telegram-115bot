// services/offline.ts - 离线下载服务层

export interface OfflineTask {
  local_task_id: string;
  remote: any;
}

export interface OfflineStatus {
  status?: string;
  state?: string;
  progress?: number;
  [key: string]: any;
}

export const offlineService = {
  /**
   * 创建离线下载任务
   * @param url 下载链接
   * @param targetFolder 目标文件夹（默认 '/'）
   * @param notifyTg 是否通知 Telegram（默认 true）
   */
  async createTask(
    url: string,
    targetFolder: string = '/',
    notifyTg: boolean = true
  ): Promise<OfflineTask> {
    const response = await fetch('/api/offline/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url,
        target_folder: targetFolder,
        notify_tg: notifyTg,
      }),
    });

    const data = await response.json();
    
    if (data.code === 429) {
      throw new Error('达到 115 QPS 限制，请稍后再试');
    }
    
    if (data.code !== 0) {
      throw new Error(data.msg || '创建离线任务失败');
    }

    return data.data;
  },

  /**
   * 查询离线任务状态
   * @param taskId 任务 ID
   */
  async getTaskStatus(taskId: string): Promise<OfflineStatus> {
    const response = await fetch(`/api/offline/status?task_id=${encodeURIComponent(taskId)}`);
    const data = await response.json();
    
    if (data.code === 1) {
      throw new Error('任务不存在');
    }
    
    if (data.code !== 0) {
      throw new Error(data.msg || '查询任务状态失败');
    }

    return data.data;
  },
};
