const API_BASE_URL = 'http://localhost:8000/api';

export const fetchClusterData = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/cluster`);
        return await response.json();
    } catch (error) {
        console.error("Backend unreachable", error);
        return null; // Handle graceful failure in UI if needed
    }
};

export const triggerChaos = async () => {
    await fetch(`${API_BASE_URL}/chaos`, { method: 'POST' });
};

export const autoRecover = async () => {
    await fetch(`${API_BASE_URL}/recover`, { method: 'POST' });
};
