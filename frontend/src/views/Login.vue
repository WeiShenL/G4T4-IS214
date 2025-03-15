<template>
  <div class="login-body">
    <div class="login-container">
      <router-link to="/" class="back-to-home">
        <i class="fas fa-arrow-left"></i> Back to Home
      </router-link>
      
      <div class="login-card">
        <div class="login-header">
          <div class="login-logo">
            <i class="fas fa-utensils"></i>
          </div>
          <h1 class="login-title">Welcome back</h1>
          <p class="login-subtitle">Sign in to continue to FeastFinder</p>
        </div>
        
        <div class="user-type-selector">
          <div 
            class="user-type" 
            :class="{ 'active': userType === 'customer' }"
            @click="userType = 'customer'"
          >
            Customer
          </div>
          <div 
            class="user-type" 
            :class="{ 'active': userType === 'driver' }"
            @click="userType = 'driver'"
          >
            Delivery Partner
          </div>
        </div>
        
        <!-- Success Message -->
        <div v-if="successMessage" class="alert alert-success mb-3" role="alert">
          {{ successMessage }}
        </div>
        
        <!-- Error Alert -->
        <div v-if="errorMessage" class="alert alert-danger mb-3" role="alert">
          {{ errorMessage }}
        </div>
        
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="email" class="form-label">Email</label>
            <input 
              type="email" 
              id="email" 
              class="form-control" 
              v-model="email" 
              placeholder="Enter your email" 
              required
            >
          </div>
          
          <div class="form-group">
            <label for="password" class="form-label">Password</label>
            <div class="password-field">
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password" 
                class="form-control" 
                v-model="password" 
                placeholder="Enter your password" 
                required
              >
              <span class="password-toggle" @click="togglePassword">
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </span>
            </div>
          </div>
          
          <div class="d-flex justify-content-between mb-3">
            <div class="form-check">
              <input 
                type="checkbox" 
                class="form-check-input" 
                id="rememberMe" 
                v-model="rememberMe"
              >
              <label class="form-check-label" for="rememberMe">Remember me</label>
            </div>
            <router-link to="/forgot-password" class="forgotten-password">Forgot password?</router-link>
          </div>
          
          <button type="submit" class="login-btn" :disabled="isLoading">
            <span v-if="isLoading">
              <i class="fas fa-spinner fa-spin"></i> Signing In...
            </span>
            <span v-else>
              <i class="fas fa-sign-in-alt"></i> Sign In
            </span>
          </button>
        </form>
        
        <div class="divider">
          <span>or continue with</span>
        </div>
        
        <div class="social-login">
          <a href="#" class="social-btn" @click.prevent="socialLogin('google')">
            <i class="fab fa-google"></i> Google
          </a>
          <a href="#" class="social-btn" @click.prevent="socialLogin('facebook')">
            <i class="fab fa-facebook-f"></i> Facebook
          </a>
        </div>
        
        <div class="signup-link">
          Don't have an account? <router-link to="/signup">Sign up</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { signIn, getCurrentUser, getUserType } from '@/services/supabase';

export default {
  name: 'Login',
  setup() {
    const router = useRouter();
    const route = useRoute();
    
    const email = ref('');
    const password = ref('');
    const rememberMe = ref(false);
    const showPassword = ref(false);
    const userType = ref('customer');
    const errorMessage = ref('');
    const successMessage = ref('');
    const isLoading = ref(false);
    
    // Check for success message from signup and user type from query parameter
    onMounted(() => {
      window.scrollTo({
        top: 0,
        behavior: 'auto' // Using 'auto' instead of 'smooth' to avoid visible scrolling
      });
      if (route.query.signup === 'success') {
        successMessage.value = 'Account created successfully! Please log in.';
      }
      
      // Set user type based on query parameter
      if (route.query.type === 'driver') {
        userType.value = 'driver';
      }
      
      // Check if user is already logged in
      checkExistingSession();
    });
    
    const checkExistingSession = async () => {
      try {
        const user = await getCurrentUser();
        if (user) {
          // User is already logged in, redirect to appropriate dashboard
          redirectLoggedInUser(user.id);
        }
      } catch (error) {
        console.error('Session check error:', error);
      }
    };
    
    const togglePassword = () => {
      showPassword.value = !showPassword.value;
    };
    
    const login = async () => {
      try {
        isLoading.value = true;
        errorMessage.value = '';
        
        console.log('Attempting login with:', email.value, password.value);
        
        // Sign in with Supabase
        const { data, error } = await signIn(email.value, password.value);
        
        if (error) throw error;
        
        console.log('Login successful, checking user type...');
        
        // Check user type
        const userTypeValue = await getUserType(data.user.id);
        
        if (!userTypeValue) {
          throw new Error('Unable to determine user type');
        }
        
        console.log('User type:', userTypeValue);
        
        // Verify user is logging in with correct account type
        if (userTypeValue !== userType.value) {
          throw new Error(`This account is registered as a ${userTypeValue}. Please select the correct account type.`);
        }
        
        // Redirect based on user type
        if (userTypeValue === 'customer') {
          router.push('/customer-dashboard');
        } else if (userTypeValue === 'driver') {
          router.push('/driver-dashboard');
        }
      } catch (error) {
        console.error('Login error:', error);
        errorMessage.value = error.message || 'Failed to log in. Please check your credentials.';
      } finally {
        isLoading.value = false;
      }
    };
    
    const socialLogin = async (provider) => {
      alert(`Social login with ${provider} will be implemented in a future update.`);
    };
    
    // Helper function to redirect logged in users
    const redirectLoggedInUser = async (userId) => {
      try {
        const userTypeValue = await getUserType(userId);
        
        if (userTypeValue === 'customer') {
          router.push('/customer-dashboard');
        } else if (userTypeValue === 'driver') {
          router.push('/driver-dashboard');
        }
      } catch (error) {
        console.error('Redirect error:', error);
        errorMessage.value = 'Error determining user type. Please try again.';
      }
    };
    
    return {
      email,
      password,
      rememberMe,
      showPassword,
      userType,
      errorMessage,
      successMessage,
      isLoading,
      togglePassword,
      login,
      socialLogin
    };
  }
};
</script>