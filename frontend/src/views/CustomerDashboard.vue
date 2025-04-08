<template>
  <div>
    <!-- Dashboard Header -->
    <div class="dashboard-header">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <router-link to="/" class="dashboard-logo">
            <span>FeastFinder</span>
          </router-link>
          <div class="dashboard-user d-flex align-items-center">
            <!-- Notification Bell Icon -->
            <div class="position-relative me-3" v-if="hasPendingReservation">
              <router-link to="/accept-booking" class="notification-bell">
                <i class="fas fa-bell text-warning"></i>
                <span class="notification-badge"></span>
              </router-link>
            </div>
            <div class="dropdown">
              <button class="btn dropdown-toggle" type="button" id="userDropdown" @click="toggleDropdown">
                <i class="fas fa-user-circle"></i>
                <span v-if="user">{{ user.customerName }}</span>
                <span v-else>Loading...</span>
              </button>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                <!-- reservation pg-->
                <li><router-link class="dropdown-item" to="/reservations"><i class="fas fa-receipt"></i> My Orders</router-link></li>
                <li><router-link class="dropdown-item" to="/reservations"><i class="fas fa-calendar-check"></i> My Reservations</router-link></li>
                <li v-if="hasPendingReservation"><router-link class="dropdown-item text-warning" to="/accept-booking"><i class="fas fa-bell"></i> Pending Table Offer</router-link></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click.prevent="logout"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Dashboard Content -->
    <div class="dashboard-container">
      <div class="container">
        <!-- Welcome Message -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="welcome-card">
              <h2>Welcome, <span v-if="user">{{ user.customerName }}</span><span v-else>Customer</span>!</h2>
              <p>What would you like to eat today?</p>
              <!-- Pending Reservation Alert -->
              <div v-if="hasPendingReservation" class="alert alert-warning mt-3">
                <i class="fas fa-bell me-2"></i> You have a pending table offer! 
                <router-link to="/accept-booking" class="alert-link">View details</router-link>
              </div>
            </div>
          </div>
        </div>
                
        <!-- Quick Actions -->
        <div class="row mb-4">
          <div class="col-12">
            <h3 class="section-heading">Quick Actions</h3>
          </div>
          <div class="col-md-3 col-sm-6 mb-3" v-for="(action, index) in quickActions" :key="index">
            <div class="action-card">
              <div class="action-icon">
                <i :class="action.icon"></i>
              </div>
              <h4>{{ action.title }}</h4>
              <router-link :to="action.link" class="action-link" @click="action.orderType">{{ action.linkText }}</router-link>
            </div>
          </div>
        </div>
        
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-container">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p>Loading your data...</p>
        </div>
        
        <!-- Error Message -->
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
          {{ errorMessage }}
        </div>
        
        <!-- Content shown only when data is loaded -->
        <div v-if="!isLoading && !errorMessage">
          <!-- Featured Restaurants -->
          <div class="row mb-4">
            <div class="col-12">
              <h3 class="section-heading">Featured Restaurants</h3>
              <p class="section-subheading">Popular places to order from</p>
            </div>
            <!-- Restaurants would be loaded here -->
            <div class="col-12 text-center">
              <p>More restaurants coming soon!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { supabaseClient, signOut } from '@/services/supabase';
import { checkPendingReservations } from '@/services/reservationService';

const setOrderType = async (type) => {
  // Store order_type in localStorage for temporary use
  localStorage.setItem('orderType', type);
}

export default {
  name: 'CustomerDashboard',
  setup() {
    const router = useRouter();
    const user = ref(null);
    const isLoading = ref(true);
    const errorMessage = ref('');
    const searchQuery = ref('');
    const hasPendingReservation = ref(false);
    
    const quickActions = [
      {
        icon: 'fas fa-calendar-check',
        title: 'Book a Table',
        link: '/restaurants',
        linkText: 'Find Restaurants',
        orderType: () => setOrderType('dine_in')
      },
      {
        icon: 'fas fa-list-alt',
        title: 'View My Table Reservations',
        link: '/reservations',
        linkText: 'See Table Bookings'
      },
      // yet to change link
      {
        icon: 'fas fa-utensils',
        title: 'Order Food for Delivery',
        link: '/restaurants',
        linkText: 'Browse Restaurants',
        orderType: () => setOrderType('delivery')
      },
      // yet to change link
      {
        icon: 'fas fa-list-alt',
        title: 'View My Home Delivery Orders',
        link: '/reservations',
        linkText: 'See Delivery Orders'
      }
    ];
    
    // toggle dropdown manually
    const toggleDropdown = (event) => {
      const dropdownMenu = event.target.closest('.dropdown').querySelector('.dropdown-menu');
      dropdownMenu.classList.toggle('show');
    };
    
    // Load user data when component mounts
    onMounted(async () => {
      try {
        // First check if user is logged in
        const { data: sessionData, error: sessionError } = await supabaseClient.auth.getSession();
        
        if (sessionError) {
          console.error('Session error:', sessionError);
          throw sessionError;
        }
        
        if (!sessionData.session) {
          console.log('No active session found, redirecting to login');
          // Not logged in, redirect to login
          router.push('/login');
          return;
        }
        
        console.log('Session found, checking user type');
        
        // Check if user is customer type
        const { data: userTypeData, error: userTypeError } = await supabaseClient
          .from('user_types')
          .select('user_type')
          .eq('user_id', sessionData.session.user.id)
          .single();
          
        if (userTypeError) {
          console.error('Error fetching user type:', userTypeError);
          throw userTypeError;
        }
        
        console.log('User type:', userTypeData.user_type);
        
        if (userTypeData.user_type !== 'customer') {
          console.log('User is not a customer, redirecting to driver dashboard');
          // Wrong user type, redirect to appropriate dashboard
          router.push('/driver-dashboard');
          return;
        }
        
        console.log('Fetching customer profile data');
        
        // Get customer profile data
        const { data: profileData, error: profileError } = await supabaseClient
          .from('customer_profiles')
          .select('*')
          .eq('id', sessionData.session.user.id)
          .single();
        
        if (profileError) {
          console.error('Error fetching profile data:', profileError);
          throw profileError;
        }
        
        console.log('Profile data retrieved:', profileData);
        
        // Update user ref with profile data
        user.value = {
          customerName: profileData.customer_name,
          phoneNumber: profileData.phone_number,
          streetAddress: profileData.street_address,
          postalCode: profileData.postal_code,
          id: profileData.id
        };
        
        // Store user information in localStorage for other components
        localStorage.setItem('user_id', profileData.id);
        localStorage.setItem('user_name', profileData.customer_name);
        localStorage.setItem('user_phone', profileData.phone_number);
        
        console.log('User data loaded successfully');
        
        // Check for pending reservations
        try {
          const pendingReservations = await checkPendingReservations(profileData.id);
          hasPendingReservation.value = pendingReservations.length > 0;
          
          if (hasPendingReservation.value) {
            // Store pending reservation in localStorage for the accept booking page
            localStorage.setItem('pendingReservation', JSON.stringify(pendingReservations[0]));
          }
        } catch (error) {
          console.error('Error checking pending reservations:', error);
          // Non-critical error, continue loading dashboard
        }
      } catch (error) {
        console.error('Error loading user data:', error);
        errorMessage.value = 'Failed to load user data. Please try again.';
      } finally {
        isLoading.value = false;
      }
    });
    
    // Logout function
    const logout = async () => {
      try {
        isLoading.value = true;
        console.log('Logging out...');
        
        const { error } = await signOut();
        if (error) {
          console.error('Logout error:', error);
          throw error;
        }
        
        // Clear any stored user data
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_phone');
        localStorage.removeItem('pendingReservation');
        
        console.log('Logout successful, redirecting to home');
        // Redirect to home page after logout
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
      isLoading,
      errorMessage,
      searchQuery,
      quickActions,
      hasPendingReservation,
      logout,
      toggleDropdown
    };
  }
};
</script>

<style scoped>
.notification-bell {
  font-size: 1.5rem;
  color: #ffc107;
  display: block;
  position: relative;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #dc3545;
  display: block;
}
</style>