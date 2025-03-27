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
    
    <!-- Checkout Content -->
    <div class="dashboard-container">
      <div class="container">
        <!-- Page Title -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="welcome-card">
              <h2>Checkout</h2>
              <p>Complete your order</p>
            </div>
          </div>
        </div>
        
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-container">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p>Loading checkout details...</p>
        </div>
        
        <!-- Error Message -->
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
          {{ errorMessage }}
        </div>
        
        <!-- Order Placed Success Message -->
        <div v-if="orderPlaced" class="alert alert-success" role="alert">
          <h4 class="alert-heading">Order Placed Successfully!</h4>
          <p>Your order has been placed and is being processed. Thank you for your purchase!</p>
          <hr>
          <p class="mb-0">Payment ID: {{ paymentId }}</p>
          <div class="mt-3">
            <router-link to="/customer-dashboard" class="btn btn-primary">
              Return to Dashboard
            </router-link>
          </div>
        </div>
        
        <!-- Checkout Content -->
        <div v-if="!isLoading && !orderPlaced && orderInfo" class="row">
          <!-- Order Summary -->
          <div class="col-md-5">
            <div class="card mb-4">
              <div class="card-header">
                <h3 class="mb-0">Order Summary</h3>
              </div>
              <div class="card-body">
                <div class="restaurant-name">
                  <h4>{{ orderInfo.restaurantName }}</h4>
                </div>
                <div class="order-item">
                  <div class="d-flex justify-content-between">
                    <div>
                      <h5>{{ orderInfo.item.name }}</h5>
                      <div class="order-quantity">Quantity: {{ orderInfo.item.quantity }}</div>
                    </div>
                    <div class="order-price">${{ orderInfo.item.price.toFixed(2) }}</div>
                  </div>
                </div>
                <hr>
                <div class="order-subtotal d-flex justify-content-between">
                  <span>Subtotal</span>
                  <span>${{ (orderInfo.item.price * orderInfo.item.quantity).toFixed(2) }}</span>
                </div>
                <div class="order-tax d-flex justify-content-between">
                  <span>Tax (8%)</span>
                  <span>${{ calculateTax().toFixed(2) }}</span>
                </div>
                <div class="order-total d-flex justify-content-between mt-3">
                  <h5>Total</h5>
                  <h5>${{ calculateTotal().toFixed(2) }}</h5>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Delivery Info and Checkout Button -->
          <div class="col-md-7">
            <div class="card">
              <div class="card-header">
                <h3 class="mb-0">Delivery Information</h3>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label for="deliveryAddress" class="form-label">Delivery Address</label>
                  <textarea class="form-control" id="deliveryAddress" v-model="deliveryAddress" rows="2" required></textarea>
                </div>
                
                <div class="mb-3">
                  <label for="deliveryInstructions" class="form-label">Delivery Instructions (Optional)</label>
                  <textarea class="form-control" id="deliveryInstructions" v-model="deliveryInstructions" rows="2" placeholder="E.g., Leave at door, call upon arrival, etc."></textarea>
                </div>
                
                <div v-if="paymentError" class="alert alert-danger mb-3">
                  {{ paymentError }}
                </div>
                
                <div class="stripe-info alert alert-info mb-3">
                  <i class="fas fa-info-circle me-2"></i>
                  When you click "Proceed to Payment", you'll be redirected to Stripe's secure checkout page to complete your payment.
                </div>
                
                <button type="button" class="btn btn-primary w-100" @click="proceedToStripeCheckout" :disabled="isSubmitting || !deliveryAddress">
                  <span v-if="isSubmitting">
                    <i class="fas fa-spinner fa-spin"></i> Processing...
                  </span>
                  <span v-else>
                    <i class="fas fa-credit-card me-2"></i> Proceed to Payment - ${{ calculateTotal().toFixed(2) }}
                  </span>
                </button>
                
                <div class="mt-3 text-center">
                  <small class="text-muted">
                    <i class="fas fa-lock me-1"></i> Secure payment powered by Stripe
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- No Order Info -->
        <div v-if="!isLoading && !orderInfo && !orderPlaced" class="empty-state">
          <i class="fas fa-shopping-cart"></i>
          <p>No order information found.</p>
          <small>Please select items from a restaurant menu first.</small>
          <div class="mt-3">
            <router-link to="/restaurants" class="btn btn-primary">
              Browse Restaurants
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { getCurrentUser, signOut } from '@/services/supabase';
import { createOrder } from '@/services/menuService';
import { initStripe, createCheckoutSession } from '@/services/stripeService';

export default {
  name: 'Checkout',
  setup() {
    const router = useRouter();
    const route = useRoute();
    
    const user = ref(null);
    const orderInfo = ref(null);
    const isLoading = ref(true);
    const errorMessage = ref('');
    const paymentError = ref('');
    const isSubmitting = ref(false);
    const orderPlaced = ref(false);
    const paymentId = ref('');
    const deliveryAddress = ref('');
    const deliveryInstructions = ref('');
    
    // Get restaurant ID from route params
    const restaurantId = parseInt(route.params.id);
    
    // Check if this is a return from Stripe Checkout
    const isReturnFromStripe = computed(() => {
      return route.query.payment_intent && route.query.session_id;
    });
    
    // Load data when component mounts
    onMounted(async () => {
      try {
        // Make sure we have a valid restaurant ID
        if (!restaurantId || isNaN(restaurantId)) {
          throw new Error('Invalid restaurant ID');
        }
        
        // Initialize Stripe
        await initStripe();
        
        // Load user data
        await loadUserData();
        
        // If returning from Stripe, process the payment
        if (isReturnFromStripe.value) {
          await handleStripeReturn();
        } else {
          // Get order info from localStorage
          const storedOrderInfo = localStorage.getItem('orderInfo');
          if (storedOrderInfo) {
            orderInfo.value = JSON.parse(storedOrderInfo);
            
            // Validate that stored order info matches current restaurant
            if (orderInfo.value.restaurantId !== restaurantId) {
              throw new Error('Order information does not match current restaurant');
            }
          }
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
        
        // Set user data
        user.value = {
          id: currentUser.id,
          customerName: currentUser.user_metadata?.name || 'Customer'
        };
        
        // Pre-fill delivery address if available from profile
        if (currentUser.user_metadata?.address) {
          deliveryAddress.value = currentUser.user_metadata.address;
        }
      } catch (error) {
        console.error('Error loading user data:', error);
        throw error;
      }
    };
    
    // Calculate tax
    const calculateTax = () => {
      if (!orderInfo.value) return 0;
      return orderInfo.value.item.total * 0.08; // 8% tax
    };
    
    // Calculate total
    const calculateTotal = () => {
      if (!orderInfo.value) return 0;
      return orderInfo.value.item.total + calculateTax();
    };
    
    // Process payment with Stripe Checkout
    const proceedToStripeCheckout = async () => {
      try {
        if (!orderInfo.value || !user.value) {
          throw new Error('Missing order or user information');
        }
        
        // Validate delivery address
        if (!deliveryAddress.value) {
          paymentError.value = 'Please enter a delivery address';
          return;
        }
        
        isSubmitting.value = true;
        paymentError.value = '';
        
        // Store delivery info in localStorage for after Stripe return
        localStorage.setItem('delivery_address', deliveryAddress.value);
        localStorage.setItem('delivery_instructions', deliveryInstructions.value || '');
        
        // Save the total amount for verification later
        localStorage.setItem('stripe_amount', calculateTotal());
        
        // Prepare order details for Stripe
        const orderDetails = {
          restaurantId: orderInfo.value.restaurantId,
          restaurantName: orderInfo.value.restaurantName,
          itemName: orderInfo.value.item.name,
          quantity: orderInfo.value.item.quantity,
          amount: calculateTotal() * 100, // Stripe uses cents
          currency: 'usd'
        };
        
        // Set up success and cancel URLs
        const currentUrl = window.location.origin;
        const successUrl = `${currentUrl}/checkout/${orderInfo.value.restaurantId}?success=true`;
        const cancelUrl = `${currentUrl}/checkout/${orderInfo.value.restaurantId}?canceled=true`;
        
        console.log('Creating Stripe checkout session...');
        
        // Create a checkout session
        const { sessionId, url } = await createCheckoutSession(
          orderDetails,
          user.value.id,
          successUrl,
          cancelUrl
        );
        
        console.log('Redirecting to Stripe checkout...');
        
        // Redirect to Stripe Checkout
        const { error } = await initStripe().then(stripe => 
          stripe.redirectToCheckout({ sessionId })
        );
        
        if (error) {
          throw new Error(error.message);
        }
      } catch (error) {
        console.error('Error processing payment:', error);
        paymentError.value = error.message || 'Payment initialization failed. Please try again.';
        isSubmitting.value = false;
      }
    };
    
    // Handle return from Stripe
    const handleStripeReturn = async () => {
      try {
        isLoading.value = true;
        
        // Get payment intent ID from query param
        const stripePaymentIntentId = route.query.payment_intent;
        
        if (!stripePaymentIntentId) {
          throw new Error('Invalid payment information');
        }
        
        // Restore order info from localStorage
        const storedOrderInfo = localStorage.getItem('orderInfo');
        if (!storedOrderInfo) {
          throw new Error('Order information not found');
        }
        
        orderInfo.value = JSON.parse(storedOrderInfo);
        
        // Get delivery info from localStorage
        const storedAddress = localStorage.getItem('delivery_address');
        
        if (!storedAddress) {
          throw new Error('Delivery information not found');
        }
        
        // Create the order with payment ID
        const order = {
          user_id: user.value.id,
          restaurant_id: orderInfo.value.restaurantId,
          item_name: orderInfo.value.item.name,
          quantity: orderInfo.value.item.quantity,
          order_price: calculateTotal(),
          payment_id: stripePaymentIntentId
        };
        
        console.log('Creating order with payment ID:', stripePaymentIntentId);
        const result = await createOrder(order);
        
        if (result.success) {
          // Clear order info from localStorage
          localStorage.removeItem('orderInfo');
          localStorage.removeItem('delivery_address');
          localStorage.removeItem('delivery_instructions');
          localStorage.removeItem('stripe_payment_intent_id');
          localStorage.removeItem('stripe_amount');
          
          // Set payment ID for display
          paymentId.value = stripePaymentIntentId;
          
          // Show success message
          orderPlaced.value = true;
          
          // Clear query params from URL without reloading
          const newUrl = window.location.pathname;
          window.history.replaceState({}, document.title, newUrl);
        } else {
          throw new Error('Failed to create order');
        }
      } catch (error) {
        console.error('Error handling Stripe return:', error);
        errorMessage.value = error.message || 'Failed to process your payment. Please contact support.';
      } finally {
        isLoading.value = false;
      }
    };
    
    // Logout function
    const logout = async () => {
      try {
        isLoading.value = true;
        await signOut();
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
      orderInfo,
      isLoading,
      errorMessage,
      paymentError,
      isSubmitting,
      orderPlaced,
      paymentId,
      deliveryAddress,
      deliveryInstructions,
      calculateTax,
      calculateTotal,
      proceedToStripeCheckout,
      logout
    };
  }
};
</script>

<style scoped>
.restaurant-name {
  margin-bottom: 20px;
}

.order-item {
  margin-bottom: 20px;
}

.order-quantity {
  color: #6c757d;
  font-size: 0.9rem;
}

.order-price {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--primary-color);
}

.order-subtotal, .order-tax {
  margin-bottom: 5px;
  color: #6c757d;
}

.order-total {
  font-size: 1.2rem;
  color: var(--dark-color);
  border-top: 1px solid #eee;
  padding-top: 10px;
}

.stripe-info {
  background-color: rgba(0, 123, 255, 0.05);
  border-color: rgba(0, 123, 255, 0.1);
  color: #0056b3;
}
</style>