import axios from 'axios'
import { useParticipantStore } from '../store/participant'
import { useAuthStore } from '../store/auth'

// Create custom axios instance
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor
axiosInstance.interceptors.request.use(config => {
  const participantStore = useParticipantStore()
  const authStore = useAuthStore()

  // First check for participant token
  if (participantStore.token) {
    console.log('[Axios] Adding participant token:', participantStore.token.substring(0, 20) + '...');
    config.headers.Authorization = `Bearer ${participantStore.token}`;
  }
  // If no participant token but user is authenticated, use FormShip token
  else if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }

  return config;
}, error => {
  console.error('[Axios] Request interceptor error:', error);
  return Promise.reject(error);
});

// Add response interceptor
axiosInstance.interceptors.response.use(
  response => response,
  async error => {
    console.error('[Axios] Response error:', error.response?.status, error.response?.data);
    
    if (error.response?.status === 401) {
      const participantStore = useParticipantStore()
      if (participantStore.isAuthenticated) {
        console.error('[Axios] Unauthorized request, clearing participant data');
        participantStore.clearParticipant();
        
        // Only redirect if we're not already on the login page
        if (!window.location.pathname.includes('/participant/login')) {
          window.location.href = '/participant/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default axiosInstance; 