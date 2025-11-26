/**
 * Authentication Context
 * 
 * Provides global authentication state and functions throughout the app.
 * Handles token storage, user session restoration, and auth state management.
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getCurrentUser } from '../api/authApi';

// Create the authentication context
const AuthContext = createContext(null);

/**
 * Authentication Provider Component
 * 
 * Wraps the application and provides auth state and functions to all children.
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Check if user is authenticated
   */
  const isAuthenticated = !!user && !!token;

  /**
   * Login function - stores token and user data
   * 
   * @param {Object} userData - User information from server
   * @param {string} accessToken - JWT access token
   */
  const login = useCallback((userData, accessToken) => {
    localStorage.setItem('token', accessToken);
    setToken(accessToken);
    setUser(userData);
    setError(null);
  }, []);

  /**
   * Logout function - clears token and user data
   */
  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setError(null);
  }, []);

  /**
   * Restore user session on app load
   * Attempts to fetch current user if token exists
   */
  const restoreSession = useCallback(async () => {
    const storedToken = localStorage.getItem('token');
    
    if (!storedToken) {
      setLoading(false);
      return;
    }

    try {
      const response = await getCurrentUser();
      setUser(response.user);
      setError(null);
    } catch (err) {
      // Token is invalid or expired
      console.error('Session restoration failed:', err);
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      
      // Only set error if it's not a 401 (expected for expired tokens)
      if (err.response?.status !== 401) {
        setError('Failed to restore session');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Restore session on component mount
   */
  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  // Context value to provide to consumers
  const value = {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    restoreSession,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Custom hook to access authentication context
 * 
 * @returns {Object} Auth context with user, token, and auth functions
 * @throws {Error} If used outside of AuthProvider
 */
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

export default AuthContext;
