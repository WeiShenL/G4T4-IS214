import { loadStripe } from '@stripe/stripe-js';

// Stripe public key from environment 
const STRIPE_PUBLISHABLE_KEY = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;

// Backend API endpoints
const PAYMENT_API_URL = 'http://localhost:5006/api/payment';

// Stripe instance
let stripePromise = null;

/**
 * Initialize Stripe
 */
export const initStripe = () => {
  if (!stripePromise) {
    stripePromise = loadStripe(STRIPE_PUBLISHABLE_KEY);
  }
  return stripePromise;
};

/**
 * Create a checkout session with Stripe
 * @param {Object} orderDetails - Order details including items, amount, etc.
 * @param {string} customerId - userID
 * @param {string} successUrl - URL to redirect on successful payment
 * @param {string} cancelUrl - URL to redirect on canceled payment
 */
export const createCheckoutSession = async (orderDetails, customerId, successUrl, cancelUrl) => {
  try {
    const response = await fetch(`${PAYMENT_API_URL}/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ orderDetails, customerId, successUrl, cancelUrl })
    });
    
    const data = await response.json();
    
    if (data.code !== 200) {
      throw new Error(data.message || 'Failed to create checkout session');
    }
    
    return {
      sessionId: data.sessionId,
      url: data.url
    };
  } catch (error) {
    console.error('Error creating checkout session:', error);
    throw new Error('Failed to initialize checkout process');
  }
};

/**
 * Verify a payment was successful
 * @param {string} sessionId - Stripe Checkout session ID
 */
export const verifyPayment = async (sessionId) => {
  try {
    const response = await fetch(`${PAYMENT_API_URL}/verify-payment/${sessionId}`);
    const data = await response.json();
    
    if (data.code !== 200) {
      throw new Error(data.message || 'Payment verification failed');
    }
    
    return {
      paymentIntent: data.paymentIntent
    };
  } catch (error) {
    console.error('Error verifying payment:', error);
    throw new Error('Payment verification failed');
  }
};

/**
 * Process a refund through Stripe
 * @param {string} paymentId - The original payment intent ID
 * @param {number} amount - Amount to refund (in cents)
 */
export const processRefund = async (paymentId, amount = null) => {
  try {
    const response = await fetch(`${PAYMENT_API_URL}/refund`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        payment_id: paymentId, 
        amount: amount 
      })
    });
    
    const data = await response.json();
    
    if (data.code !== 200) {
      throw new Error(data.message || 'Refund processing failed');
    }
    
    return {
      refundId: data.refund.id,
      amount: data.refund.amount,
      status: data.refund.status
    };
  } catch (error) {
    console.error('Error processing refund:', error);
    throw new Error('Failed to process refund: ' + error.message);
  }
};