import React, { useEffect, useState } from 'react';
import Navbar from '../common/NavBar';
import './ReportsPage.css';

const ReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    published: null
  });
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20,
    total: 0
  });
  const [selectedReport, setSelectedReport] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchReports();
    fetchStats();
  }, [pagination.skip, filters]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      let url = `${API_URL}/api/reports?skip=${pagination.skip}&limit=${pagination.limit}`;
      if (filters.published !== null) url += `&published=${filters.published}`;

      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch reports');

      const data = await response.json();
      setReports(data.reports || []);
      setPagination(prev => ({ ...prev, total: data.total }));
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/reports/stats/summary`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const handlePublishReport = async (reportId) => {
    try {
      const response = await fetch(`${API_URL}/api/reports/${reportId}/publish`, {
        method: 'PATCH'
      });
      if (!response.ok) throw new Error('Failed to publish report');

      alert('✓ Report published successfully');
      fetchReports();
      fetchStats();
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (error) {
    return (
      <div className="page">
        <Navbar />
        <main className="reports-content">
          <h1>📊 Incident Reports</h1>
          <div className="error-container">
            <p>Error: {error}</p>
            <button onClick={fetchReports}>Retry</button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="page">
      <Navbar />
      <main className="reports-content">
        <h1>📊 Incident Reports</h1>

        {/* Statistics Cards */}
        {stats && (
          <section className="stats-cards">
            <div className="stat-card">
              <h3>Total Reports</h3>
              <p className="stat-number">{stats.total_reports}</p>
            </div>
            <div className="stat-card">
              <h3>Published</h3>
              <p className="stat-number" style={{ color: '#28a745' }}>
                {stats.published}
              </p>
            </div>
            <div className="stat-card">
              <h3>Unpublished</h3>
              <p className="stat-number" style={{ color: '#ffc107' }}>
                {stats.unpublished}
              </p>
            </div>
            <div className="stat-card">
              <h3>By Severity</h3>
              <div className="severity-breakdown">
                {stats.by_severity.map(item => (
                  <div key={item.severity} style={{ fontSize: '0.85rem' }}>
                    <span style={{ color: getSeverityColor(item.severity) }}>
                      {item.severity}:
                    </span>
                    <strong> {item.count}</strong>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* Filters */}
        <section className="filters">
          <label>
            Status:
            <select
              value={filters.published === null ? '' : filters.published.toString()}
              onChange={(e) => {
                setFilters({
                  published: e.target.value === '' ? null : e.target.value === 'true'
                });
                setPagination({ ...pagination, skip: 0 });
              }}
            >
              <option value="">All</option>
              <option value="true">Published</option>
              <option value="false">Unpublished</option>
            </select>
          </label>
        </section>

        {/* Reports Table */}
        <section className="reports-table">
          {loading ? (
            <p>Loading reports...</p>
          ) : reports.length === 0 ? (
            <p>No reports found. Create an incident to generate reports.</p>
          ) : (
            <>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Incident ID</th>
                    <th>Report ID</th>
                    <th>Severity</th>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Generated</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map((report) => (
                    <tr key={report.id}>
                      <td>#{report.id}</td>
                      <td>#{report.incident_id}</td>
                      <td>{report.report_id}</td>
                      <td>
                        <span
                          style={{
                            backgroundColor: getSeverityColor(report.severity),
                            color: 'white',
                            padding: '4px 8px',
                            borderRadius: '4px'
                          }}
                        >
                          {report.severity}
                        </span>
                      </td>
                      <td>{report.title}</td>
                      <td>
                        {report.is_published ? (
                          <span style={{ color: '#28a745', fontWeight: 'bold' }}>
                            ✅ Published
                          </span>
                        ) : (
                          <span style={{ color: '#ffc107', fontWeight: 'bold' }}>
                            ⏳ Unpublished
                          </span>
                        )}
                      </td>
                      <td>{formatDate(report.generated_at)}</td>
                      <td>
                        <button
                          className="btn-small"
                          onClick={() => setSelectedReport(report)}
                        >
                          👁️ View
                        </button>
                        {!report.is_published && (
                          <button
                            className="btn-small"
                            onClick={() => handlePublishReport(report.id)}
                          >
                            📤 Publish
                          </button>
                        )}
                      </td>
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

        {/* Report Detail Modal */}
        {selectedReport && (
          <div className="modal-overlay" onClick={() => setSelectedReport(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>{selectedReport.title}</h2>
                <button className="close-btn" onClick={() => setSelectedReport(null)}>✕</button>
              </div>
              <div className="modal-body">
                <p><strong>Report ID:</strong> {selectedReport.report_id}</p>
                <p><strong>Incident ID:</strong> {selectedReport.incident_id}</p>
                <p><strong>Severity:</strong>
                  <span style={{
                    backgroundColor: getSeverityColor(selectedReport.severity),
                    color: 'white',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    marginLeft: '0.5rem'
                  }}>
                    {selectedReport.severity}
                  </span>
                </p>
                <p><strong>Generated:</strong> {formatDate(selectedReport.generated_at)}</p>
                <hr />
                <h3>Report Content</h3>
                <pre className="report-content">{selectedReport.content}</pre>
              </div>
              <div className="modal-footer">
                {!selectedReport.is_published && (
                  <button
                    className="btn btn-success"
                    onClick={() => {
                      handlePublishReport(selectedReport.id);
                      setSelectedReport(null);
                    }}
                  >
                    📤 Publish Report
                  </button>
                )}
                <button
                  className="btn btn-secondary"
                  onClick={() => setSelectedReport(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default ReportsPage;
