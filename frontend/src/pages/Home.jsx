/**
 * Home Page Component
 * 
 * Landing page for the Time Capsule application.
 * Displays project description and links to login/register.
 */

import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Home.css';

function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="home-page">
      <div className="hero-section">
        <h1 className="hero-title">
          Time Capsule for Digital Legacy
        </h1>
        
        <p className="hero-description">
          Create meaningful time capsules — messages, letters, photos, and memories — 
          that will be delivered to your loved ones at a future date or when certain 
          life events occur. Preserve your digital legacy and ensure your words reach 
          the people who matter most.
        </p>

        <div className="hero-features">
          <div className="feature">
            <span className="feature-icon">📝</span>
            <h3>Create Capsules</h3>
            <p>Write heartfelt messages and letters for your loved ones</p>
          </div>
          
          <div className="feature">
            <span className="feature-icon">📅</span>
            <h3>Schedule Delivery</h3>
            <p>Set specific dates or event-based triggers for delivery</p>
          </div>
          
          <div className="feature">
            <span className="feature-icon">🔒</span>
            <h3>Secure & Private</h3>
            <p>Your messages are encrypted and protected</p>
          </div>
        </div>

        <div className="hero-cta">
          {isAuthenticated ? (
            <Link to="/dashboard" className="btn btn-primary">
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link to="/register" className="btn btn-primary">
                Get Started
              </Link>
              <Link to="/login" className="btn btn-secondary">
                Sign In
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Home;
