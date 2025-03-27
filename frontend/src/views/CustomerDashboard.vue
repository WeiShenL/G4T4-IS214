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
    
    <!-- Dashboard Content -->
    <div class="dashboard-container">
      <div class="container">
        <!-- Welcome Message -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="welcome-card">
              <h2>Welcome, <span v-if="user">{{ user.customerName }}</span><span v-else>Customer</span>!</h2>
              <p>What would you like to eat today?</p>
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
                placeholder="Search for restaurants or cuisine..."
              >
              <button class="search-btn">
                <i class="fas fa-search"></i> Search
              </button>
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
              <router-link :to="action.link" class="action-link">{{ action.linkText }}</router-link>
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

export default {
  name: 'CustomerDashboard',
  setup() {
    const router = useRouter();
    const user = ref(null);
    const isLoading = ref(true);
    const errorMessage = ref('');
    const searchQuery = ref('');
    
    const quickActions = [
      {
        icon: 'fas fa-calendar-check',
        title: 'Book a Table',
        link: '/restaurants',
        linkText: 'Find Restaurants'
      },
      {
        icon: 'fas fa-list-alt',
        title: 'View My Reservations',
        link: '/reservations',
        linkText: 'See Bookings'
      },
      // yet to change 
      {
        icon: 'fas fa-utensils',
        title: 'Order Food for Delivery',
        link: '/restaurants',
        linkText: 'Browse Restaurants'
      },
      // placeholder pg
      {
        icon: 'fas fa-star',
        title: 'Favorites',
        link: '/favorites',
        linkText: 'Your Favorite Places'
      }
    ];
    
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
        
        console.log('User data loaded successfully');
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
      logout
    };
  }
};
</script>