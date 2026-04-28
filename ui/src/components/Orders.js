import React, { useEffect, useState } from 'react';
import { apiGet, apiPost } from '../utils/api';

export default function Orders({ navigateTo, currentUser }) {
  const [inventory, setInventory] = useState([]);
  const [distributionCenters, setDistributionCenters] = useState([]);
  const [customOptions, setCustomOptions] = useState([]);
  const [quantities, setQuantities] = useState({});
  const [customSelections, setCustomSelections] = useState({});
  const [selectedDcId, setSelectedDcId] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadOrderData() {
      try {
        // Fetch inventory, distribution centers, and custom options
        const [inventoryRes, dcsRes, customRes, productsRes, colorsRes] = await Promise.all([
          apiGet('/api/inventory'),
          apiGet('/api/distribution-centers'),
          apiGet('/api/custom-options'),
          apiGet('/api/products?active=true'),
          apiGet('/api/colors'),
        ]);

        const inventoryData = await inventoryRes.json();
        const dcsData = await dcsRes.json();
        const customData = await customRes.json();
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
        setDistributionCenters(dcsData);
        setCustomOptions(customData);

        if (dcsData && dcsData.length > 0) {
          setSelectedDcId(dcsData[0].dc_id);
        }
      } catch (error) {
        setMessage('Could not load order data: ' + error.message);
      } finally {
        setIsLoading(false);
      }
    }

    loadOrderData();
  }, []);

  function updateQuantity(stockId, value) {
    setQuantities({
      ...quantities,
      [stockId]: Number(value),
    });
  }

  function updateCustomSelection(stockId, value) {
    setCustomSelections({
      ...customSelections,
      [stockId]: value,
    });
  }

  function getSelectedItems() {
    return inventory
      .filter((item) => quantities[item.stock_id] > 0)
      .map((item) => ({
        stock_id: item.stock_id,
        custom_id: customSelections[item.stock_id] || null,
        quantity_ordered: quantities[item.stock_id],
      }));
  }

  function getCustomCharge(stockId) {
    const customId = customSelections[stockId];

    if (!customId) {
      return 0;
    }

    const option = customOptions.find((custom) => custom.custom_id === customId);
    return option ? Number(option.added_charge) : 0;
  }

  function calculateTotal() {
    return inventory.reduce((total, item) => {
      const quantity = quantities[item.stock_id] || 0;
      const price = Number(item.base_cost) + getCustomCharge(item.stock_id);
      return total + quantity * price;
    }, 0);
  }

  async function submitOrder() {
    setMessage('');

    const selectedItems = getSelectedItems();

    if (!selectedDcId) {
      setMessage('Please select a distribution center.');
      return;
    }

    if (!contactEmail) {
      setMessage('Please enter a contact email.');
      return;
    }

    if (selectedItems.length === 0) {
      setMessage('Please enter a quantity for at least one product.');
      return;
    }

    try {
      const response = await apiPost('/api/orders/create', {
        dc_id: selectedDcId,
        contact_email: contactEmail,
        items: selectedItems,
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.detail || 'Order could not be submitted.');
        return;
      }

      setMessage(`Order submitted successfully. Total: $${Number(data.total_cost).toFixed(2)}`);
      setQuantities({});
      setCustomSelections({});
      setContactEmail('');
    } catch (error) {
      setMessage('Could not connect to the backend server: ' + error.message);
    }
  }

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px' }}>
        <h1 style={{ color: '#2c3e50', margin: 0 }}>Place Order</h1>
        <button className="primary-button" onClick={() => navigateTo('view-orders')}>
          View All Orders -&gt;
        </button>
      </div>

      {message && (
        <div className="card" style={{ marginBottom: '20px', color: message.includes('successfully') ? 'green' : 'red' }}>
          {message}
        </div>
      )}

      {isLoading ? (
        <div className="card">Loading order data...</div>
      ) : (
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          <div className="card" style={{ flex: 2, minWidth: '300px' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Product Name</th>
                  <th>Color</th>
                  <th>Available</th>
                  <th>Cost</th>
                  <th>Custom Option</th>
                  <th>Quantity</th>
                </tr>
              </thead>
              <tbody>
                {inventory.length === 0 ? (
                  <tr>
                    <td colSpan="6">No inventory found.</td>
                  </tr>
                ) : (
                  inventory.map((item) => (
                    <tr key={item.stock_id}>
                      <td>{item.product_name}</td>
                      <td>{item.color_name}</td>
                      <td>{item.quantity_available}</td>
                      <td>${Number(item.base_cost).toFixed(2)}</td>
                      <td>
                        <select
                          className="input-field"
                          value={customSelections[item.stock_id] || ''}
                          onChange={(event) => updateCustomSelection(item.stock_id, event.target.value)}
                        >
                          <option value="">None</option>
                          {customOptions.map((option) => (
                            <option key={option.custom_id} value={option.custom_id}>
                              {option.custom_type}
                              {option.branch_name ? ` - ${option.branch_name}` : ''}
                              {` (+${Number(option.added_charge).toFixed(2)})`}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <input
                          className="input-field"
                          type="number"
                          min="0"
                          max={item.quantity_available}
                          value={quantities[item.stock_id] || ''}
                          onChange={(event) => updateQuantity(item.stock_id, event.target.value)}
                          style={{ width: '70px', padding: '8px' }}
                        />
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="card" style={{ flex: 1, minWidth: '250px', height: 'fit-content' }}>
            <h2 style={{ marginTop: 0, color: '#0056b3' }}>Order Overview</h2>

            <label>Distribution Center</label>
            <select
              className="input-field"
              value={selectedDcId}
              onChange={(event) => setSelectedDcId(event.target.value)}
              style={{ width: '100%', marginBottom: '15px' }}
            >
              {distributionCenters.map((dc) => (
                <option key={dc.dc_id} value={dc.dc_id}>
                  {dc.facility_name}
                </option>
              ))}
            </select>

            
            <input
              className="input-field"
              type="email"
              value={contactEmail}
              onChange={(event) => setContactEmail(event.target.value)}
              placeholder="customer@email.com"
              style={{ width: '100%', marginBottom: '15px', boxSizing: 'border-box' }}
            />

            <hr style={{ borderTop: '2px solid #e0e6ed', margin: '15px 0' }} />

            {inventory
              .filter((item) => quantities[item.stock_id] > 0)
              .map((item) => {
                const quantity = quantities[item.stock_id];
                const itemTotal = quantity * (Number(item.base_cost) + getCustomCharge(item.stock_id));

                return (
                  <div key={item.stock_id} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                    <span>{item.product_name} x {quantity}</span>
                    <span>${itemTotal.toFixed(2)}</span>
                  </div>
                );
              })}

            <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', fontSize: '18px', marginBottom: '20px' }}>
              <span>Total</span>
              <span>${calculateTotal().toFixed(2)}</span>
            </div>

            <button className="primary-button" style={{ width: '100%' }} onClick={submitOrder}>
              Submit Order
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
