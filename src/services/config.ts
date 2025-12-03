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

// ----------------------------------------------------
// 新增 2FA 连通函数
// ----------------------------------------------------

// 1. 获取密钥和二维码URL
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

// 2. 验证并保存密钥
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