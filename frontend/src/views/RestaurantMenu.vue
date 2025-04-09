<template>
    <div>
      <!-- Dashboard Header -->
      <div class="dashboard-header">
        <div class="container">
          <div class="d-flex justify-content-between align-items-center">
            <router-link to="/" class="dashboard-logo">
              <span>FeastFinder</span>
            </router-link>
            <div class="dashboard-user">
              <div class="dropdown">
                <button class="btn dropdown-toggle" type="button" id="userDropdown" @click="toggleDropdown">
                  <i class="fas fa-user-circle"></i>
                  <span v-if="user">{{ user.customerName }}</span>
                  <span v-else>Loading...</span>
                </button>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                  <li><router-link class="dropdown-item" to="/customer-dashboard"><i class="fas fa-home"></i> Dashboard</router-link></li>
                  <li><router-link class="dropdown-item" to="/reservations"><i class="fas fa-calendar-check"></i> My Reservations</router-link></li>
                  <li><hr class="dropdown-divider"></li>
                  <li><a class="dropdown-item" href="#" @click.prevent="logout"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Menu Content -->
      <div class="dashboard-container">
        <div class="container">
          <!-- Page Title -->
          <div class="row mb-4">
            <div class="col-12">
              <div class="welcome-card">
                <h2>{{ restaurant ? restaurant.name : 'Restaurant' }} Menu</h2>
                <p>Select an item you'd like to order</p>
                
                <!-- Order Type Indicator -->
                <div class="order-type-indicator mt-3">
                  <div class="alert" :class="orderType === 'delivery' ? 'alert-info' : 'alert-success'">
                    <i :class="['fas', orderType === 'delivery' ? 'fa-motorcycle' : 'fa-utensils', 'me-2']"></i>
                    <strong>{{ orderType === 'delivery' ? 'Delivery Mode' : 'Dine In Mode' }}:</strong> 
                    {{ orderType === 'delivery' ? 'Your order will be delivered to your address.' : 'You can book a table and dine at the restaurant.' }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Loading State -->
          <div v-if="isLoading" class="loading-container">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p>Loading menu items...</p>
          </div>
          
          <!-- Error Message -->
          <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>
          
          <!-- Menu Items -->
          <div v-if="!isLoading && menuItems.length > 0" class="row">
            <div class="col-md-8">
              <div class="card">
                <div class="card-header">
                  <h3 class="mb-0">Menu Items</h3>
                </div>
                <div class="card-body">
                  <div class="menu-items-list">
                    <div 
                      v-for="item in menuItems" 
                      :key="item.menu_id" 
                      class="menu-item"
                      :class="{ 'selected': selectedItem && selectedItem.menu_id === item.menu_id }"
                      @click="selectItem(item)"
                    >
                      <div class="menu-item-content">
                        <h4 class="menu-item-name">{{ item.item_name }}</h4>
                        <p class="menu-item-description">{{ item.description }}</p>
                        <div class="menu-item-price">${{ Number(item.price).toFixed(2) }}</div>
                      </div>
                      <div class="menu-item-select">
                        <i 
                          class="fas" 
                          :class="selectedItem && selectedItem.menu_id === item.menu_id ? 'fa-check-circle text-success' : 'fa-circle text-secondary'"
                        ></i>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="card order-summary-card">
                <div class="card-header">
                  <h3 class="mb-0">Your Selection</h3>
                </div>
                <div class="card-body">
                  <div v-if="selectedItem" class="selected-item-summary">
                    <h4>{{ selectedItem.item_name }}</h4>
                    <p class="selected-item-description">{{ selectedItem.description }}</p>
                    <div class="d-flex justify-content-between align-items-center mb-3">
                      <div class="quantity-control">
                        <button 
                          class="btn btn-sm btn-outline-secondary" 
                          @click="decreaseQuantity"
                          :disabled="quantity <= 1"
                        >
                          <i class="fas fa-minus"></i>
                        </button>
                        <span class="mx-2">{{ quantity }}</span>
                        <button 
                          class="btn btn-sm btn-outline-secondary" 
                          @click="increaseQuantity"
                        >
                          <i class="fas fa-plus"></i>
                        </button>
                      </div>
                      <div class="item-price">${{ (Number(selectedItem.price) * quantity).toFixed(2) }}</div>
                    </div>
                    
                    <div class="order-total">
                      <h5>Total</h5>
                      <h5>${{ (Number(selectedItem.price) * quantity).toFixed(2) }}</h5>
                    </div>
                    
                    <button 
                      class="btn btn-primary w-100 mt-3" 
                      @click="proceedToCheckout"
                    >
                      Proceed to Checkout
                    </button>
                  </div>
                  
                  <div v-else class="empty-selection">
                    <i class="fas fa-utensils fa-2x mb-3 text-secondary"></i>
                    <p>No item selected</p>
                    <small>Please select an item from the menu to proceed</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- if got no menu items(shldnt happen) -->
          <div v-if="!isLoading && menuItems.length === 0" class="empty-state">
            <i class="fas fa-utensils"></i>
            <p>No menu items available for this restaurant.</p>
            <small>Please check back later or try another restaurant.</small>
            <div class="mt-3">
              <router-link to="/restaurants" class="btn btn-primary">
                Back to Restaurants
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { getCurrentUser, signOut } from '@/services/supabase';
  import { getRestaurantById } from '@/services/restaurantService';
  import { getRestaurantMenu } from '@/services/menuService';
  
  export default {
    name: 'RestaurantMenu',
    setup() {
      const router = useRouter();
      const route = useRoute();
      
      const user = ref(null);
      const restaurant = ref(null);
      const menuItems = ref([]);
      const selectedItem = ref(null);
      const quantity = ref(1);
      const isLoading = ref(true);
      const errorMessage = ref('');
      const orderType = ref('dine_in'); // Default to dine_in
      
      // get restaurant ID from route params
      const restaurantId = parseInt(route.params.id);
      
      // Load data when component mounts
      onMounted(async () => {
        try {
          // Make sure we have a valid restaurant ID
          if (!restaurantId || isNaN(restaurantId)) {
            throw new Error('Invalid restaurant ID');
          }
          
          // Get order type from localStorage
          const storedOrderType = localStorage.getItem('orderType');
          if (storedOrderType) {
            orderType.value = storedOrderType;
          }
          
          // Load user data
          await loadUserData();
          
          // Load restaurant and menu data
          await Promise.all([
            loadRestaurant(),
            loadMenu()
          ]);
        } catch (error) {
          console.error('Error during initialization:', error);
          errorMessage.value = 'An error occurred while loading the page. Please try again.';
        } finally {
          isLoading.value = false;
        }
      });
      
      // Load user data
      const loadUserData = async () => {
        try {
          const currentUser = await getCurrentUser();
          
          if (!currentUser) {
            // Not logged in, redirect to login
            router.push('/login');
            return;
          }
          
          // Set user data
          user.value = {
            id: currentUser.id,
            customerName: currentUser.user_metadata?.name || 'Customer'
          };
        } catch (error) {
          console.error('Error loading user data:', error);
          throw error;
        }
      };
      
      // Load restaurant data
      const loadRestaurant = async () => {
        try {
          const restaurantData = await getRestaurantById(restaurantId);
          if (!restaurantData) {
            throw new Error('Restaurant not found');
          }
          restaurant.value = restaurantData;
        } catch (error) {
          console.error('Error loading restaurant:', error);
          throw error;
        }
      };
      
      // Load menu data
      const loadMenu = async () => {
        try {
          const menuData = await getRestaurantMenu(restaurantId);
          menuItems.value = menuData;
        } catch (error) {
          console.error('Error loading menu:', error);
          throw error;
        }
      };
      
      // Select a menu item (reset qty when click sth else)
      const selectItem = (item) => {
        selectedItem.value = item;
        quantity.value = 1;
      };
      
      // Increase item quantity
      const increaseQuantity = () => {
        quantity.value++;
      };
      
      // Decrease item quantity
      const decreaseQuantity = () => {
        if (quantity.value > 1) {
          quantity.value--;
        }
      };
      
      // go checkout
      const proceedToCheckout = () => {
        if (!selectedItem.value) {
          alert('Please select an item first');
          return;
        }
        
        // Store order info in localStorage for the checkout page
        const orderInfo = {
          restaurantId: restaurantId,
          restaurantName: restaurant.value.name,
          item: {
            menuId: selectedItem.value.menu_id,
            name: selectedItem.value.item_name,
            price: Number(selectedItem.value.price),
            quantity: quantity.value,
            total: Number(selectedItem.value.price) * quantity.value
          }
        };
        
        localStorage.setItem('orderInfo', JSON.stringify(orderInfo));
        
        // go checkout page
        router.push(`/checkout/${restaurantId}`);
      };
      
      // Logout function
      const logout = async () => {
        try {
          isLoading.value = true;
          await signOut();
          router.push('/');
        } catch (error) {
          console.error('Logout error:', error);
          errorMessage.value = 'Failed to log out. Please try again.';
        } finally {
          isLoading.value = false;
        }
      };
      
      // Simple method to toggle dropdown manually
      const toggleDropdown = (event) => {
        const dropdownMenu = event.target.closest('.dropdown').querySelector('.dropdown-menu');
        dropdownMenu.classList.toggle('show');
      };
      
      return {
        user,
        restaurant,
        menuItems,
        selectedItem,
        quantity,
        isLoading,
        errorMessage,
        orderType,
        selectItem,
        increaseQuantity,
        decreaseQuantity,
        proceedToCheckout,
        logout,
        toggleDropdown
      };
    }
  };
  </script>
  
  <style scoped>
  .menu-items-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .menu-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    border-radius: 10px;
    background-color: #fff;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .menu-item:hover {
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    transform: translateY(-2px);
  }
  
  .menu-item.selected {
    background-color: rgba(240, 90, 40, 0.05);
    border-left: 4px solid var(--primary-color);
  }
  
  .menu-item-content {
    flex: 1;
  }
  
  .menu-item-name {
    font-weight: 600;
    margin-bottom: 5px;
    color: var(--dark-color);
  }
  
  .menu-item-description {
    color: #6c757d;
    font-size: 0.9rem;
    margin-bottom: 5px;
  }
  
  .menu-item-price {
    font-weight: 700;
    color: var(--primary-color);
    font-size: 1.1rem;
  }
  
  .menu-item-select {
    margin-left: 15px;
    font-size: 1.5rem;
  }
  
  .order-summary-card {
    position: sticky;
    top: 100px;
  }
  
  .selected-item-summary {
    padding: 10px 0;
  }
  
  .selected-item-description {
    color: #6c757d;
    font-size: 0.9rem;
    margin-bottom: 15px;
  }
  
  .quantity-control {
    display: flex;
    align-items: center;
    font-weight: 600;
  }
  
  .item-price {
    font-weight: 700;
    font-size: 1.2rem;
    color: var(--primary-color);
  }
  
  .order-total {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #eee;
  }
  
  .empty-selection {
    text-align: center;
    padding: 30px 0;
    color: #6c757d;
  }
  
  .empty-selection i {
    display: block;
    margin-bottom: 10px;
  }
  </style>