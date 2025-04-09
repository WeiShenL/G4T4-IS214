import { supabaseClient } from './supabase';

// Base URL for the API
const ORDER_API_URL = 'http://localhost:5004/api';

// Get auth headers
const getAuthHeaders = async () => {
  const { data } = await supabaseClient.auth.getSession();
  const token = data.session?.access_token;
  
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

// Create a new order with Stripe payment ID
export const createOrder = async (orderData) => {
  try {
    const headers = await getAuthHeaders();
    
    const response = await fetch(`${ORDER_API_URL}/orders`, {
      method: 'POST',
      headers,
      body: JSON.stringify(orderData),
    });
    
    const data = await response.json();
    
    if (data.code === 201) {
      return {
        success: true,
        message: data.message,
        data: data.data
      };
    } else {
      throw new Error(data.message || 'Failed to create order');
    }
  } catch (error) {
    console.error('Error creating order:', error);
    throw error;
  }
};

// Get all orders for a specific user
export const getUserOrders = async (userId) => {
  try {
    if (!userId) {
      throw new Error('User ID is required');
    }
    
    const headers = await getAuthHeaders();
    
    const response = await fetch(`${ORDER_API_URL}/orders/user/${userId}`, {
      headers
    });
    
    const data = await response.json();
    
    if (data.code === 200) {
      return data.data.orders;
    } else if (data.code === 404) {
      return [];
    } else {
      throw new Error(data.message || 'Failed to fetch user orders');
    }
  } catch (error) {
    console.error('Error fetching user orders:', error);
    throw error;
  }
};

// Get orders for a specific user by order type
export const getUserOrdersByType = async (userId, orderType) => {
  try {
    if (!userId) {
      throw new Error('User ID is required');
    }
    
    if (!orderType) {
      throw new Error('Order type is required');
    }
    
    const headers = await getAuthHeaders();
    
    // Use the orders api to get all orders of a specific type
    const response = await fetch(`${ORDER_API_URL}/orders/type/${orderType}`, {
      headers
    });
    
    const data = await response.json();
    
    if (data.code === 200) {
      // Further filter by user ID since the endpoint returns all orders of a type
      const filteredOrders = data.data.orders.filter(order => order.user_id === userId);
      return filteredOrders;
    } else if (data.code === 404) {
      return [];
    } else {
      throw new Error(data.message || `Failed to fetch ${orderType} orders`);
    }
  } catch (error) {
    console.error(`Error fetching ${orderType} orders for user ${userId}:`, error);
    throw error;
  }
}; 