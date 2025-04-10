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
                <li><router-link class="dropdown-item" to="/reservations"><i class="fas fa-calendar-check"></i> My Reservations</router-link></li>
                <li><router-link class="dropdown-item" to="/delivery-orders"><i class="fas fa-truck"></i> My Delivery Orders</router-link></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click.prevent="logout"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Restaurants Content -->
    <div class="dashboard-container">
      <div class="container">
        <!-- Page Title -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="welcome-card">
              <h2>Restaurants</h2>
              <p>Discover and explore restaurants near you</p>
              
              <!-- Mode Selection Buttons (not implemented)
              <div class="mode-selection mt-3">
                <button 
                  class="btn btn-lg me-2" 
                  :class="orderType === 'dine_in' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="setOrderType('dine_in')"
                >
                  <i class="fas fa-utensils me-2"></i>Dine In
                </button>
                <button 
                  class="btn btn-lg" 
                  :class="orderType === 'delivery' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="setOrderType('delivery')"
                >
                  <i class="fas fa-motorcycle me-2"></i>Delivery
                </button>
              </div> -->
              
              <!-- Mode Indicator -->
              <div class="mode-indicator mt-3" v-if="orderType === 'delivery'">
                <div class="alert alert-info">
                  <i class="fas fa-info-circle me-2"></i>
                  <strong>Delivery Mode:</strong> Your order will be delivered to your address.
                </div>
              </div>
              <div class="mode-indicator mt-3" v-else>
                <div class="alert alert-info">
                  <i class="fas fa-info-circle me-2"></i>
                  <strong>Dine In Mode:</strong> You can book a table and dine at the restaurant.
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Search Bar -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="search-container">
              <input 
                type="text" 
                v-model="searchQuery" 
                class="search-input" 
                placeholder="Search by name or cuisine..."
              >
              <button class="search-btn" @click="filterRestaurants">
                <i class="fas fa-search"></i> Search
              </button>
            </div>
          </div>
        </div>
        
        <!-- Filter Options -->
        <div class="row mb-4">
          <div class="col-md-3 mb-3">
            <select class="form-select" v-model="cuisineFilter">
              <option value="">All Cuisines</option>
              <option v-for="cuisine in availableCuisines" :key="cuisine" :value="cuisine">
                {{ cuisine }}
              </option>
            </select>
          </div>
          <div class="col-md-3 mb-3">
            <select class="form-select" v-model="availabilityFilter">
              <option value="">All Availability</option>
              <option value="1">Available Now</option>
              <option value="0">Currently Unavailable</option>
            </select>
          </div>
          <div class="col-md-3 mb-3">
            <button class="btn btn-primary w-100" @click="filterRestaurants">
              Apply Filters
            </button>
          </div>
        </div>
        
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-container">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p>Loading restaurants...</p>
        </div>
        
        <!-- Error Message -->
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
          {{ errorMessage }}
        </div>
        
        <!-- Restaurants Grid -->
        <div v-if="!isLoading && filteredRestaurants.length > 0" class="row">
          <div v-for="restaurant in filteredRestaurants" :key="restaurant.restaurant_id" class="col-lg-4 col-md-6 mb-4">
            <div class="restaurant-card">
              <div class="restaurant-card-header">
                <span 
                  class="restaurant-status" 
                  :class="{ 'status-open': restaurant.availability, 'status-closed': !restaurant.availability }"
                >
                  {{ restaurant.availability ? 'Open' : 'Closed' }}
                </span>
                <h3 class="restaurant-name">{{ restaurant.name }}</h3>
                <div class="restaurant-rating">
                  <i class="fas fa-star"></i> {{ restaurant.rating }}
                </div>
              </div>
              <div class="restaurant-card-body">
                <div class="restaurant-cuisine">
                  <i class="fas fa-utensils"></i> {{ restaurant.cuisine }}
                </div>
                <div class="restaurant-address">
                  <i class="fas fa-map-marker-alt"></i> {{ restaurant.address }}
                </div>
                <div class="restaurant-capacity" v-if="orderType === 'dine_in'">
                  <i class="fas fa-users"></i> Capacity: {{ restaurant.capacity }} table(s)
                </div>
                <div class="restaurant-delivery" v-if="orderType === 'delivery'">
                  <i class="fas fa-motorcycle"></i> Delivery Available
                </div>
              </div>
              <div class="restaurant-card-footer">
                <button 
                  class="btn btn-primary btn-sm" 
                  @click="bookRestaurant(restaurant)"
                  :disabled="!restaurant.availability"
                >
                  {{ orderType === 'delivery' ? 'Order & Delivery' : 'Order & Book' }}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- No Results -->
        <div v-if="!isLoading && filteredRestaurants.length === 0" class="empty-state">
          <i class="fas fa-search"></i>
          <p>No restaurants found matching your criteria.</p>
          <small>Try adjusting your filters or search query.</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { supabaseClient, signOut, getCurrentUser } from '@/services/supabase';
import { getAllRestaurants, getRestaurantsByAvailability } from '@/services/restaurantService';

export default {
  name: 'Restaurants',
  setup() {
    const router = useRouter();
    const user = ref(null);
    const restaurants = ref([]);
    const filteredRestaurants = ref([]);
    const isLoading = ref(true);
    const errorMessage = ref('');
    const searchQuery = ref('');
    const cuisineFilter = ref('');
    const availabilityFilter = ref('');
    const orderType = ref('dine_in'); // Default to dine_in
    
    // Computed property to get unique cuisines
    const availableCuisines = computed(() => {
      const cuisines = restaurants.value.map(r => r.cuisine);
      return [...new Set(cuisines)].sort();
    });
    
    // Computed property for button text based on order type
    const buttonText = computed(() => {
      return orderType.value === 'delivery' ? 'Order & Delivery' : 'Order & Book';
    });
    
    // Load user data and restaurants when component mounts
    onMounted(async () => {
      try {
        // Get order type from localStorage
        const storedOrderType = localStorage.getItem('orderType');
        if (storedOrderType) {
          orderType.value = storedOrderType;
        }
        
        await loadUserData();
        await loadRestaurants();
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
        // Check if user is logged in
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
          id: profileData.id
        };
      } catch (error) {
        console.error('Error loading user data:', error);
        throw error;
      }
    };
    
    // Load restaurants data
    const loadRestaurants = async () => {
      try {
        // Fetch restaurants from the backend API
        const restaurantsData = await getAllRestaurants();
        restaurants.value = restaurantsData;
        
        // Initialize filteredRestaurants with all restaurants
        filteredRestaurants.value = [...restaurants.value];
      } catch (error) {
        console.error('Error loading restaurants:', error);
        errorMessage.value = 'Failed to load restaurants. Please try again later.';
        throw error;
      }
    };
    
    // Filter restaurants based on search query and filters
    const filterRestaurants = async () => {
      try {
        isLoading.value = true;
        errorMessage.value = '';
        
        let baseRestaurants;
        
        // Get base restaurant list 
        if (availabilityFilter.value !== '') {
          baseRestaurants = await getRestaurantsByAvailability(availabilityFilter.value);
        } else {
          baseRestaurants = restaurants.value;
        }
        
        // client-side filters 
        filteredRestaurants.value = baseRestaurants.filter(restaurant => {
          // Search query filter
          const searchMatches = !searchQuery.value || 
            restaurant.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
            restaurant.cuisine.toLowerCase().includes(searchQuery.value.toLowerCase());
          
          // Cuisine filter
          const cuisineMatches = !cuisineFilter.value || 
            restaurant.cuisine === cuisineFilter.value;
          
          return searchMatches && cuisineMatches;
        });
      } catch (error) {
        console.error('Error filtering restaurants:', error);
        errorMessage.value = 'Failed to filter restaurants. Please try again.';
      } finally {
        isLoading.value = false;
      }
    };
    
    // Navigate to the restaurant menu page
    const bookRestaurant = (restaurant) => {
      // Store restaurant and order type info for the menu page
      localStorage.setItem('selectedRestaurant', JSON.stringify(restaurant));
      // Navigate to the restaurant menu page
      router.push(`/restaurant/${restaurant.restaurant_id}/menu`);
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
    
    // Simple method to toggle dropdown manually
    const toggleDropdown = (event) => {
      const dropdownMenu = event.target.closest('.dropdown').querySelector('.dropdown-menu');
      dropdownMenu.classList.toggle('show');
    };
    
    // Set order type
    const setOrderType = (type) => {
      orderType.value = type;
      localStorage.setItem('orderType', type);
    };
    
    return {
      user,
      restaurants,
      filteredRestaurants,
      isLoading,
      errorMessage,
      searchQuery,
      cuisineFilter,
      availabilityFilter,
      availableCuisines,
      orderType,
      buttonText,
      filterRestaurants,
      bookRestaurant,
      logout,
      toggleDropdown,
      setOrderType
    };
  }
};
</script>

<style scoped>
.restaurant-card {
  background-color: white;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.restaurant-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.restaurant-card-header {
  padding: 1.5rem;
  background: linear-gradient(to right, #f8f9fa, #ffffff);
  position: relative;
}

.restaurant-status {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-open {
  background-color: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.status-closed {
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.restaurant-name {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  padding-right: 70px;
}

.restaurant-rating {
  display: inline-block;
  background-color: rgba(255, 193, 7, 0.1);
  color: #ffc107;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 600;
}

.restaurant-rating i {
  margin-right: 5px;
}

.restaurant-card-body {
  padding: 1.5rem;
  flex-grow: 1;
}

.restaurant-cuisine, .restaurant-address, .restaurant-capacity {
  margin-bottom: 0.75rem;
  color: #6c757d;
}

.restaurant-cuisine i, .restaurant-address i, .restaurant-capacity i {
  width: 20px;
  margin-right: 10px;
  color: var(--primary-color);
}

.restaurant-card-footer {
  padding: 1.5rem;
  border-top: 1px solid #f1f1f1;
  display: flex;
  justify-content: center;
}

.btn-outline-primary {
  background-color: transparent;
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.btn-outline-primary:hover {
  background-color: var(--primary-color);
  color: white;
}

.empty-state {
  background-color: white;
  border-radius: 15px;
  padding: 3rem 1.5rem;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  margin-top: 2rem;
}

.empty-state i {
  font-size: 3rem;
  color: #dee2e6;
  margin-bottom: 1rem;
  display: block;
}

.empty-state p {
  font-size: 1.2rem;
  font-weight: 600;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.empty-state small {
  color: #adb5bd;
}
</style>