import React, { useEffect, useState } from 'react';
import { apiGet } from '../utils/api';

export default function Dashboard() {
  const [orders, setOrders] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const ordersResponse = await apiGet('/api/orders');
        const ordersData = await ordersResponse.json();

        const inventoryResponse = await apiGet('/api/inventory');
        const inventoryData = await inventoryResponse.json();

        if (!ordersResponse.ok || !inventoryResponse.ok) {
          setMessage('Could not load dashboard data.');
          return;
        }

        setOrders(ordersData || []);
        setInventory(inventoryData || []);
      } catch (error) {
        setMessage('Could not connect to the backend server: ' + error.message);
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  const totalOrders = orders.length;

  const toBePackaged = orders.filter((order) => order.status === 'IN_FULFILLMENT').length;
  const toBeShipped = orders.filter((order) => order.status === 'SHIPPED').length;
  const cancelled = orders.filter((order) => order.status === 'CANCELLED').length;

  const outOfStockItems = inventory.filter((item) => item.quantity_available === 0).length;
  const lowStockItems = inventory.filter(
    (item) => item.quantity_available > 0 && item.quantity_available <= 5
  ).length;



  return (
    <div className="page-container">
      <h1 style={{ marginBottom: '25px', color: '#2c3e50' }}>Dashboard</h1>

      {message && (
        <div className="card" style={{ marginBottom: '20px', color: 'red' }}>
          {message}
        </div>
      )}

      {isLoading ? (
        <div className="card">Loading dashboard data...</div>
      ) : (
        <>
          <div className="card">
            <h2 style={{ marginTop: 0, color: '#0056b3' }}>Order Overview</h2>

            <p style={{ fontSize: '18px' }}>
              <strong>Total number of orders:</strong>{' '}
              <span className="badge" style={{ backgroundColor: '#eef2f6', color: '#0056b3' }}>
                {totalOrders}
              </span>
            </p>

            <div style={{ display: 'flex', gap: '20px', marginTop: '15px', flexWrap: 'wrap' }}>
              <p>
                In Fulfillment:{' '}
                <span className="badge" style={{ backgroundColor: '#fff3cd', color: '#856404' }}>
                  {toBePackaged}
                </span>
              </p>

              <p>
                Shipped:{' '}
                <span className="badge" style={{ backgroundColor: '#d4edda', color: '#155724' }}>
                  {toBeShipped}
                </span>
              </p>

              <p>
                Cancelled:{' '}
                <span className="badge" style={{ backgroundColor: '#f8d7da', color: '#721c24' }}>
                  {cancelled}
                </span>
              </p>
            </div>
          </div>

          <div className="card">
            <h2 style={{ marginTop: 0, color: '#0056b3' }}>Inventory Details</h2>

            

            <p>
              <strong>Out of Stock items:</strong>{' '}
              <span className="badge" style={{ backgroundColor: '#f8d7da', color: '#721c24' }}>
                {outOfStockItems}
              </span>
            </p>

            <p>
              <strong>Low Stock Items:</strong>{' '}
              <span className="badge" style={{ backgroundColor: '#fff3cd', color: '#856404' }}>
                {lowStockItems}
              </span>
            </p>
          </div>
        </>
      )}
    </div>
  );
}
