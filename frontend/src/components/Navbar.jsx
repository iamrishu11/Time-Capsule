/**
 * Navigation Bar Component
 * 
 * Displays navigation links based on authentication state.
 * Shows different options for logged-in vs logged-out users.
 */

import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  /**
   * Handle user logout
   */
  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo / Brand */}
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">⏳</span>
          <span className="brand-text">Time Capsule</span>
        </Link>

        {/* Navigation Links */}
        <div className="navbar-links">
          <Link to="/" className="nav-link">
            Home
          </Link>

          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="nav-link">
                Dashboard
              </Link>
              <Link to="/recipients" className="nav-link">
                Recipients
              </Link>
              <Link to="/capsules/new" className="nav-link nav-link-accent">
                + Create Capsule
              </Link>
              <div className="nav-user">
                <span className="user-name">{user?.name}</span>
                <button 
                  className="btn btn-outline btn-small"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">
                Login
              </Link>
              <Link to="/register" className="btn btn-primary btn-small">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
