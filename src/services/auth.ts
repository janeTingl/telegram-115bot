const AUTH_KEY = '115_BOT_AUTH_TOKEN';
const TWO_FA_KEY = '115_BOT_2FA_SESSION';

// 检查是否已登录 (用于路由保护)
export const checkAuth = (): boolean => {
  return localStorage.getItem(AUTH_KEY) === 'true';
};

// 退出登录
export const logout = () => {
  localStorage.removeItem(AUTH_KEY);
  sessionStorage.removeItem(TWO_FA_KEY);
};

// --- 前端敏感信息查看保护 (2FA) ---
// 这是一个前端层面的二次锁，防止误操作修改 Key
// 实际的后端配置保存由后端鉴权拦截

export const check2FA = (): boolean => {
  return sessionStorage.getItem(TWO_FA_KEY) === 'true';
};

export const verify2FA = (code: string): boolean => {
  // 默认的前端解锁码，简单防止误触
  // 如果需要更高级的安全，这里应该调用后端接口 /api/verify_2fa
  if (code === '123456') {
    sessionStorage.setItem(TWO_FA_KEY, 'true');
    return true;
  }
  return false;
};

// 获取失败次数 (前端仅做展示，实际锁定由后端控制)
export const getFailedAttempts = (): number => {
  return 0; // 实际逻辑已移交后端
};

export const isLocked = (): boolean => {
  return false; // 实际逻辑已移交后端
};

// 登录成功后调用
export const loginSuccess = () => {
  localStorage.setItem(AUTH_KEY, 'true');
};
