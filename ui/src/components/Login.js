import React, { useState } from 'react';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  async function handleLogin(event) {
    event.preventDefault();

    setErrorMessage('');

    if (!username || !password) {
      setErrorMessage('Please enter both username and password.');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setErrorMessage(data.detail || 'Login failed.');
        return;
      }

      // Store JWT token and user info
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('currentUser', JSON.stringify(data.user));
      onLogin(data.user);
    } catch (error) {
      setErrorMessage('Could not connect to the backend server.');
    } finally {
      setIsLoading(false);
    }
  }

  

  return (
    <div className="login-container">
      <div className="card" style={{ textAlign: 'center', width: '350px' }}>
        <h1 style={{ color: '#0056b3', marginBottom: '5px' }}>South Balance</h1>
        <h3 style={{ color: '#666', marginTop: '0', marginBottom: '30px' }}>
          Order & Inventory
        </h3>

        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '15px' }}>
            <input
              className="input-field"
              type="text"
              placeholder="Username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              style={{ width: '100%', boxSizing: 'border-box', maxWidth: '100%' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <input
              className="input-field"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              style={{ width: '100%', boxSizing: 'border-box', maxWidth: '100%' }}
            />
          </div>

          {errorMessage && (
            <p style={{ color: 'red', marginBottom: '15px' }}>
              {errorMessage}
            </p>
          )}

          <button
            className="primary-button"
            type="submit"
            disabled={isLoading}
            style={{ width: '100%' }}
          >
            {isLoading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}