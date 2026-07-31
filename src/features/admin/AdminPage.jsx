import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../common/NavBar';
import './AdminPage.css';

const AdminPage = () => {
  return (
    <div className="page">
      <Navbar />
      <main className="admin-content">
        <h1>🛡️ Nostromus - Admin Dashboard</h1>

        <section className="dashboard-grid">
          {/* Incidents Card */}
          <div className="dashboard-card">
            <div className="card-header incidents">
              <span className="card-icon">🚨</span>
              <h2>Incidents</h2>
            </div>
            <div className="card-body">
              <p>View and manage security incidents and events</p>
              <ul className="features">
                <li>✅ Real-time incident tracking</li>
                <li>✅ Filter by severity and status</li>
                <li>✅ Create test incidents</li>
                <li>✅ View event details</li>
              </ul>
              <Link to="/incidents" className="btn btn-primary">
                Go to Incidents →
              </Link>
            </div>
          </div>

          {/* Reports Card */}
          <div className="dashboard-card">
            <div className="card-header reports">
              <span className="card-icon">📊</span>
              <h2>Reports</h2>
            </div>
            <div className="card-body">
              <p>View generated AI analysis reports</p>
              <ul className="features">
                <li>✅ AI-generated reports</li>
                <li>✅ Severity analytics</li>
                <li>✅ Publish reports</li>
                <li>✅ View report details</li>
              </ul>
              <Link to="/reports" className="btn btn-primary">
                Go to Reports →
              </Link>
            </div>
          </div>

          {/* System Status Card */}
          <div className="dashboard-card">
            <div className="card-header system">
              <span className="card-icon">⚙️</span>
              <h2>System Status</h2>
            </div>
            <div className="card-body">
              <p>Monitor system health and services</p>
              <ul className="features">
                <li>✅ FastAPI Backend</li>
                <li>✅ PostgreSQL Database</li>
                <li>✅ RabbitMQ Event Bus</li>
                <li>✅ Keycloak Authentication</li>
              </ul>
              <button className="btn btn-secondary" onClick={() => {
                fetch('http://localhost:8000/health')
                  .then(r => r.json())
                  .then(d => alert(`Status: ${JSON.stringify(d.services)}`))
                  .catch(e => alert('Error: ' + e.message));
              }}>
                Check Health →
              </button>
            </div>
          </div>

          {/* Configuration Card */}
          <div className="dashboard-card">
            <div className="card-header config">
              <span className="card-icon">⚡</span>
              <h2>Configuration</h2>
            </div>
            <div className="card-body">
              <p>System configuration and management</p>
              <ul className="features">
                <li>✅ Keycloak Admin Console</li>
                <li>✅ RabbitMQ Management</li>
                <li>✅ Database Management</li>
                <li>✅ API Documentation</li>
              </ul>
              <div className="config-links">
                <a href="http://localhost:8080" target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                  Keycloak
                </a>
                <a href="http://localhost:15672" target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                  RabbitMQ
                </a>
                <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                  API Docs
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Stats Section */}
        <section className="quick-stats">
          <h2>📈 Quick Stats</h2>
          <p style={{ textAlign: 'center', color: '#666' }}>
            Stats will be displayed here. Navigate to Incidents or Reports to see live data.
          </p>
        </section>
      </main>
    </div>
  );
};

export default AdminPage;