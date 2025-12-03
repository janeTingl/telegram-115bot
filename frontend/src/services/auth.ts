const AUTH_KEY = '115_BOT_AUTH_TOKEN';
const ATTEMPTS_KEY = '115_BOT_LOGIN_ATTEMPTS';
const TWO_FA_KEY = '115_BOT_2FA_SESSION';
const MAX_ATTEMPTS = 5;

export const getFailedAttempts = (): number => {
  return parseInt(localStorage.getItem(ATTEMPTS_KEY) || '0', 10);
};

export const isLocked = (): boolean => {
  return getFailedAttempts() >= MAX_ATTEMPTS;
};

const incrementAttempts = () => {
  const current = getFailedAttempts();
  localStorage.setItem(ATTEMPTS_KEY, (current + 1).toString());
};

const resetAttempts = () => {
  localStorage.removeItem(ATTEMPTS_KEY);
};

export const checkAuth = (): boolean => {
  return localStorage.getItem(AUTH_KEY) === 'true';
};

export const logout = () => {
  localStorage.removeItem(AUTH_KEY);
  sessionStorage.removeItem(TWO_FA_KEY);
};

export const login = async (username: string, pass: string): Promise<{ success: boolean; locked: boolean }> => {
  const attempts = getFailedAttempts();
  
  if (attempts >= MAX_ATTEMPTS) {
    return { success: false, locked: true };
  }

  const formData = new FormData();
  formData.append('password', pass); 

  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    if (result.code === 0) {
      localStorage.setItem(AUTH_KEY, 'true'); 
      resetAttempts();
      return { success: true, locked: false };
    } else {
      incrementAttempts();
      return { success: false, locked: getFailedAttempts() >= MAX_ATTEMPTS };
    }
  } catch (error) {
    console.error("Login API error. Ensure backend is running and proxy is set up.", error);
    incrementAttempts(); 
    return { success: false, locked: getFailedAttempts() >= MAX_ATTEMPTS };
  }
};