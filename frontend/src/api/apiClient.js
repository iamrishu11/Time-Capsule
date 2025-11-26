/**
 * Axios API Client
 * 
 * Configured Axios instance for making API requests to the Flask backend.
 * Automatically attaches JWT token to requests when available.
 */

import axios from 'axios';

// Get base URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create Axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle specific error cases
    if (error.response) {
      const { status } = error.response;
      
      // Token expired or invalid - clear auth state
      if (status === 401) {
        localStorage.removeItem('token');
        // Optionally redirect to login
        // window.location.href = '/login';
      }
      
      // Server error
      if (status >= 500) {
        console.error('Server error:', error.response.data);
      }
    } else if (error.request) {
      // Network error - no response received
      console.error('Network error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
