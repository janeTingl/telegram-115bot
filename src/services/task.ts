// services/task.ts
export const startOrganizeTask = async () => {
    const response = await fetch('/api/organize/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // 注意：这里不需要发送配置，因为后端应该从自己的存储中读取配置
        body: JSON.stringify({ action: 'start' }) 
    });
    
    if (!response.ok) {
        throw new Error('Failed to start task');
    }
    return response.json();
};
