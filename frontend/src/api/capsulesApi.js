/**
 * Capsules API Functions
 * 
 * Provides functions for managing time capsules including
 * creation, retrieval, updates, and file attachments.
 */

import apiClient from './apiClient';

/**
 * Create a new time capsule
 * 
 * @param {Object} data - Capsule data
 * @param {string} data.title - Capsule title
 * @param {string} data.message - Message content (will be encrypted server-side)
 * @param {Array<number>} data.recipient_ids - Array of recipient IDs
 * @param {string} data.release_type - "TIME" or "EVENT"
 * @param {string} [data.release_at] - ISO datetime for TIME-based release
 * @param {boolean} [data.requires_guardian] - Whether guardian confirmation is needed
 * @returns {Promise<Object>} Created capsule
 */
export const createCapsule = async (data) => {
  const response = await apiClient.post('/api/capsules', data);
  return response.data;
};

/**
 * Get all capsules for the current user (summary view)
 * 
 * @returns {Promise<Array>} List of capsules with recipients
 */
export const getCapsules = async () => {
  const response = await apiClient.get('/api/capsules');
  return response.data;
};

/**
 * Get a single capsule by ID with decrypted message
 * 
 * @param {number} id - Capsule ID
 * @returns {Promise<Object>} Capsule with decrypted message, recipients, and attachments
 */
export const getCapsuleById = async (id) => {
  const response = await apiClient.get(`/api/capsules/${id}`);
  return response.data;
};

/**
 * Update a capsule
 * 
 * @param {number} id - Capsule ID
 * @param {Object} data - Updated capsule data
 * @returns {Promise<Object>} Updated capsule
 */
export const updateCapsule = async (id, data) => {
  const response = await apiClient.put(`/api/capsules/${id}`, data);
  return response.data;
};

/**
 * Delete (cancel) a capsule
 * 
 * @param {number} id - Capsule ID
 * @returns {Promise<Object>} Deletion confirmation
 */
export const deleteCapsule = async (id) => {
  const response = await apiClient.delete(`/api/capsules/${id}`);
  return response.data;
};

/**
 * Upload a file attachment to a capsule
 * 
 * @param {number} capsuleId - Capsule ID
 * @param {File} file - File object to upload
 * @returns {Promise<Object>} Uploaded attachment metadata
 */
export const uploadAttachment = async (capsuleId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post(
    `/api/capsules/${capsuleId}/attachments`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

/**
 * Get all attachments for a capsule
 * 
 * @param {number} capsuleId - Capsule ID
 * @returns {Promise<Array>} List of attachments
 */
export const getAttachments = async (capsuleId) => {
  const response = await apiClient.get(`/api/capsules/${capsuleId}/attachments`);
  return response.data;
};

/**
 * Delete an attachment from a capsule
 * 
 * @param {number} capsuleId - Capsule ID
 * @param {number} attachmentId - Attachment ID
 * @returns {Promise<Object>} Deletion confirmation
 */
export const deleteAttachment = async (capsuleId, attachmentId) => {
  const response = await apiClient.delete(
    `/api/capsules/${capsuleId}/attachments/${attachmentId}`
  );
  return response.data;
};

export default {
  createCapsule,
  getCapsules,
  getCapsuleById,
  updateCapsule,
  deleteCapsule,
  uploadAttachment,
  getAttachments,
  deleteAttachment,
};
