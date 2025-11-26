/**
 * Dashboard Page Component
 * 
 * Protected page showing user's dashboard after authentication.
 * Displays user's capsules, recipients count, and quick actions.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getCapsules } from '../api/capsulesApi';
import { getRecipients } from '../api/recipientsApi';
import './Dashboard.css';

function Dashboard() {
  const { user } = useAuth();
  const [capsules, setCapsules] = useState([]);
  const [recipients, setRecipients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const [capsulesData, recipientsData] = await Promise.all([
        getCapsules(),
        getRecipients(),
      ]);
      setCapsules(capsulesData);
      setRecipients(recipientsData);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'PENDING':
        return 'badge-warning';
      case 'RELEASED':
        return 'badge-success';
      case 'DELIVERED':
        return 'badge-info';
      case 'CANCELLED':
        return 'badge-error';
      default:
        return '';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  // Calculate stats
  const stats = {
    total: capsules.length,
    pending: capsules.filter((c) => c.status === 'PENDING').length,
    delivered: capsules.filter((c) => c.status === 'DELIVERED').length,
    recipients: recipients.length,
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">
        <header className="dashboard-header">
          <div className="header-left">
            <h1>Welcome, {user?.name || 'User'}!</h1>
            <p className="subtitle">
              Your personal Time Capsule dashboard
            </p>
          </div>
          <div className="header-actions">
            <Link to="/capsules/new" className="btn btn-primary">
              + Create Capsule
            </Link>
          </div>
        </header>

        {error && <div className="alert alert-error">{error}</div>}

        <section className="dashboard-content">
          {/* Stats Grid */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{stats.total}</div>
              <div className="stat-label">Total Capsules</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.pending}</div>
              <div className="stat-label">Pending Delivery</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.delivered}</div>
              <div className="stat-label">Delivered</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.recipients}</div>
              <div className="stat-label">Recipients</div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="quick-actions">
            <h2>Quick Actions</h2>
            <div className="actions-grid">
              <Link to="/capsules/new" className="action-card">
                <span className="action-icon">📝</span>
                <span className="action-text">Create Capsule</span>
              </Link>
              <Link to="/recipients" className="action-card">
                <span className="action-icon">👥</span>
                <span className="action-text">Manage Recipients</span>
              </Link>
            </div>
          </div>

          {/* Capsules List */}
          <div className="capsules-section">
            <div className="section-header">
              <h2>Your Time Capsules</h2>
              <Link to="/capsules/new" className="btn btn-secondary btn-small">
                + New
              </Link>
            </div>

            {loading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p>Loading capsules...</p>
              </div>
            ) : capsules.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📭</div>
                <h3>No Time Capsules Yet</h3>
                <p>Create your first time capsule to preserve memories for your loved ones.</p>
                <Link to="/capsules/new" className="btn btn-primary">
                  Create Your First Capsule
                </Link>
              </div>
            ) : (
              <div className="capsules-list">
                {capsules.map((capsule) => (
                  <Link
                    key={capsule.id}
                    to={`/capsules/${capsule.id}`}
                    className="capsule-card"
                  >
                    <div className="capsule-card-header">
                      <h3 className="capsule-title">{capsule.title}</h3>
                      <span className={`badge ${getStatusBadgeClass(capsule.status)}`}>
                        {capsule.status}
                      </span>
                    </div>
                    <div className="capsule-card-body">
                      <div className="capsule-meta">
                        <span className="meta-item">
                          <span className="meta-icon">📅</span>
                          Release: {formatDate(capsule.release_at)}
                        </span>
                        <span className="meta-item">
                          <span className="meta-icon">👥</span>
                          {capsule.recipients?.length || 0} Recipients
                        </span>
                      </div>
                    </div>
                    <div className="capsule-card-footer">
                      <span className="created-date">
                        Created {formatDate(capsule.created_at)}
                      </span>
                      <span className="view-link">View →</span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* User Info Card */}
          <div className="user-info-card">
            <h3>Account Information</h3>
            <div className="info-row">
              <span className="label">Name:</span>
              <span className="value">{user?.name}</span>
            </div>
            <div className="info-row">
              <span className="label">Email:</span>
              <span className="value">{user?.email}</span>
            </div>
            <div className="info-row">
              <span className="label">Account Type:</span>
              <span className="value">{user?.role || 'User'}</span>
            </div>
            <div className="info-row">
              <span className="label">Member Since:</span>
              <span className="value">
                {user?.created_at 
                  ? new Date(user.created_at).toLocaleDateString()
                  : 'N/A'
                }
              </span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
