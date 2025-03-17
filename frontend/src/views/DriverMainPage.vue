<template>
    <div class="driver-main-page">
      <!-- Header -->
      <header class="header">
        <div class="header-content">
          <img src="../assets/logo.png" alt="App Logo" class="logo" />
          <h1>Delivery Driver Dashboard</h1>
        </div>
      </header>
  
      <!-- Main Content -->
      <main class="content">
        <!-- Search/Request Orders Button -->
        <button @click="searchOrders" :disabled="isLoading" class="search-button">
          {{ isLoading ? 'Searching...' : 'Search/Request Orders' }}
        </button>
  
        <!-- Notification Area -->
        <section v-if="notifications.length" class="notifications">
          <h2>Notifications</h2>
          <ul>
            <li v-for="(notification, index) in notifications" :key="index">
              {{ notification }}
            </li>
          </ul>
        </section>
  
        <!-- Nearby Orders Map -->
        <section class="map-section">
          <h2>Nearby Orders</h2>
          <OrderMap :orders="nearbyOrders" @order-selected="handleOrderSelection" />
        </section>
  
        <!-- Routing Service -->
        <section v-if="currentOrder" class="routing-section">
          <h2>Routing Instructions</h2>
          <RoutingService
            :order="currentOrder"
            @pickup-complete="handlePickupComplete"
          />
        </section>
      </main>
    </div>
  </template>
  
  <script>
  import OrderMap from './OrderMap.vue';
  import RoutingService from './RoutingService.vue';
  
  export default {
    components: { OrderMap, RoutingService },
    data() {
      return {
        nearbyOrders: [],
        currentOrder: null,
        isLoading: false,
        notifications: [], // Placeholder for notifications
      };
    },
    methods: {
      searchOrders() {
        this.isLoading = true;
        this.notifications.push('Searching for new orders...');
        setTimeout(() => {
          this.nearbyOrders = [
            { id: 1, restaurant: 'Restaurant A', location: '123 Main St', destination: '456 Elm St', items: ['Pizza', 'Burger'] },
            { id: 2, restaurant: 'Restaurant B', location: '789 Oak St', destination: '321 Pine St', items: ['Sushi', 'Salad'] },
          ];
          this.isLoading = false;
          this.notifications.push('New orders found!');
        }, 2000);
      },
      handleOrderSelection(order) {
        this.currentOrder = order;
        this.notifications.push(`Selected order #${order.id}`);
      },
      handlePickupComplete(orderId) {
        this.notifications.push(`Order #${orderId} picked up.`);
      },
    },
  };
  </script>
  
  <style scoped>
  .driver-main-page {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: #f9f9f9;
  }
  
  .header {
    background-color: #4caf50;
    color: white;
    padding: 1rem;
    text-align: center;
    font-size: 1.2rem;
    font-weight: bold;
  }
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
  }
  
  .logo {
    width: 40px;
    height: 40px;
  }
  
  .content {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .search-button:hover {
    background-color: #0056b3;
  }
  
  .search-button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .notifications {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 1rem;
  }
  
  .notifications h2 {
    margin-top: 0;
    font-size: 1.1rem;
    color: #333;
  }
  
  .notifications ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .notifications li {
    background-color: #f0f0f0;
    margin-bottom: 0.5rem;
    padding: 0.5rem;
    border-radius: 8px;
    font-size: 0.9rem;
    color: #666;
  }
  </style>