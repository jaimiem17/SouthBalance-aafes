import React, { useEffect, useState } from 'react';
import './App.css';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Inventory from './components/Inventory';
import Orders from './components/Orders';
import ViewOrders from './components/ViewOrders';
import Notifications from './components/Notifications';
import Invoices from './components/Invoices';
import Logs from './components/Logs';
import Account from './components/Account';

function App() {
  const [currentPage, setCurrentPage] = useState('login');
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');

    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
      setCurrentPage('dashboard');
    }
  }, []);

  function handleLogin(user) {
    setCurrentUser(user);
    localStorage.setItem('currentUser', JSON.stringify(user));
    setCurrentPage('dashboard');
  }

  function handleLogout() {
    localStorage.removeItem('currentUser');
    setCurrentUser(null);
    setCurrentPage('login');
  }

  let PageToDisplay;

  if (!currentUser) {
    PageToDisplay = <Login onLogin={handleLogin} />;
  } else if (currentPage === 'dashboard') {
    PageToDisplay = <Dashboard navigateTo={setCurrentPage} currentUser={currentUser} />;
  } else if (currentPage === 'inventory') {
    PageToDisplay = <Inventory navigateTo={setCurrentPage} currentUser={currentUser} />;
  } else if (currentPage === 'orders') {
    PageToDisplay = <Orders navigateTo={setCurrentPage} currentUser={currentUser} />;
  } else if (currentPage === 'view-orders') {
    PageToDisplay = <ViewOrders navigateTo={setCurrentPage} currentUser={currentUser} />;
  } else if (currentPage === 'notifications') {
    PageToDisplay = <Notifications navigateTo={setCurrentPage} currentUser={currentUser} />;
  } else if (currentPage === 'invoices') {
    PageToDisplay = <Invoices navigateTo={setCurrentPage} currentUser={currentUser} />;
  } else if (currentPage === 'logs') {
    PageToDisplay = <Logs navigateTo={setCurrentPage} currentUser={currentUser} />;
  } else if (currentPage === 'account') {
    PageToDisplay = (
      <Account
        navigateTo={setCurrentPage}
        currentUser={currentUser}
        onLogout={handleLogout}
      />
    );
  } else {
    PageToDisplay = <Dashboard navigateTo={setCurrentPage} currentUser={currentUser} />;
  }

  return (
    <div>
      {currentUser && (
        <div className="navbar">
          <button className="nav-button" onClick={() => setCurrentPage('dashboard')}>Dashboard</button>
          <button className="nav-button" onClick={() => setCurrentPage('orders')}>Orders</button>
          <button className="nav-button" onClick={() => setCurrentPage('inventory')}>Inventory</button>
          <button className="nav-button" onClick={() => setCurrentPage('notifications')}>Notifications</button>
          <button className="nav-button" onClick={() => setCurrentPage('invoices')}>Invoices</button>
          <button className="nav-button" onClick={() => setCurrentPage('logs')}>View Logs</button>
          <button className="nav-button" onClick={() => setCurrentPage('account')}>Account</button>
          <button className="nav-button" onClick={handleLogout}>Logout</button>
        </div>
      )}

      {PageToDisplay}
    </div>
  );
}

export default App;