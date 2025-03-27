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
      
      <!-- Reservations Content -->
      <div class="dashboard-container">
        <div class="container">
          <!-- Page Title -->
          <div class="row mb-4">
            <div class="col-12">
              <div class="welcome-card">
                <h2>My Reservations</h2>
                <p>View your restaurant reservations</p>
              </div>
            </div>
          </div>
          
          <!-- Loading State -->
          <div v-if="isLoading" class="loading-container">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p>Loading your reservations...</p>
          </div>
          
          <!-- Error Message -->
          <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>
          
          <!-- Reservations Table -->
          <div v-if="!isLoading && reservations.length > 0" class="card mb-4">
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Restaurant</th>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Party Size</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="reservation in reservations" :key="reservation.reservation_id">
                      <td>{{ getRestaurantName(reservation.restaurant_id) }}</td>
                      <td>{{ formatDate(reservation.time) }}</td>
                      <td>{{ formatTime(reservation.time) }}</td>
                      <td>{{ reservation.count }}</td>
                      <td>
                        <span 
                          class="badge"
                          :class="getStatusClass(reservation.status)"
                        >
                          {{ reservation.status }}
                        </span>
                      </td>
                      <td>
                        <button 
                          class="btn btn-sm btn-outline-primary"
                          @click="viewReservation(reservation)"
                        >
                          Details
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          
          <!-- No Reservations -->
          <div v-if="!isLoading && reservations.length === 0" class="empty-state">
            <i class="fas fa-calendar-alt"></i>
            <p>You don't have any reservations yet.</p>
            <small>Book a table at your favorite restaurant to see it here.</small>
            <div class="mt-3">
              <router-link to="/restaurants" class="btn btn-primary">
                Browse Restaurants
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Reservation Details Modal -->
      <div class="modal fade" id="reservationModal" tabindex="-1" aria-labelledby="reservationModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content" v-if="selectedReservation">
            <div class="modal-header">
              <h5 class="modal-title" id="reservationModalLabel">Reservation Details</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="reservation-details">
                <div class="detail-item">
                  <span class="detail-label">Restaurant:</span>
                  <span class="detail-value">{{ getRestaurantName(selectedReservation.restaurant_id) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Date:</span>
                  <span class="detail-value">{{ formatDate(selectedReservation.time) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Time:</span>
                  <span class="detail-value">{{ formatTime(selectedReservation.time) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Party Size:</span>
                  <span class="detail-value">{{ selectedReservation.count }} people</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Status:</span>
                  <span class="detail-value">
                    <span 
                      class="badge"
                      :class="getStatusClass(selectedReservation.status)"
                    >
                      {{ selectedReservation.status }}
                    </span>
                  </span>
                </div>
                <div class="detail-item" v-if="selectedReservation.table_no">
                  <span class="detail-label">Table Number:</span>
                  <span class="detail-value">{{ selectedReservation.table_no }}</span>
                </div>
                <div class="detail-item" v-if="selectedReservation.price">
                  <span class="detail-label">Estimated Price:</span>
                  <span class="detail-value">${{ selectedReservation.price.toFixed(2) }}</span>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
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
  import { getUserReservations, getAllRestaurants } from '@/services/restaurantService';
  
  export default {
    name: 'CustomerReservations',
    setup() {
      const router = useRouter();
      const user = ref(null);
      const reservations = ref([]);
      const restaurants = ref([]);
      const isLoading = ref(true);
      const errorMessage = ref('');
      const selectedReservation = ref(null);
      const reservationModal = ref(null);
      
      // Load data when component mounts
      onMounted(async () => {
        try {
          // Initialize Bootstrap modal
          if (typeof bootstrap !== 'undefined') {
            reservationModal.value = new bootstrap.Modal(document.getElementById('reservationModal'));
          }
          
          await loadUserData();
          await loadRestaurants();
          await loadReservations();
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
      
      // Load user's reservations
      const loadReservations = async () => {
        try {
          if (!user.value || !user.value.id) return;
          
          const userReservations = await getUserReservations(user.value.id);
          reservations.value = userReservations;
        } catch (error) {
          console.error('Error loading reservations:', error);
          errorMessage.value = 'Failed to load your reservations. Please try again later.';
          throw error;
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
      
      // Get CSS class for status badge
      const getStatusClass = (status) => {
        switch (status) {
          case 'Booked':
            return 'bg-primary';
          case 'Confirmed':
            return 'bg-success';
          case 'Cancelled':
            return 'bg-danger';
          case 'Completed':
            return 'bg-info';
          default:
            return 'bg-secondary';
        }
      };
      
      // Show reservation details
      const viewReservation = (reservation) => {
        selectedReservation.value = reservation;
        reservationModal.value.show();
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
        reservations,
        isLoading,
        errorMessage,
        selectedReservation,
        formatDate,
        formatTime,
        getRestaurantName,
        getStatusClass,
        viewReservation,
        logout
      };
    }
  };
  </script>
  
  <style scoped>
  .reservation-details {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .detail-item {
    display: flex;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 10px;
  }
  
  .detail-label {
    font-weight: 600;
    width: 40%;
    color: #555;
  }
  
  .detail-value {
    width: 60%;
  }
  
  .badge {
    padding: 6px 10px;
  }
  </style>