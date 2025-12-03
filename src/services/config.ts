// services/config.ts

interface ProxySettings {
    enabled: boolean;
    type: string;
    host: string;
    port: string;
}

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