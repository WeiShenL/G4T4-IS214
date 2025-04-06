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
      
      <!-- Accept Booking Content -->
      <div class="dashboard-container">
        <div class="container">
          <div class="row justify-content-center">
            <div class="col-lg-8">
              <!-- Page Title -->
              <div class="welcome-card mb-4">
                <h2>Table Offer Available!</h2>
                <p>Someone has cancelled their reservation and you're next in the waitlist</p>
              </div>
              
              <!-- Loading State -->
              <div v-if="isLoading" class="loading-container">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p>Loading table details...</p>
              </div>
              
              <!-- Error Message -->
              <div v-if="errorMessage" class="alert alert-danger" role="alert">
                {{ errorMessage }}
              </div>
              
              <!-- Success Message -->
              <div v-if="bookingAccepted" class="card mb-4">
                <div class="card-body text-center p-5">
                  <div class="mb-4">
                    <i class="fas fa-check-circle text-success fa-4x"></i>
                  </div>
                  <h3 class="mb-3">Table Booked Successfully!</h3>
                  <p class="mb-4">Your reservation has been confirmed. We look forward to seeing you soon!</p>
                  <div class="d-flex justify-content-center">
                    <router-link to="/reservations" class="btn btn-primary me-2">
                      <i class="fas fa-calendar-check me-2"></i>View My Reservations
                    </router-link>
                    <router-link to="/customer-dashboard" class="btn btn-outline-primary">
                      <i class="fas fa-home me-2"></i>Back to Dashboard
                    </router-link>
                  </div>
                </div>
              </div>
              
              <!-- Booking Offer Details -->
              <div v-if="!isLoading && !bookingAccepted && reservation" class="card mb-4">
                <div class="card-header bg-warning text-dark">
                  <h3 class="mb-0"><i class="fas fa-exclamation-circle me-2"></i>Limited Time Offer</h3>
                </div>
                <div class="card-body">
                  <div class="reservation-details">
                    <div class="row mb-4">
                      <div class="col-md-6">
                        <div class="detail-item">
                          <span class="detail-label">Restaurant:</span>
                          <span class="detail-value">{{ restaurantName }}</span>
                        </div>
                        <div class="detail-item">
                          <span class="detail-label">Table Number:</span>
                          <span class="detail-value">{{ reservation.table_no }}</span>
                        </div>
                        <div class="detail-item">
                          <span class="detail-label">Date:</span>
                          <span class="detail-value">{{ formatDate(reservation.time) }}</span>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="detail-item">
                          <span class="detail-label">Time:</span>
                          <span class="detail-value">{{ formatTime(reservation.time) }}</span>
                        </div>
                        <div class="detail-item">
                          <span class="detail-label">Status:</span>
                          <span class="detail-value status-badge status-pending">{{ reservation.status }}</span>
                        </div>
                        <div class="detail-item">
                          <span class="detail-label">Offer Expires:</span>
                          <span class="detail-value text-danger">{{ offerExpiryTime }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div class="alert alert-info mb-4">
                      <i class="fas fa-info-circle me-2"></i>
                      <strong>This offer is available only for you!</strong> Someone cancelled their reservation and you are next in line on our waitlist. This table will be held for you for a limited time only.
                    </div>
                    
                    <!-- Order Form -->
                    <h4 class="mb-3">Pre-Order Options</h4>
                    <div class="row mb-3">
                      <div class="col-md-6">
                        <div class="form-group mb-3">
                          <label for="partySize" class="form-label">Number of People</label>
                          <input 
                            type="number" 
                            class="form-control" 
                            id="partySize" 
                            v-model="partySize" 
                            min="1" 
                            max="20" 
                            required
                          >
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="form-group mb-3">
                          <label for="menuItem" class="form-label">Pre-Order Item (Optional)</label>
                          <select class="form-select" id="menuItem" v-model="selectedMenuItem">
                            <option value="">Select an item (optional)</option>
                            <option v-for="item in menuItems" :key="item.menu_id" :value="item">
                              {{ item.item_name }} (${{ Number(item.price).toFixed(2) }})
                            </option>
                          </select>
                        </div>
                      </div>
                    </div>
                    
                    <div v-if="selectedMenuItem" class="mb-4">
                      <div class="selected-menu-item p-3 border rounded">
                        <h5>{{ selectedMenuItem.item_name }}</h5>
                        <p class="text-muted mb-2">{{ selectedMenuItem.description || 'No description available' }}</p>
                        
                        <div class="d-flex justify-content-between align-items-center">
                          <div class="quantity-control">
                            <button 
                              class="btn btn-sm btn-outline-secondary" 
                              @click="decreaseQuantity"
                              :disabled="itemQuantity <= 1"
                            >
                              <i class="fas fa-minus"></i>
                            </button>
                            <span class="mx-2">{{ itemQuantity }}</span>
                            <button 
                              class="btn btn-sm btn-outline-secondary" 
                              @click="increaseQuantity"
                            >
                              <i class="fas fa-plus"></i>
                            </button>
                          </div>
                          <div class="item-price font-weight-bold">
                            ${{ (Number(selectedMenuItem.price) * itemQuantity).toFixed(2) }}
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div class="text-center">
                      <div v-if="isAccepting" class="d-flex justify-content-center mb-3">
                        <div class="spinner-border text-primary" role="status">
                          <span class="visually-hidden">Processing...</span>
                        </div>
                      </div>
                      
                      <button 
                        class="btn btn-lg btn-success me-3" 
                        @click="acceptBooking"
                        :disabled="isAccepting || !partySize"
                      >
                        <i class="fas fa-check-circle me-2"></i>
                        Accept & Book This Table
                      </button>
                      
                      <button 
                        class="btn btn-lg btn-outline-danger" 
                        @click="declineBooking"
                        :disabled="isAccepting"
                      >
                        <i class="fas fa-times-circle me-2"></i>
                        Decline Offer
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- No Reservation Available -->
              <div v-if="!isLoading && !reservation && !bookingAccepted" class="card">
                <div class="card-body text-center p-5">
                  <div class="mb-4">
                    <i class="fas fa-exclamation-circle text-warning fa-4x"></i>
                  </div>
                  <h3 class="mb-3">No Table Offers Available</h3>
                  <p class="mb-4">There are currently no table offers available for you. Please check back later or make a new reservation.</p>
                  <div class="d-flex justify-content-center">
                    <router-link to="/restaurants" class="btn btn-primary me-2">
                      <i class="fas fa-utensils me-2"></i>Browse Restaurants
                    </router-link>
                    <router-link to="/customer-dashboard" class="btn btn-outline-primary">
                      <i class="fas fa-home me-2"></i>Back to Dashboard
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, computed } from 'vue';
  import { useRouter } from 'vue-router';
  import { getCurrentUser, signOut } from '@/services/supabase';
  import { getRestaurantById } from '@/services/restaurantService';
  import { getRestaurantMenu } from '@/services/menuService';
  import { acceptReallocation, declineReallocation } from '@/services/reservationService';
  
  export default {
    name: 'AcceptBooking',
    setup() {
      const router = useRouter();
      const user = ref(null);
      const reservation = ref(null);
      const restaurantData = ref(null);
      const restaurantName = ref('');
      const menuItems = ref([]);
      const selectedMenuItem = ref(null);
      const itemQuantity = ref(1);
      const partySize = ref(2); // Default to 2 people
      const isLoading = ref(true);
      const isAccepting = ref(false);
      const errorMessage = ref('');
      const bookingAccepted = ref(false);
      const offerExpiryTime = ref('15:00');
      
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
      
      // Calculate order total if menu item is selected
      const orderTotal = computed(() => {
        if (selectedMenuItem.value) {
          return (Number(selectedMenuItem.value.price) * itemQuantity.value).toFixed(2);
        }
        return '0.00';
      });
      
      // Load data when component mounts
      onMounted(async () => {
        try {
          // Load user data
          await loadUserData();
          
          // Check for pending reservation
          const pendingReservationStr = localStorage.getItem('pendingReservation');
          if (pendingReservationStr) {
            reservation.value = JSON.parse(pendingReservationStr);
            
            // Get restaurant data
            if (reservation.value.restaurant_id) {
              await loadRestaurantData(reservation.value.restaurant_id);
            }
            
            // Set expiry time (example: 30 minutes from now)
            const expiryDate = new Date();
            expiryDate.setMinutes(expiryDate.getMinutes() + 30);
            offerExpiryTime.value = expiryDate.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            });
          }
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
          
          // Try to get from localStorage first
          const userName = localStorage.getItem('user_name');
          const userPhone = localStorage.getItem('user_phone');
          const userId = localStorage.getItem('user_id');
          
          if (userName && userPhone && userId) {
            user.value = {
              id: userId,
              customerName: userName,
              phoneNumber: userPhone
            };
            return;
          }
          
          // If not in localStorage, fetch from Supabase
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
            id: profileData.id
          };
          
          // Store user information in localStorage
          localStorage.setItem('user_id', profileData.id);
          localStorage.setItem('user_name', profileData.customer_name);
          localStorage.setItem('user_phone', profileData.phone_number);
        } catch (error) {
          console.error('Error loading user data:', error);
          throw error;
        }
      };
      
      // Load restaurant data and menu
      const loadRestaurantData = async (restaurantId) => {
        try {
          // Get restaurant details
          restaurantData.value = await getRestaurantById(restaurantId);
          if (restaurantData.value) {
            restaurantName.value = restaurantData.value.name;
          } else {
            restaurantName.value = `Restaurant #${restaurantId}`;
          }
          
          // Get menu items
          const menuData = await getRestaurantMenu(restaurantId);
          menuItems.value = menuData;
        } catch (error) {
          console.error('Error loading restaurant data:', error);
          // Non-critical error, continue loading page
          restaurantName.value = `Restaurant #${restaurantId}`;
        }
      };
      
      // Increase item quantity
      const increaseQuantity = () => {
        itemQuantity.value++;
      };
      
      // Decrease item quantity
      const decreaseQuantity = () => {
        if (itemQuantity.value > 1) {
          itemQuantity.value--;
        }
      };
      
      // Accept booking
      const acceptBooking = async () => {
        if (isAccepting.value) return;
        
        try {
          isAccepting.value = true;
          errorMessage.value = '';
          
          if (!partySize.value) {
            errorMessage.value = 'Please specify the number of people for your reservation';
            isAccepting.value = false;
            return;
          }
          
          // Prepare the data for accepting the reservation
          const acceptData = {
            reservation_id: reservation.value.reservation_id,
            user_id: user.value.id,
            party_size: partySize.value,
            menu_item: selectedMenuItem.value ? {
              menu_id: selectedMenuItem.value.menu_id,
              item_name: selectedMenuItem.value.item_name,
              price: selectedMenuItem.value.price,
              quantity: itemQuantity.value
            } : null
          };
          
          console.log('Accepting reservation with data:', acceptData);
          
          // Call the API to accept the reservation
          const result = await acceptReallocation(reservation.value.reservation_id, acceptData);
          
          // Handle successful acceptance
          bookingAccepted.value = true;
          
          // Clear the pending reservation from localStorage
          localStorage.removeItem('pendingReservation');
          
          // Redirect to dashboard after 3 seconds
          setTimeout(() => {
            router.push('/customer-dashboard');
          }, 3000);
          
        } catch (error) {
          console.error('Error accepting booking:', error);
          errorMessage.value = error.message || 'Failed to accept booking. Please try again.';
        } finally {
          isAccepting.value = false;
        }
      };
      
      // Decline booking
      const declineBooking = async () => {
        try {
          if (confirm('Are you sure you want to decline this table offer?')) {
            isLoading.value = true;
            
            // Call the API to decline the reservation
            await declineReallocation(reservation.value.reservation_id);
            
            // Clear the pending reservation and redirect to dashboard
            localStorage.removeItem('pendingReservation');
            router.push('/customer-dashboard');
          }
        } catch (error) {
          console.error('Error declining booking:', error);
          errorMessage.value = error.message || 'Failed to decline booking. Please try again.';
          isLoading.value = false;
        }
      };
        // Logout function
        const logout = async () => {
            try {
                isLoading.value = true;
                await signOut();
                
                // Clear any stored user data
                localStorage.removeItem('user_id');
                localStorage.removeItem('user_name');
                localStorage.removeItem('user_phone');
                localStorage.removeItem('pendingReservation');
                
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
            reservation,
            restaurantName,
            menuItems,
            selectedMenuItem,
            itemQuantity,
            partySize,
            isLoading,
            isAccepting,
            errorMessage,
            bookingAccepted,
            offerExpiryTime,
            orderTotal,
            formatDate,
            formatTime,
            increaseQuantity,
            decreaseQuantity,
            acceptBooking,
            declineBooking,
            logout
            };
        }
        };
        </script>

    <style scoped>
        .detail-item {
        margin-bottom: 15px;
        }

        .detail-label {
        display: block;
        font-weight: 600;
        color: #6c757d;
        font-size: 0.9rem;
        }

        .detail-value {
        font-size: 1.1rem;
        color: var(--dark-color);
        }

        .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        }

        .status-pending {
        background-color: rgba(255, 193, 7, 0.1);
        color: #ffc107;
        }

        .selected-menu-item {
        background-color: rgba(240, 90, 40, 0.05);
        }

        .quantity-control {
        display: flex;
        align-items: center;
        }

        .quantity-control .btn {
        width: 30px;
        height: 30px;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        }
    </style>