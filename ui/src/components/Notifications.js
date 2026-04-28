import React, { useEffect, useState } from 'react';
import { apiGet } from '../utils/api';

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadNotifications() {
      try {
        const response = await apiGet('/api/notifications');

        if (!response.ok) {
          const data = await response.json();
          setError(data.detail || 'Could not load notifications.');
          return;
        }

        const data = await response.json();
        setNotifications(data || []);
      } catch (error) {
        setError('Could not connect to the backend server: ' + error.message);
      } finally {
        setLoading(false);
      }
    }

    loadNotifications();
  }, []);

  function getStyle(type) {
    if (type === 'order_confirmation' || type === 'invoice') {
      return {
        background: '#d4edda',
        color: '#155724'
      };
    }

    if (type === 'fulfillment' || type === 'shipping') {
      return {
        background: '#cce5ff',
        color: '#004085'
      };
    }

    return {
      background: '#fff3cd',
      color: '#856404'
    };
  }

  return (
    <div className="page-container">
      <h1
        style={{
          marginBottom: '25px',
          color: '#2c3e50'
        }}
      >
        Notification Logs
      </h1>

      {error && (
        <div className="card" style={{ marginBottom: '20px', color: 'red' }}>
          {error}
        </div>
      )}

      <div className="card">
        {loading ? (
          <p>Loading notifications...</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Order ID</th>
                <th>Recipient Email</th>
                <th>Details</th>
                <th>Timestamp</th>
              </tr>
            </thead>

            <tbody>
              {notifications.length === 0 ? (
                <tr>
                  <td colSpan="5">
                    No notifications found.
                  </td>
                </tr>
              ) : (
                notifications.map((note) => (
                  <tr key={note.notification_id}>
                    <td>
                      <span className="badge" style={getStyle(note.notification_type)}>
                        {note.notification_type}
                      </span>
                    </td>

                    <td>{note.order_id}</td>

                    <td>{note.recipient_email}</td>

                    <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {note.details || 'N/A'}
                    </td>

                    <td>
                      {new Date(note.timestamp).toLocaleString()}
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
