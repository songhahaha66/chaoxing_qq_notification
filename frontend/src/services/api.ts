import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';
import { ElMessage } from 'element-plus';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const authStore = useAuthStore();

    // Check for 401 error and if it's not a token refresh attempt itself
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Mark that we've attempted to refresh

      if (authStore.refreshToken) {
        try {
          // Attempt to refresh the token
          const response = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL}/refresh-token`,
            { refresh_token: authStore.refreshToken },
            { headers: { 'Content-Type': 'application/json' } }
          );

          const newAccessToken = response.data.access_token;
          // Note: The backend should ideally return a new refresh token as well if it's a one-time use refresh token.
          // Assuming the current refresh token is still valid or a new one is also provided.
          // For simplicity, if a new refresh token is returned, it should also be updated in the store.
          // const newRefreshToken = response.data.refresh_token; 
          // authStore.setTokens(newAccessToken, newRefreshToken || authStore.refreshToken);
          authStore.setTokens(newAccessToken, authStore.refreshToken); // Or handle new refresh token if provided

          // Update the original request's header with the new token
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          
          // Retry the original request
          return apiClient(originalRequest);
        } catch (refreshError: any) {
          // Handle failed token refresh
          ElMessage.error(refreshError.response?.data?.detail || '会话已过期，请重新登录。');
          authStore.logout(); // Clear tokens and redirect to login
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available, logout user
        ElMessage.error('会话已过期或无效，请重新登录。');
        authStore.logout();
        return Promise.reject(error);
      }
    }
    // For other errors, just pass them on
    return Promise.reject(error);
  }
);

export default apiClient;

