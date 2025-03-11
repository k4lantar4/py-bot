/**
 * API service for the 3X-UI Management System.
 * 
 * This module provides functions for communicating with the backend API.
 */

import axios from 'axios';
import { handleAPIError } from '../utils/errorHandler';

// Get the API URL from environment variables or construct it
const getApiUrl = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Get the current hostname (will be the public IP or domain in production)
  const hostname = window.location.hostname;
  const port = '8000';
  const protocol = window.location.protocol;
  
  return `${protocol}//${hostname}:${port}/api/v1`;
};

// Create axios instance
const apiClient = axios.create({
  baseURL: getApiUrl(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Language': localStorage.getItem('language') || 'fa',
  },
});

// Request queue for handling 401 errors
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(handleAPIError(error));
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        processQueue(new Error('No refresh token'));
        return Promise.reject(handleAPIError(error));
      }

      try {
        const response = await axios.post(
          `${getApiUrl()}/auth/refresh-token`,
          { refresh_token: refreshToken },
          { headers: { 'Content-Type': 'application/json' } }
        );

        const { access_token, refresh_token } = response.data;
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem('refreshToken', refresh_token);

        apiClient.defaults.headers['Authorization'] = `Bearer ${access_token}`;
        originalRequest.headers['Authorization'] = `Bearer ${access_token}`;

        processQueue(null, access_token);
        isRefreshing = false;

        return apiClient(originalRequest);
      } catch (err) {
        processQueue(err);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/auth/login';
        return Promise.reject(handleAPIError(err));
      }
    }

    return Promise.reject(handleAPIError(error));
  }
);

// Auth API
export const authAPI = {
  /**
   * Set authentication token for API calls
   * @param {string} token - JWT token
   */
  setAuthToken: (token) => {
    if (token) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete apiClient.defaults.headers.common['Authorization'];
    }
  },
  
  /**
   * Login user
   * @param {string} usernameOrEmail - Username or email
   * @param {string} password - User password
   * @returns {Promise} - Response with user data and tokens
   */
  login: async (usernameOrEmail, password) => {
    return apiClient.post('/auth/login', {
      username_or_email: usernameOrEmail,
      password,
    });
  },
  
  /**
   * Register new user
   * @param {Object} userData - User registration data
   * @returns {Promise} - Response with user data
   */
  register: async (userData) => {
    return apiClient.post('/auth/register', userData);
  },
  
  /**
   * Logout user
   * @returns {Promise} - Logout response
   */
  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    return response;
  },
  
  /**
   * Reset password request
   * @param {string} email - User email
   * @returns {Promise} - Response data
   */
  requestPasswordReset: async (email) => {
    return apiClient.post('/auth/reset-password', { email });
  },
  
  /**
   * Confirm password reset with token
   * @param {string} token - Reset token
   * @param {string} newPassword - New password
   * @returns {Promise} - Response data
   */
  confirmPasswordReset: async (token, newPassword) => {
    return apiClient.post('/auth/reset-password-confirm', {
      token,
      new_password: newPassword,
    });
  },
  
  /**
   * Get current user info
   * @returns {Promise} - User data
   */
  me: async () => {
    return apiClient.get('/auth/me');
  },
  
  /**
   * Refresh access token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise} - New tokens
   */
  refreshToken: async (refreshToken) => {
    return apiClient.post('/auth/refresh-token', { refresh_token: refreshToken });
  },

  forgotPassword: async (email) => {
    return apiClient.post('/auth/forgot-password', { email });
  },

  verifyEmail: async (token) => {
    return apiClient.post('/auth/verify-email', { token });
  },

  resendVerification: async (email) => {
    return apiClient.post('/auth/resend-verification', { email });
  },

  changePassword: async (oldPassword, newPassword) => {
    return apiClient.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },
};

// User API
export const userAPI = {
  /**
   * Get current user profile.
   * 
   * @returns {Promise<Object>} User data
   */
  getProfile: async () => {
    return apiClient.get('/users/me');
  },
  
  /**
   * Update current user profile.
   * 
   * @param {Object} userData - User update data
   * @returns {Promise<Object>} Updated user data
   */
  updateProfile: async (userData) => {
    return apiClient.put('/users/me', userData);
  },
  
  /**
   * Get all users (admin only).
   * 
   * @param {number} page - Page number
   * @param {number} limit - Items per page
   * @returns {Promise<Array>} List of users
   */
  getUsers: async (page = 1, limit = 10) => {
    const skip = (page - 1) * limit;
    return apiClient.get(`/users?skip=${skip}&limit=${limit}`);
  },
  
  /**
   * Get a specific user by ID (admin only).
   * 
   * @param {number} userId - User ID
   * @returns {Promise<Object>} User data
   */
  getUserById: async (userId) => {
    return apiClient.get(`/users/${userId}`);
  },
  
  /**
   * Create a new user (admin only).
   * 
   * @param {Object} userData - User creation data
   * @returns {Promise<Object>} Created user data
   */
  createUser: async (userData) => {
    return apiClient.post('/users', userData);
  },
  
  /**
   * Update a user by ID (admin only).
   * 
   * @param {number} userId - User ID
   * @param {Object} userData - User update data
   * @returns {Promise<Object>} Updated user data
   */
  updateUser: async (userId, userData) => {
    return apiClient.put(`/users/${userId}`, userData);
  },
  
  /**
   * Delete a user by ID (admin only).
   * 
   * @param {number} userId - User ID
   * @returns {Promise<Object>} Deleted user data
   */
  deleteUser: async (userId) => {
    return apiClient.delete(`/users/${userId}`);
  },
  
  /**
   * Update a user's roles (admin only).
   * 
   * @param {number} userId - User ID
   * @param {Array<string>} roles - List of role names
   * @returns {Promise<Object>} Updated user data
   */
  updateUserRoles: async (userId, roles) => {
    return apiClient.put(`/users/${userId}/roles`, { roles });
  },
  
  /**
   * Update user wallet balance (admin only).
   * 
   * @param {number} userId - User ID
   * @param {number} amount - Amount to add or subtract
   * @param {string} operation - "add" or "subtract"
   * @returns {Promise<Object>} Updated user data
   */
  updateUserWallet: async (userId, amount, operation) => {
    return apiClient.put(`/users/${userId}/wallet`, { 
      amount, 
      operation 
    });
  },
  
  /**
   * Get current user's clients.
   * 
   * @param {number} page - Page number
   * @param {number} limit - Items per page
   * @returns {Promise<Array>} List of user clients
   */
  getMyClients: async (page = 1, limit = 10) => {
    const skip = (page - 1) * limit;
    return apiClient.get(`/users/me/clients?skip=${skip}&limit=${limit}`);
  },

  uploadAvatar: async (file) => {
    const formData = new FormData();
    formData.append('avatar', file);
    return apiClient.post('/users/me/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  deleteAvatar: async () => {
    return apiClient.delete('/users/me/avatar');
  },

  getNotificationSettings: async () => {
    return apiClient.get('/users/me/notifications');
  },

  updateNotificationSettings: async (settings) => {
    return apiClient.put('/users/me/notifications', settings);
  },
};

// Role API
const roleAPI = {
  /**
   * Get all roles.
   * 
   * @returns {Promise<Array>} List of roles
   */
  getRoles: async () => {
    return apiClient.get('/roles');
  },
  
  /**
   * Create a new role (admin only).
   * 
   * @param {Object} roleData - Role creation data
   * @returns {Promise<Object>} Created role data
   */
  createRole: async (roleData) => {
    return apiClient.post('/roles', roleData);
  },
  
  /**
   * Update a role (admin only).
   * 
   * @param {number} roleId - Role ID
   * @param {Object} roleData - Role update data
   * @returns {Promise<Object>} Updated role data
   */
  updateRole: async (roleId, roleData) => {
    return apiClient.put(`/roles/${roleId}`, roleData);
  },
  
  /**
   * Delete a role (admin only).
   * 
   * @param {number} roleId - Role ID
   * @returns {Promise<Object>} Deleted role data
   */
  deleteRole: async (roleId) => {
    return apiClient.delete(`/roles/${roleId}`);
  },
};

// Settings API
const settingsAPI = {
  getSettings: async () => {
    return apiClient.get('/settings');
  },

  updateSettings: async (settings) => {
    return apiClient.put('/settings', settings);
  },

  getTheme: async () => {
    return apiClient.get('/settings/theme');
  },

  updateTheme: async (theme) => {
    return apiClient.put('/settings/theme', { theme });
  },

  getLanguage: async () => {
    return apiClient.get('/settings/language');
  },

  updateLanguage: async (language) => {
    return apiClient.put('/settings/language', { language });
  },
};

// Dashboard API
export const dashboardAPI = {
  /**
   * Get dashboard statistics.
   * 
   * @returns {Promise<Object>} Dashboard statistics
   */
  getStats: async () => {
    return apiClient.get('/dashboard/stats');
  },
  
  /**
   * Get recent activities.
   * 
   * @param {number} limit - Number of activities to fetch
   * @returns {Promise<Array>} List of recent activities
   */
  getRecentActivities: async (limit = 10) => {
    return apiClient.get(`/dashboard/activities?limit=${limit}`);
  },

  getChartData: async (type, period) => {
    return apiClient.get(`/dashboard/charts/${type}`, {
      params: { period },
    });
  },

  getActivities: async (page = 1, limit = 10) => {
    return apiClient.get('/dashboard/activities', {
      params: { page, limit },
    });
  },
};

// Export all API services
export { apiClient, roleAPI, settingsAPI };

// Default export is the raw axios instance
export default apiClient; 