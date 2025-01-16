import axios from 'axios';
import { useAuthStore } from '@/store/auth';
import router from '@/router';

export const useAxios = () => {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

    // Create Axios instance
    const axiosInstance = axios.create({
        baseURL: apiBaseUrl,
    });

    // Add a response interceptor
    axiosInstance.interceptors.response.use(
        (response) => response, // Pass through successful responses
        (error) => {
            if (error.response && error.response.status === 401) {
                const authStore = useAuthStore();
                authStore.logout(router); // Trigger logout and redirect to login
            }
            return Promise.reject(error); // Allow local handling if needed
        }
    );

    return {
        axiosInstance,
    };
};