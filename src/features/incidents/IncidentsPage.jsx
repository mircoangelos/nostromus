import React, { useEffect, useState } from 'react';
import Navbar from '../common/NavBar';
import './IncidentsPage.css';

const IncidentsPage = () => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    severity: ''
  });
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20,
    total: 0
  });

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchIncidents();
  }, [pagination.skip, filters]);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      let url = `${API_URL}/api/incidents?skip=${pagination.skip}&limit=${pagination.limit}`;
      if (filters.status) url += `&status_filter=${filters.status}`;
      if (filters.severity) url += `&severity_filter=${filters.severity}`;

      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch incidents');

      const data = await response.json();
      setIncidents(data.incidents || []);
      setPagination(prev => ({ ...prev, total: data.total }));
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTestIncident = async (type) => {
    try {
      const endpoint = type === 'brute-force'
        ? '/api/incidents/test/brute-force'
        : '/api/incidents/test/slow-query';

      const response = await fetch(`${API_URL}${endpoint}`);
      if (!response.ok) throw new Error('Failed to create incident');

      alert(`✓ Test incident created: ${type}`);
      fetchIncidents();
    } catch (err) {
      alert(`✗ Error: ${err.message}`);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: '#dc3545',
      HIGH: '#fd7e14',
      MEDIUM: '#ffc107',
      LOW: '#28a745'
    };
    return colors[severity] || '#6c757d';
  };

  const getStatusBadge = (status) => {
    const badges = {
      OPEN: { color: '#dc3545', label: '🔴 Open' },
      IN_PROGRESS: { color: '#0dcaf0', label: '🔵 In Progress' },
      RESOLVED: { color: '#198754', label: '✅ Resolved' },
      CLOSED: { color: '#6c757d', label: '⚫ Closed' }
    };
    return badges[status] || { color: '#6c757d', label: status };
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (error) {
    return (
      <div className="page">
        <Navbar />
        <main className="incidents-content">
          <h1>🛡️ Security Incidents</h1>
          <div className="error-container">
            <p>Error: {error}</p>
            <button onClick={fetchIncidents}>Retry</button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="page">
      <Navbar />
      <main className="incidents-content">
        <h1>🛡️ Security Incidents</h1>

        {/* Test Actions */}
        <section className="test-actions">
          <h3>Quick Test</h3>
          <button
            className="btn btn-warning"
            onClick={() => handleCreateTestIncident('brute-force')}
          >
            🔴 Create Brute Force Test
          </button>
          <button
            className="btn btn-info"
            onClick={() => handleCreateTestIncident('slow-query')}
          >
            ⚡ Create Slow Query Test
          </button>
        </section>

        {/* Filters */}
        <section className="filters">
          <label>
            Status:
            <select
              value={filters.status}
              onChange={(e) => {
                setFilters({ ...filters, status: e.target.value });
                setPagination({ ...pagination, skip: 0 });
              }}
            >
              <option value="">All</option>
              <option value="OPEN">Open</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="RESOLVED">Resolved</option>
              <option value="CLOSED">Closed</option>
            </select>
          </label>

          <label>
            Severity:
            <select
              value={filters.severity}
              onChange={(e) => {
                setFilters({ ...filters, severity: e.target.value });
                setPagination({ ...pagination, skip: 0 });
              }}
            >
              <option value="">All</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </label>
        </section>

        {/* Incidents Table */}
        <section className="incidents-table">
          {loading ? (
            <p>Loading incidents...</p>
          ) : incidents.length === 0 ? (
            <p>No incidents found</p>
          ) : (
            <>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>User</th>
                    <th>IP Address</th>
                    <th>Description</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.map((incident) => (
                    <tr key={incident.id}>
                      <td>#{incident.id}</td>
                      <td>{incident.event_type}</td>
                      <td>
                        <span
                          style={{
                            backgroundColor: getSeverityColor(incident.severity),
                            color: 'white',
                            padding: '4px 8px',
                            borderRadius: '4px'
                          }}
                        >
                          {incident.severity}
                        </span>
                      </td>
                      <td>
                        <span style={{ color: getStatusBadge(incident.status).color }}>
                          {getStatusBadge(incident.status).label}
                        </span>
                      </td>
                      <td>{incident.user_id}</td>
                      <td>{incident.ip_address || '-'}</td>
                      <td>{incident.description}</td>
                      <td>{formatDate(incident.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Pagination */}
              <div className="pagination">
                <button
                  onClick={() => setPagination({ ...pagination, skip: Math.max(0, pagination.skip - pagination.limit) })}
                  disabled={pagination.skip === 0}
                >
                  ← Previous
                </button>
                <span>
                  Showing {pagination.skip + 1} - {Math.min(pagination.skip + pagination.limit, pagination.total)} of {pagination.total}
                </span>
                <button
                  onClick={() => setPagination({ ...pagination, skip: pagination.skip + pagination.limit })}
                  disabled={pagination.skip + pagination.limit >= pagination.total}
                >
                  Next →
                </button>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
};

export default IncidentsPage;
