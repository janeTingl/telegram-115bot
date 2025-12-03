// services/task.ts
export const startOrganizeTask = async (): Promise<{ status: string; job_id?: string }> => {
    try {
        const response = await fetch('/api/file/organize/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}), 
        });
        
        const data = await response.json();
        
        if (data.code === 0) {
            return { status: 'success', job_id: data.data.job_id };
        } else {
            throw new Error(data.msg || '任务启动失败');
        }
    } catch (error) {
        console.error("Failed to start organize task:", error);
        throw new Error(`无法连接后端或启动任务: ${error.message}`);
    }
};