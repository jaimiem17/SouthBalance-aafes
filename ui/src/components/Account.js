import React from 'react';

export default function Account({ currentUser, onLogout }) {
  return (
    <div className="page-container">
      <h1
        style={{
          marginBottom: '30px',
          color: '#2c3e50',
          textAlign: 'center'
        }}
      >
        My Account
      </h1>

      <div
        className="card"
        style={{
          maxWidth: '650px',
          margin: '0 auto',
          padding: '40px',
          textAlign: 'center'
        }}
      >
        <h2
          style={{
            color: '#0056b3',
            marginTop: 0,
            marginBottom: '35px'
          }}
        >
          Account Details
        </h2>

        <div
          style={{
            background: '#f7f9fc',
            padding: '25px',
            borderRadius: '12px',
            marginBottom: '30px'
          }}
        >
          <div style={{ marginBottom: '20px' }}>
            <div
              style={{
                fontSize: '14px',
                color: '#666',
                marginBottom: '6px'
              }}
            >
              ACCOUNT NAME
            </div>

            <div
              style={{
                fontSize: '28px',
                fontWeight: '600',
                color: '#2c3e50'
              }}
            >
              {currentUser?.username || 'Unknown User'}
            </div>
          </div>

          <div>
            <div
              style={{
                fontSize: '14px',
                color: '#666',
                marginBottom: '6px'
              }}
            >
              ROLE
            </div>

            <div
              style={{
                fontSize: '22px',
                fontWeight: '500',
                color: '#0056b3'
              }}
            >
              {currentUser?.role || 'Unknown Role'}
            </div>
          </div>
        </div>

        <button
          className="primary-button"
          onClick={onLogout}
          style={{
            padding: '14px 40px',
            fontSize: '18px'
          }}
        >
          Logout
        </button>
      </div>
    </div>
  );
}