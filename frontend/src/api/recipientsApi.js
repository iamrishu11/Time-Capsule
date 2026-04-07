/**
 * Recipients API Functions
 * 
 * Provides functions for managing recipients (people who receive capsules).
 */

import apiClient from './apiClient';

/**
 * Get all recipients for the current user
 * 
 * @returns {Promise<Array>} List of recipients
 */
export const getRecipients = async () => {
  const response = await apiClient.get('/api/recipients');
  return response.data;
};

/**
 * Get a single recipient by ID
 * 
 * @param {number} id - Recipient ID
 * @returns {Promise<Object>} Recipient data
 */
export const getRecipientById = async (id) => {
  const response = await apiClient.get(`/api/recipients/${id}`);
  return response.data;
};

/**
 * Create a new recipient
 * 
 * @param {Object} data - Recipient data
 * @param {string} data.name - Recipient's name
 * @param {string} data.email - Recipient's email
 * @param {string} [data.relation] - Relationship (e.g., "daughter", "friend")
 * @returns {Promise<Object>} Created recipient
 */
export const createRecipient = async (data) => {
  const response = await apiClient.post('/api/recipients', data);
  return response.data;
};

/**
 * Update a recipient
 * 
 * @param {number} id - Recipient ID
 * @param {Object} data - Updated recipient data
 * @returns {Promise<Object>} Updated recipient
 */
export const updateRecipient = async (id, data) => {
  const response = await apiClient.put(`/api/recipients/${id}`, data);
  return response.data;
};

/**
 * Delete a recipient
 * 
 * @param {number} id - Recipient ID
 * @returns {Promise<Object>} Deletion confirmation
 */
export const deleteRecipient = async (id) => {
  const response = await apiClient.delete(`/api/recipients/${id}`);
  return response.data;
};

export default {
  getRecipients,
  getRecipientById,
  createRecipient,
  updateRecipient,
  deleteRecipient,
};
