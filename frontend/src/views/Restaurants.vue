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
              <button class="btn dropdown-toggle" type="button" id="userDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="fas fa-user-circle"></i>
                <span v-if="user">{{ user.customerName }}</span>
                <span v-else>Loading...</span>
              </button>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                <li><router-link class="dropdown-item" to="/customer-profile"><i class="fas fa-user-cog"></i> My Profile</router-link></li>
                <li><router-link class="dropdown-item" to="/customer-orders"><i class="fas fa-receipt"></i> My Orders</router-link></li>
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
                <div class="restaurant-capacity">
                  <i class="fas fa-users"></i> Capacity: {{ restaurant.capacity }} people
                </div>
              </div>
              <div class="restaurant-card-footer">
                <button 
                  class="btn btn-primary btn-sm" 
                  @click="bookRestaurant(restaurant)"
                  :disabled="!restaurant.availability"
                >
                  Book a Table
                </button>
                <button class="btn btn-outline-primary btn-sm" @click="viewRestaurantDetails(restaurant)">
                  View Details
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
    
    <!-- Book Restaurant Modal -->
    <div class="modal fade" id="bookingModal" tabindex="-1" aria-labelledby="bookingModalLabel" aria-hidden="true" ref="bookingModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="bookingModalLabel">Book a Table at {{ selectedRestaurant?.name }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitReservation">
              <div class="mb-3">
                <label for="partySize" class="form-label">Number of People</label>
                <input type="number" class="form-control" id="partySize" v-model="reservation.count" min="1" :max="selectedRestaurant?.capacity || 10" required>
              </div>
              <div class="mb-3">
                <label for="reservationDate" class="form-label">Date</label>
                <input type="date" class="form-control" id="reservationDate" v-model="reservation.date" required>
              </div>
              <div class="mb-3">
                <label for="reservationTime" class="form-label">Time</label>
                <input type="time" class="form-control" id="reservationTime" v-model="reservation.time" required>
              </div>
              <div class="mb-3">
                <label for="specialRequests" class="form-label">Special Requests (Optional)</label>
                <textarea class="form-control" id="specialRequests" rows="3" v-model="reservation.specialRequests"></textarea>
              </div>
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                  <span v-if="isSubmitting">
                    <i class="fas fa-spinner fa-spin"></i> Booking...
                  </span>
                  <span v-else>
                    Confirm Booking
                  </span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { supabaseClient, signOut, getCurrentUser } from '@/services/supabase';
import { getAllRestaurants, createReservation, getRestaurantsByAvailability } from '@/services/restaurantService';

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
    
    // Modal and reservation related refs
    const bookingModal = ref(null);
    const modal = ref(null);
    const selectedRestaurant = ref(null);
    const isSubmitting = ref(false);
    const reservation = ref({
      restaurant_id: null,
      user_id: null,
      count: 2,
      date: new Date().toISOString().split('T')[0], // tdy
      time: '19:00',
      status: 'Booked',
      specialRequests: ''
    });
    
    // Computed property to get unique cuisines
    const availableCuisines = computed(() => {
      const cuisines = restaurants.value.map(r => r.cuisine);
      return [...new Set(cuisines)].sort();
    });
    
    // Load user data and restaurants when component mounts
    onMounted(async () => {
      try {
        // Initialize Bootstrap modal
        if (typeof bootstrap !== 'undefined') {
          modal.value = new bootstrap.Modal(document.getElementById('bookingModal'));
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
    
    // Cleanup on component unmount
    onUnmounted(() => {
      if (modal.value) {
        modal.value.dispose();
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
        
        // Set user_id in reservation object
        reservation.value.user_id = currentUser.id;
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
    
    // Book restaurant function (not yet implemented)
    const bookRestaurant = (restaurant) => {
      selectedRestaurant.value = restaurant;
      reservation.value.restaurant_id = restaurant.restaurant_id;
      
    };
    
    // View restaurant details function (not yet implemented)
    const viewRestaurantDetails = (restaurant) => {
      // navigate to a details page
      router.push(`/restaurant-details/${restaurant.restaurant_id}`);
    };
    
    // Submit reservation (not yet implemented)
    const submitReservation = async () => {
      try {
        isSubmitting.value = true;
        
        // Create reservation object from the form data
        const reservationDateTime = new Date(`${reservation.value.date}T${reservation.value.time}`);
        
        const reservationData = {
          restaurant_id: selectedRestaurant.value.restaurant_id,
          user_id: user.value.id,
          status: 'Booked',
          count: reservation.value.count,
          price: null, // Will be set by the restaurant if needed
          time: reservationDateTime.toISOString(),
          special_requests: reservation.value.specialRequests
        };
        
        // Call the API to create the reservation
        const result = await createReservation(reservationData);
        
        if (result.success) {
          // Close the modal
          if (modal.value) {
            modal.value.hide();
          }
          
          // Show success message
          alert('Reservation created successfully!');
          
          // Reset the form
          reservation.value = {
            restaurant_id: null,
            user_id: user.value.id,
            count: 2,
            date: new Date().toISOString().split('T')[0],
            time: '19:00',
            status: 'Booked',
            specialRequests: ''
          };
        } else {
          throw new Error('Failed to create reservation');
        }
      } catch (error) {
        console.error('Error booking reservation:', error);
        alert('Failed to book reservation. Please try again later.');
      } finally {
        isSubmitting.value = false;
      }
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
      restaurants,
      filteredRestaurants,
      isLoading,
      errorMessage,
      searchQuery,
      cuisineFilter,
      availabilityFilter,
      availableCuisines,
      bookingModal,
      selectedRestaurant,
      reservation,
      isSubmitting,
      filterRestaurants,
      bookRestaurant,
      viewRestaurantDetails,
      submitReservation,
      logout
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
  justify-content: space-between;
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