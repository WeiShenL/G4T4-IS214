<template>
    <div>
      <!-- Dashboard Header -->
      <div class="dashboard-header">
        <div class="container">
          <div class="d-flex justify-content-between align-items-center">
            <router-link to="/customer-dashboard" class="dashboard-logo">
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
                  <li><router-link class="dropdown-item" to="/delivery-orders"><i class="fas fa-truck"></i> My Delivery Orders</router-link></li>
                  <li><router-link class="dropdown-item" to="/reservations"><i class="fas fa-calendar-check"></i> My Reservations</router-link></li>
                  <li><hr class="dropdown-divider"></li>
                  <li><a class="dropdown-item" href="#" @click.prevent="logout"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Delivery Orders Content -->
      <div class="dashboard-container">
        <div class="container">
          <!-- Page Title -->
          <div class="row mb-4">
            <div class="col-12">
              <div class="welcome-card">
                <h2>My Delivery Orders</h2>
                <p>View your food delivery orders</p>
              </div>
            </div>
          </div>
          
          <!-- Loading State -->
          <div v-if="isLoading" class="loading-container">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p>Loading your delivery orders...</p>
          </div>
          
          <!-- Error Message -->
          <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>
          
          <!-- Orders Table -->
          <div v-if="!isLoading && orders.length > 0" class="card mb-4">
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Restaurant</th>
                      <th>Item</th>
                      <th>Quantity</th>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="order in orders" :key="order.order_id">
                      <td>{{ getRestaurantName(order.restaurant_id) }}</td>
                      <td>{{ order.item_name }}</td>
                      <td>{{ order.quantity }}</td>
                      <td>{{ formatDate(order.created_at) }}</td>
                      <td>{{ formatTime(order.created_at) }}</td>
                      <td>${{ order.order_price ? order.order_price.toFixed(2) : '0.00' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          
          <!-- No Orders -->
          <div v-if="!isLoading && orders.length === 0" class="empty-state">
            <i class="fas fa-truck"></i>
            <p>You don't have any delivery orders yet.</p>
            <small>Order food from your favorite restaurant to see it here.</small>
            <div class="mt-3">
              <button class="btn btn-primary" @click="browseRestaurantsForDelivery">
                Browse Restaurants
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>
  
<script>
import { ref, onMounted } from 'vue'; 
import { useRouter } from 'vue-router';
import { supabaseClient, signOut, getCurrentUser } from '@/services/supabase';
import { getAllRestaurants } from '@/services/restaurantService';
import { getUserOrdersByType } from '@/services/orderService';

export default {
  name: 'CustomerDeliveryOrders',
  setup() {
    const router = useRouter();
    const user = ref(null);
    const orders = ref([]);
    const restaurants = ref([]);
    const isLoading = ref(true);
    const errorMessage = ref('');

    // toggle dropdown manually
    const toggleDropdown = (event) => {
      const dropdownMenu = event.target.closest('.dropdown').querySelector('.dropdown-menu');
      dropdownMenu.classList.toggle('show');
    };

    // load data when the component mounts
    onMounted(async () => {
      try {
        await loadUserData(); 
        if (user.value) {
          await Promise.all([loadRestaurants(), loadOrders()]);
        }
      } catch (error) {
        console.error('Error during initialization:', error);
        errorMessage.value = 'An error occurred while loading the page. Please try again.';
      } finally {
        isLoading.value = false;
      }
    });
    
    // load user data
    const loadUserData = async () => {
      try {
        // logged in?
        const currentUser = await getCurrentUser();
        
        if (!currentUser) {
          // Not logged in, redirect to login
          router.push('/login');
          return;
        }
        
        // Get customer profile data
        const { data: profileData, error: profileError } = await supabaseClient
          .from('customer_profiles')
          .select('*')
          .eq('id', currentUser.id)
          .single();
        
        if (profileError) {
          console.error('Error fetching profile data:', profileError);
          throw profileError;
        }
        
        // Update user ref with profile data
        user.value = {
          customerName: profileData.customer_name,
          phoneNumber: profileData.phone_number,
          streetAddress: profileData.street_address,
          postalCode: profileData.postal_code,
          id: currentUser.id
        };
      } catch (error) {
        console.error('Error loading user data:', error);
        throw error;
      }
    };
    
    // Load restaurants data for names
    const loadRestaurants = async () => {
      try {
        const restaurantsData = await getAllRestaurants();
        restaurants.value = restaurantsData;
      } catch (error) {
        console.error('Error loading restaurants:', error);
        // Not fatal, so just log the error
      }
    };
    
    // Load user's delivery orders
    const loadOrders = async () => {
      try {
        if (!user.value || !user.value.id) {
          console.warn('User ID not available yet, skipping order loading');
          return; // Skip loading if user ID is not available yet
        }
        
        console.log('Loading delivery orders for user ID:', user.value.id);
        // api call
        const userOrders = await getUserOrdersByType(user.value.id.toString(), 'delivery');
        orders.value = userOrders;
        
        console.log('Loaded delivery orders:', orders.value);
      } catch (error) {
        console.error('Error loading delivery orders:', error);
        errorMessage.value = 'Failed to load your delivery orders. Please try again later.';
        // Don't throw the error, just handle it here
      }
    };

    
    // Format date from ISO string
    const formatDate = (isoString) => {
      if (!isoString) return 'N/A';
      const date = new Date(isoString);
      return date.toLocaleDateString();
    };
    
    // Format time from ISO string
    const formatTime = (isoString) => {
      if (!isoString) return 'N/A';
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };
    
    // Get restaurant name from ID
    const getRestaurantName = (restaurantId) => {
      const restaurant = restaurants.value.find(r => r.restaurant_id === restaurantId);
      return restaurant ? restaurant.name : `Restaurant #${restaurantId}`;
    };
    
    // Navigate to restaurants page with delivery option selected
    const browseRestaurantsForDelivery = () => {
      localStorage.setItem('orderType', 'delivery');
      router.push('/restaurants');
    };
    
    // Logout function
    const logout = async () => {
      try {
        isLoading.value = true;
        const { error } = await signOut();
        if (error) throw error;
        router.push('/');
      } catch (error) {
        console.error('Logout error:', error);
        errorMessage.value = 'Failed to log out. Please try again.';
      } finally {
        isLoading.value = false;
      }
    };
    
    return {
      user,
      orders,
      isLoading,
      errorMessage,
      formatDate,
      formatTime,
      getRestaurantName,
      browseRestaurantsForDelivery,
      logout,
      toggleDropdown
    };
  }
};
</script>

<style scoped>
.badge {
  padding: 6px 10px;
}

/* Add some button styling */
.btn-outline-danger {
  transition: all 0.3s ease;
}

.btn-outline-danger:hover {
  background-color: #dc3545;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(220, 53, 69, 0.3);
}
</style> 