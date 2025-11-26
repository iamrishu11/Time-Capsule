/**
 * Authentication API Functions
 * 
 * Provides functions for user registration, login, and session management.
 */

import apiClient from './apiClient';

/**
 * Register a new user account
 * 
 * @param {Object} data - Registration data
 * @param {string} data.name - User's full name
 * @param {string} data.email - User's email address
 * @param {string} data.password - User's password
 * @returns {Promise<Object>} Response with access_token and user data
 */
export const register = async (data) => {
  const response = await apiClient.post('/api/auth/register', data);
  return response.data;
};

/**
 * Login with email and password
 * 
 * @param {Object} data - Login credentials
 * @param {string} data.email - User's email address
 * @param {string} data.password - User's password
 * @returns {Promise<Object>} Response with access_token and user data
 */
export const login = async (data) => {
  const response = await apiClient.post('/api/auth/login', data);
  return response.data;
};

/**
 * Get current authenticated user's information
 * Requires valid JWT token in localStorage
 * 
 * @returns {Promise<Object>} Current user data
 */
export const getCurrentUser = async () => {
  const response = await apiClient.get('/api/auth/me');
  return response.data;
};

/**
 * Refresh the JWT access token
 * Requires valid JWT token in localStorage
 * 
 * @returns {Promise<Object>} Response with new access_token
 */
export const refreshToken = async () => {
  const response = await apiClient.post('/api/auth/refresh');
  return response.data;
};

/**
 * Test health check endpoint
 * Used to verify API connectivity
 * 
 * @returns {Promise<Object>} Health status
 */
export const healthCheck = async () => {
  const response = await apiClient.get('/api/health');
  return response.data;
};

export default {
  register,
  login,
  getCurrentUser,
  refreshToken,
  healthCheck,
};
