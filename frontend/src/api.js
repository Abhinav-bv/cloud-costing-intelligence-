/**
 * API Configuration
 * Dynamically uses VITE_API_URL environment variable or falls back to localhost
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const fetchStats = async () => {
  try {
    const response = await fetch(`${API_URL}/api/stats`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch stats from API:', error);
    return null;
  }
};

export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};

export default API_URL;
