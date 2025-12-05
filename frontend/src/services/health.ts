// services/health.ts - 健康检查和系统信息服务层

export interface HealthReport {
  generated_at: string;
  summary: {
    total_registered_routes: number;
    expected_endpoint_total: number;
    expected_available: number;
    missing_or_incomplete: number;
    backend_only: number;
    frontend_services_total: number;
    frontend_without_backend: number;
    health_score: number;
  };
  expected_endpoints: Array<{
    category: string;
    name: string;
    method: string;
    path: string;
    description: string;
    status: 'ok' | 'backend_only' | 'frontend_only' | 'missing';
    has_backend: boolean;
    frontend_services: string[];
  }>;
  backend_routes: Array<{
    method: string;
    path: string;
    name?: string;
    summary?: string;
  }>;
  frontend_services: Array<{
    name: string;
    file: string;
    method: string;
    path: string;
    backend_available: boolean;
  }>;
  missing_endpoints: any[];
  backend_only_endpoints: any[];
}

export interface VersionInfo {
  version: string;
  name: string;
}

export interface StatusInfo {
  uptime: number;
  version: string;
}

export const healthService = {
  /**
   * 获取完整的健康检查报告
   */
  async getReport(): Promise<HealthReport> {
    const response = await fetch('/api/health/report');
    const data = await response.json();
    
    if (data.code !== 0) {
      throw new Error(data.msg || '获取健康报告失败');
    }
    
    return data.data;
  },

  /**
   * 获取版本信息
   */
  async getVersion(): Promise<VersionInfo> {
    const response = await fetch('/api/version');
    const data = await response.json();
    
    if (data.code !== 0) {
      throw new Error(data.msg || '获取版本信息失败');
    }
    
    return data.data;
  },

  /**
   * 获取运行状态
   */
  async getStatus(): Promise<StatusInfo> {
    const response = await fetch('/api/status');
    const data = await response.json();
    
    if (data.code !== 0) {
      throw new Error(data.msg || '获取状态信息失败');
    }
    
    return data.data;
  },

  /**
   * 简单的健康检查（轻量级）
   */
  async check(): Promise<boolean> {
    try {
      const response = await fetch('/healthz');
      return response.ok && (await response.text()) === 'ok';
    } catch {
      return false;
    }
  },
};
