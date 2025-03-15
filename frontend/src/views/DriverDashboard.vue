// DriverDashboard.vue
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
                <span v-if="user">{{ user.driverName }}</span>
                <span v-else>Loading...</span>
              </button>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                <li><router-link class="dropdown-item" to="/driver-profile"><i class="fas fa-user-cog"></i> My Profile</router-link></li>
                <li><router-link class="dropdown-item" to="/driver-deliveries"><i class="fas fa-history"></i> Delivery History</router-link></li>
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
              <h2>Welcome, <span v-if="user">{{ user.driverName }}</span><span v-else>Driver</span>!</h2>
              <p>Ready to make some deliveries today?</p>
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
          <!-- Driver Stats -->
          <div class="row mb-4">
            <div class="col-md-4 col-sm-6 mb-3" v-for="(stat, index) in driverStats" :key="index">
              <div class="stat-card">
                <div class="stat-icon">
                  <i :class="stat.icon"></i>
                </div>
                <div class="stat-content">
                  <h4>{{ stat.title }}</h4>
                  <p class="stat-value">{{ stat.value }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- New Delivery Requests -->
          <div class="row mb-4">
            <div class="col-12">
              <h3 class="section-heading">New Delivery Requests</h3>
            </div>
            <div class="col-12">
              <div class="empty-state">
                <i class="fas fa-route"></i>
                <p>No new delivery requests at the moment.</p>
                <small>New requests will appear here when available.</small>
              </div>
            </div>
          </div>
          
          <!-- Active Deliveries -->
          <div class="row mb-4">
            <div class="col-12">
              <h3 class="section-heading">Active Deliveries</h3>
            </div>
            <div class="col-12">
              <div class="empty-state">
                <i class="fas fa-motorcycle"></i>
                <p>No active deliveries.</p>
                <small>Active deliveries will be shown here.</small>
              </div>
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
  name: 'DriverDashboard',
  setup() {
    const router = useRouter();
    const user = ref(null);
    const isLoading = ref(true);
    const errorMessage = ref('');
    
    const driverStats = [
      {
        icon: 'fas fa-truck',
        title: 'Today\'s Deliveries',
        value: '0'
      },
      {
        icon: 'fas fa-dollar-sign',
        title: 'Today\'s Earnings',
        value: '$0.00'
      },
      {
        icon: 'fas fa-star',
        title: 'Rating',
        value: 'N/A'
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
        
        // Check if user is driver type
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
        
        if (userTypeData.user_type !== 'driver') {
          console.log('User is not a driver, redirecting to customer dashboard');
          // Wrong user type, redirect to appropriate dashboard
          router.push('/customer-dashboard');
          return;
        }
        
        console.log('Fetching driver profile data');
        
        // Get driver profile data
        const { data: profileData, error: profileError } = await supabaseClient
          .from('driver_profiles')
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
          driverName: profileData.driver_name,
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
      driverStats,
      logout
    };
  }
};
</script>