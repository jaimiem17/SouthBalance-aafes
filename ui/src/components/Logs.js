import React, { useEffect, useState } from 'react';
import { apiGet } from '../utils/api';

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadLogs() {
      try {
        const response = await apiGet('/api/audit-logs');

        if (!response.ok) {
          const data = await response.json();
          setError(data.detail || 'Could not load audit logs.');
          return;
        }

        const data = await response.json();
        setLogs(data || []);
      } catch (error) {
        setError('Could not connect to the backend server: ' + error.message);
      } finally {
        setLoading(false);
      }
    }

    loadLogs();
  }, []);

  return (
    <div className="page-container">
      <h1
        style={{
          marginBottom:'25px',
          color:'#2c3e50'
        }}
      >
        Audit Logs
      </h1>

      {error && (
        <div className="card" style={{ marginBottom: '20px', color: 'red' }}>
          {error}
        </div>
      )}

      <div className="card">
        {loading ? (
          <p>Loading audit logs...</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Event Type</th>
                <th>Account ID</th>
                <th>Details</th>
                <th>IP Address</th>
                <th>Timestamp</th>
              </tr>
            </thead>

            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan="5">
                    No audit logs found.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.log_id}>
                    <td>
                      <span className="badge" style={{
                        backgroundColor: 
                          log.event_type === 'login_failed' ? '#f8d7da' :
                          log.event_type === 'login' ? '#d4edda' :
                          '#eef2f6',
                        color:
                          log.event_type === 'login_failed' ? '#721c24' :
                          log.event_type === 'login' ? '#155724' :
                          '#0056b3'
                      }}>
                        {log.event_type}
                      </span>
                    </td>

                    <td>{log.account_id || 'N/A'}</td>

                    <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {log.details || 'N/A'}
                    </td>

                    <td>{log.ip_address || 'N/A'}</td>

                    <td>
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>

          </table>
        )}
      </div>
    </div>
  );
}
