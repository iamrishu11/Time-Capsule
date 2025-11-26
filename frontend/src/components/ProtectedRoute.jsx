/**
 * Protected Route Component
 * 
 * Wrapper component that protects routes requiring authentication.
 * Redirects to login page if user is not authenticated.
 */

import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute - Wraps components that require authentication
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Child components to render if authenticated
 * @returns {React.ReactNode} Children if authenticated, redirect to login otherwise
 */
function ProtectedRoute({ children }) {
  const location = useLocation();
  const { isAuthenticated, loading } = useAuth();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    // Save the attempted location for redirect after login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // User is authenticated, render the protected content
  return children;
}

export default ProtectedRoute;
