import React, { useEffect, useState } from 'react';
import { apiGet } from '../utils/api';

export default function Invoices() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [invoiceHtml, setInvoiceHtml] = useState('');

  useEffect(() => {
    async function loadOrders() {
      try {
        const response = await apiGet('/api/orders');

        if (!response.ok) {
          const data = await response.json();
          setError(data.detail || 'Could not load orders.');
          return;
        }

        const data = await response.json();
        setOrders(data || []);
      } catch (error) {
        setError('Could not connect to the backend server: ' + error.message);
      } finally {
        setLoading(false);
      }
    }

    loadOrders();
  }, []);

  async function viewInvoice(orderId) {
    try {
      const response = await apiGet(`/api/orders/${orderId}/invoice`);

      if (!response.ok) {
        const data = await response.json();
        setError(data.detail || 'Could not load invoice.');
        return;
      }

      const html = await response.text();
      setInvoiceHtml(html);
      setSelectedInvoice(orderId);
    } catch (error) {
      setError('Could not load invoice: ' + error.message);
    }
  }

  function closeInvoice() {
    setSelectedInvoice(null);
    setInvoiceHtml('');
  }

  function printInvoice() {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(invoiceHtml);
    printWindow.document.close();
    printWindow.print();
  }

  return (
    <div className="page-container">
      <h1
        style={{
          marginBottom: '25px',
          color: '#2c3e50'
        }}
      >
        Invoices
      </h1>

      {error && (
        <div className="card" style={{ marginBottom: '20px', color: 'red' }}>
          {error}
        </div>
      )}

      <div className="card">
        {loading ? (
          <p>Loading orders...</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Date</th>
                <th>Contact Email</th>
                <th>Status</th>
                <th>Total Cost</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {orders.length === 0 ? (
                <tr>
                  <td colSpan="6">
                    No orders found.
                  </td>
                </tr>
              ) : (
                orders.map((order) => (
                  <tr key={order.order_id}>
                    <td>{order.order_id}</td>

                    <td>
                      {new Date(order.order_date).toLocaleDateString()}
                    </td>

                    <td>{order.contact_email}</td>

                    <td>
                      <span className="badge" style={{
                        backgroundColor: 
                          order.status === 'IN_FULFILLMENT' ? '#fff3cd' :
                          order.status === 'SHIPPED' ? '#d4edda' :
                          order.status === 'CANCELLED' ? '#f8d7da' : '#eef2f6',
                        color:
                          order.status === 'IN_FULFILLMENT' ? '#856404' :
                          order.status === 'SHIPPED' ? '#155724' :
                          order.status === 'CANCELLED' ? '#721c24' : '#0056b3'
                      }}>
                        {order.status}
                      </span>
                    </td>

                    <td>${Number(order.total_cost).toFixed(2)}</td>

                    <td>
                      <button
                        className="primary-button"
                        onClick={() => viewInvoice(order.order_id)}
                        style={{ fontSize: '14px', padding: '6px 12px' }}
                      >
                        View Invoice
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Invoice Modal */}
      {selectedInvoice && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            maxWidth: '90%',
            maxHeight: '90%',
            overflow: 'auto',
            position: 'relative'
          }}>
            <div style={{ marginBottom: '15px', display: 'flex', gap: '10px' }}>
              <button className="primary-button" onClick={printInvoice}>
                Print Invoice
              </button>
              <button className="secondary-button" onClick={closeInvoice}>
                Close
              </button>
            </div>
            <div dangerouslySetInnerHTML={{ __html: invoiceHtml }} />
          </div>
        </div>
      )}
    </div>
  );
}
