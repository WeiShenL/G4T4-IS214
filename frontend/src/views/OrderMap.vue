<template>
    <div class="order-map">
      <ul class="order-list">
        <li
          v-for="order in orders"
          :key="order.id"
          class="order-card"
        >
          <div class="order-details">
            <strong>{{ order.restaurant }}</strong>
            <p>To: {{ order.destination }}</p>
            <p><small>{{ order.items.join(', ') }}</small></p>
          </div>
          <div class="order-actions">
            <button @click="acceptOrder(order)" class="accept-button">Accept</button>
            <button @click="declineOrder(order)" class="decline-button">Decline</button>
          </div>
        </li>
      </ul>
      <!-- Placeholder for actual map integration -->
      <div class="map-placeholder">
        <p>Map will be displayed here</p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      orders: {
        type: Array,
        required: true,
      },
    },
    emits: ['order-selected'],
    methods: {
      acceptOrder(order) {
        alert(`Order #${order.id} accepted!`);
        this.$emit('order-selected', order);
      },
      declineOrder(order) {
        alert(`Order #${order.id} declined.`);
      },
    },
  };
  </script>
  
  <style scoped>
  .order-map {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .order-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .order-card {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  .order-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .order-details strong {
    font-size: 1rem;
    color: #333;
  }
  
  .order-details p {
    margin: 0.2rem 0 0;
    font-size: 0.9rem;
    color: #666;
  }
  
  .order-actions {
    display: flex;
    gap: 0.5rem;
  }
  
  .accept-button {
    background-color: #28a745;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .accept-button:hover {
    background-color: #218838;
  }
  
  .decline-button {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .decline-button:hover {
    background-color: #c82333;
  }
  </style>