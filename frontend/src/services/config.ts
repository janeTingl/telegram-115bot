// services/config.ts (完整代码，包含之前新增的函数)

interface ProxySettings {
    enabled: boolean;
    type: string;
    host: string;
    port: string;
}

// 假设 AppConfig 类型已从其他文件导入
// import { AppConfig } from '../types';
type AppConfig = any; 

// --- Config R/W ---
export const loadGlobalConfig = async (): Promise<AppConfig> => {
    const response = await fetch('/api/config/load', { method: 'GET' });
    const data = await response.json();
    if (data.code === 0) {
        return data.data as AppConfig;
    } else {
        throw new Error(data.msg || "无法从后端加载配置");
    }
};

export const saveGlobalConfig = async (config: AppConfig): Promise<void> => {
    const response = await fetch('/api/config/save_all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
    });
    
    const data = await response.json();
    if (data.code !== 0) {
        throw new Error(data.msg || "配置保存失败");
    }
};


// --- Password & Proxy ---
export const saveAdminPassword = async (newPassword: string): Promise<void> => {
    const formData = new FormData();
    formData.append('new_password', newPassword); 
    
    const response = await fetch('/api/auth/password', {
        method: 'POST',
        body: formData,
    });
    
    const data = await response.json();
    if (data.code !== 0) {
        throw new Error(data.msg || "修改密码失败");
    }
};

export const saveProxyConfig = async (proxyConfig: ProxySettings): Promise<void> => {
    const response = await fetch('/api/config/proxy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(proxyConfig),
    });
    
    const data = await response.json();
    if (data.code !== 0) {
        throw new Error(data.msg || "保存代理配置失败");
    }
};


// --- 2FA ---
export const generate2FASecret = async (): Promise<{ secret: string; otpauthUrl: string }> => {
    const response = await fetch('/api/auth/2fa/generate', {
        method: 'GET',
    });
    
    const data = await response.json();
    if (data.code === 0) {
        return { secret: data.data.secret, otpauthUrl: data.data.otpauth_url };
    } else {
        throw new Error(data.msg || "获取 2FA 密钥失败");
    }
};

export const verifyAndSave2FA = async (secret: string, code: string): Promise<void> => {
    const formData = new FormData();
    formData.append('secret', secret);
    formData.append('code', code); 

    const response = await fetch('/api/auth/2fa/verify', {
        method: 'POST',
        body: formData,
    });

    const data = await response.json();
    if (data.code !== 0) {
        throw new Error(data.msg || "2FA 验证失败");
    }
};


// --- Settings Service (unified endpoint) ---
export const loadSettings = async (): Promise<AppConfig> => {
    const response = await fetch('/api/config', { method: 'GET' });
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    return data as AppConfig;
};

export const saveSettings = async (config: AppConfig): Promise<void> => {
    const response = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    if (data.code !== 0) {
        throw new Error(data.msg || "配置保存失败");
    }
};

export const testEmbyConnection = async (embyConfig: { host: string; api_key: string }): Promise<{ success: boolean; serverName?: string; version?: string; error?: string }> => {
    const response = await fetch('/api/emby/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(embyConfig),
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
};