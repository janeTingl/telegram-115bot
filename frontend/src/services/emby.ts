// services/emby.ts - Emby 媒体服务器服务层

export const embyService = {
  /**
   * 刷新 Emby 媒体库并探测项目
   * @param itemId Emby 项目 ID（可选）
   */
  async refreshAndProbe(itemId?: string): Promise<void> {
    const formData = new FormData();
    if (itemId) {
      formData.append('item_id', itemId);
    }

    const response = await fetch('/api/emby/refresh_and_probe', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    
    if (data.code === 1) {
      throw new Error('Emby 未配置');
    }
    
    if (data.code === 429) {
      throw new Error('请求频率过高，请稍后再试');
    }
    
    if (data.code !== 0) {
      throw new Error(data.msg || 'Emby 刷新失败');
    }
  },

  /**
   * 简化版：仅刷新媒体库
   */
  async refresh(): Promise<void> {
    return this.refreshAndProbe();
  },
};
