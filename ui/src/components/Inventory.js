import React, { useEffect, useState } from 'react';
import { apiGet, apiPatch } from '../utils/api';

export default function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [adjustments, setAdjustments] = useState({});
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  async function loadInventory() {
    try {
      // Fetch inventory, products, and colors to enrich the data
      const [inventoryRes, productsRes, colorsRes] = await Promise.all([
        apiGet('/api/inventory'),
        apiGet('/api/products'),
        apiGet('/api/colors'),
      ]);

      const inventoryData = await inventoryRes.json();
      const productsData = await productsRes.json();
      const colorsData = await colorsRes.json();

      // Enrich inventory with product and color names
      const enrichedInventory = inventoryData.map(inv => {
        const product = productsData.find(p => p.product_id === inv.product_id);
        const color = colorsData.find(c => c.color_id === inv.color_id);
        return {
          ...inv,
          product_name: product?.product_name || 'Unknown',
          base_cost: product?.base_cost || 0,
          color_name: color?.color_name || 'Unknown',
        };
      });

      setInventory(enrichedInventory);
    } catch (error) {
      setMessage('Could not load inventory: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadInventory();
  }, []);

  function updateAdjustment(stockId, value) {
    setAdjustments({
      ...adjustments,
      [stockId]: Number(value),
    });
  }

  async function adjustInventory(stockId, direction) {
    setMessage('');

    const amount = adjustments[stockId];

    if (!amount || amount <= 0) {
      setMessage('Please enter a positive quantity to adjust.');
      return;
    }

    const quantityChange = direction === 'add' ? amount : -amount;

    try {
      const response = await apiPatch(`/api/inventory/${stockId}/adjust`, {
        quantity_change: quantityChange,
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.detail || 'Inventory could not be updated.');
        return;
      }

      setMessage('Inventory updated successfully.');
      setAdjustments({
        ...adjustments,
        [stockId]: '',
      });

      loadInventory();
    } catch (error) {
      setMessage('Could not connect to the backend server: ' + error.message);
    }
  }

  return (
    <div className="page-container">
      <h1 style={{ marginBottom: '25px', color: '#2c3e50' }}>Inventory Management</h1>

      {message && (
        <div
          className="card"
          style={{
            marginBottom: '20px',
            color: message.includes('successfully') ? 'green' : 'red',
          }}
        >
          {message}
        </div>
      )}

      <div className="card">
        {isLoading ? (
          <p>Loading inventory...</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>StockID</th>
                <th>Product Name</th>
                <th>Color</th>
                <th>Cost</th>
                <th>Current Quantity</th>
                <th>Adjust By</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {inventory.length === 0 ? (
                <tr>
                  <td colSpan="7">No inventory found.</td>
                </tr>
              ) : (
                inventory.map((item) => (
                  <tr key={item.stock_id}>
                    <td>{item.stock_id}</td>
                    <td>{item.product_name}</td>
                    <td>{item.color_name}</td>
                    <td>${Number(item.base_cost).toFixed(2)}</td>
                    <td>{item.quantity_available}</td>
                    <td>
                      <input
                        className="input-field"
                        type="number"
                        min="1"
                        value={adjustments[item.stock_id] || ''}
                        onChange={(event) => updateAdjustment(item.stock_id, event.target.value)}
                        style={{ width: '80px' }}
                      />
                    </td>
                    <td>
                      <button
                        className="primary-button"
                        onClick={() => adjustInventory(item.stock_id, 'add')}
                        style={{ marginRight: '8px' }}
                      >
                        Add
                      </button>

                      <button
                        className="secondary-button"
                        onClick={() => adjustInventory(item.stock_id, 'remove')}
                      >
                        Remove
                      </button>
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
