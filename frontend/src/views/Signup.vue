<template>
  <div class="login-body">
    <div class="login-container">
      <router-link to="/" class="back-to-home">
        <i class="fas fa-arrow-left"></i> Back to Home
      </router-link>
      
      <div class="login-card signup-card">
        <div class="login-header">
          <div class="login-logo">
            <i class="fas fa-utensils"></i>
          </div>
          <h1 class="login-title">Create an Account</h1>
          <p class="login-subtitle">Join FeastFinder today</p>
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
        
        <!-- Error Alert -->
        <div v-if="errorMessage" class="alert alert-danger mb-3" role="alert">
          {{ errorMessage }}
        </div>
        
        <!-- Success Alert -->
        <div v-if="successMessage" class="alert alert-success mb-3" role="alert">
          {{ successMessage }}
        </div>
        
        <form @submit.prevent="signup">
          <div class="form-group">
            <label for="name" class="form-label">Full Name</label>
            <input 
              type="text" 
              id="name" 
              class="form-control" 
              v-model="name" 
              placeholder="Enter your full name" 
              required
            >
          </div>
          
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
            <label for="phone" class="form-label">Phone Number</label>
            <input 
              type="tel" 
              id="phone" 
              class="form-control" 
              v-model="phone" 
              placeholder="Enter your phone number" 
              required
            >
          </div>
          
          <div class="form-group">
            <label for="address" class="form-label">Street Address</label>
            <input 
              type="text" 
              id="address" 
              class="form-control" 
              v-model="address" 
              placeholder="Enter your street address" 
              required
            >
          </div>
          
          <div class="form-group">
            <label for="postalCode" class="form-label">Postal Code</label>
            <input 
              type="number" 
              id="postalCode" 
              class="form-control" 
              v-model="postalCode" 
              placeholder="Enter your postal code" 
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
                placeholder="Create a password" 
                required
              >
              <span class="password-toggle" @click="togglePassword">
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </span>
            </div>
            <small class="form-text text-muted">
              Password must be at least 6 characters long
            </small> 
          </div>
          
          <div class="form-group">
            <label for="confirmPassword" class="form-label">Confirm Password</label>
            <div class="password-field">
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="confirmPassword" 
                class="form-control" 
                v-model="confirmPassword" 
                placeholder="Confirm your password" 
                required
              >
            </div>
          </div>
          
          <button type="submit" class="login-btn" :disabled="isLoading">
            <span v-if="isLoading">
              <i class="fas fa-spinner fa-spin"></i> Creating Account...
            </span>
            <span v-else>
              <i class="fas fa-user-plus"></i> Sign Up
            </span>
          </button>
        </form>
        
        <div class="divider">
          <span>or sign up with</span>
        </div>
        
        <div class="social-login">
          <a href="#" class="social-btn" @click.prevent="socialSignup('google')">
            <i class="fab fa-google"></i> Google
          </a>
          <a href="#" class="social-btn" @click.prevent="socialSignup('facebook')">
            <i class="fab fa-facebook-f"></i> Facebook
          </a>
        </div>
        
        <div class="signup-link">
          Already have an account? <router-link to="/login">Log in</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'; // Add onMounted
import { useRouter, useRoute } from 'vue-router';
import { signUp } from '@/services/supabase';

export default {
  name: 'Signup',
  setup() {
    const router = useRouter();
    const route = useRoute(); // Make sure this is added
    
    const name = ref('');
    const email = ref('');
    const phone = ref('');
    const address = ref('');
    const postalCode = ref('');
    const password = ref('');
    const confirmPassword = ref('');
    const userType = ref('customer'); // Default is customer
    const showPassword = ref(false);
    const errorMessage = ref('');
    const successMessage = ref('');
    const isLoading = ref(false);
    
    // Add this onMounted hook to check the query parameter
    onMounted(() => {
      window.scrollTo({
        top: 0,
        behavior: 'auto' // Using 'auto' instead of 'smooth' to avoid visible scrolling
      });
      // Check if 'type' query parameter exists and set userType accordingly
      if (route.query.type === 'driver') {
        userType.value = 'driver';
      }
      
    });
    
    const togglePassword = () => {
      showPassword.value = !showPassword.value;
    };
    
    const validateForm = () => {
      if (password.value !== confirmPassword.value) {
        errorMessage.value = 'Passwords do not match';
        return false;
      }
      
      if (password.value.length < 6) {
        errorMessage.value = 'Password must be at least 6 characters long';
        return false;
      }
      
      if (!/^\d+$/.test(phone.value)) {
        errorMessage.value = 'Phone number should contain only digits';
        return false;
      }
      
      if (!/^\d+$/.test(postalCode.value)) {
        errorMessage.value = 'Postal code should contain only digits';
        return false;
      }
      
      return true;
    };
    
    const signup = async () => {
      if (!validateForm()) return;
      
      try {
        isLoading.value = true;
        errorMessage.value = '';
        
        // Create user data object
        const userData = {
          name: name.value,
          phone: phone.value,
          address: address.value,
          postal_code: postalCode.value,
          user_type: userType.value
        };
        
        // Sign up the user
        await signUp(email.value, password.value, userData);
        
        // Show success message
        successMessage.value = 'Account created successfully! Redirecting to login...';
        
        // Reset form
        name.value = '';
        email.value = '';
        phone.value = '';
        address.value = '';
        postalCode.value = '';
        password.value = '';
        confirmPassword.value = '';
        
        // Redirect after a short delay
        setTimeout(() => {
          router.push('/login?signup=success');
        }, 2000);
      } catch (error) {
        errorMessage.value = error.message || 'Failed to sign up. Please try again.';
      } finally {
        isLoading.value = false;
      }
    };
  
    const socialSignup = (provider) => {
      alert(`Social signup with ${provider} will be implemented in a future update.`);
    };
    
    return {
      name,
      email,
      phone,
      address,
      postalCode,
      password,
      confirmPassword,
      userType,
      showPassword,
      errorMessage,
      successMessage,
      isLoading,
      togglePassword,
      signup,
      socialSignup
    };
  }
};
</script>