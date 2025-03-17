import { createRouter, createWebHistory } from 'vue-router';

// Import views
import Home from '@/views/Home.vue';
import Login from '@/views/Login.vue';
import Signup from '@/views/Signup.vue';
import CustomerDashboard from '@/views/CustomerDashboard.vue';
import DriverDashboard from '@/views/DriverDashboard.vue';

//driver
import DriverView from '../views/DriverView.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup
  },
  {
    path: '/customer-dashboard',
    name: 'CustomerDashboard',
    component: CustomerDashboard,
    meta: { requiresAuth: true, userType: 'customer' }
  },
  {
    path: '/driver-dashboard',
    name: 'DriverDashboard',
    component: DriverDashboard,
    meta: { requiresAuth: true, userType: 'driver' }
  },
  
  {
    path: '/driver', // Route for the driver's dashboard
    name: 'DriverDashboard',
    component: DriverView,
  },
  
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition){
    // Always scroll to top plz
    return {top: 0}
  }
});

// Navigation guard for authentication
router.beforeEach(async (to, from, next) => {
  // Import supabase client
  const { supabaseClient } = await import('@/services/supabase');
  
  // Check if route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const { data } = await supabaseClient.auth.getSession();
    
    // If no session, redirect to login
    if (!data.session) {
      next({ name: 'Login' });
      return;
    }
    
    // If route requires specific user type
    if (to.meta.userType) {
      try {
        const { data: userData, error } = await supabaseClient
          .from('user_types')
          .select('user_type')
          .eq('user_id', data.session.user.id)
          .single();
          
        if (error || userData.user_type !== to.meta.userType) {
          // Redirect to appropriate dashboard
          if (userData.user_type === 'customer') {
            next({ name: 'CustomerDashboard' });
          } else if (userData.user_type === 'driver') {
            next({ name: 'DriverDashboard' });
          } else {
            next({ name: 'Login' });
          }
          return;
        }
      } catch (error) {
        console.error('Error checking user type:', error);
        next({ name: 'Login' });
        return;
      }
    }
  }
  
  next();
});

export default router;