import { supabaseClient } from './supabase';

// Get API gateway URL from environment variables
const API_GATEWAY_URL = import.meta.env.VITE_API_GATEWAY_URL || 'http://localhost:8000';

// API paths through Kong
const ORDER_PATH = '/api/orders';

// Get auth headers
const getAuthHeaders = async () => {
  const { data } = await supabaseClient.auth.getSession();
  const token = data.session?.access_token;
  
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

// Get all orders for a specific user
export const getUserOrders = async (userId) => {
  try {
    if (!userId) {
      throw new Error('User ID is required');
    }
    
    const headers = await getAuthHeaders();
    
    const response = await fetch(`${API_GATEWAY_URL}${ORDER_PATH}/user/${userId}`, {
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
    const response = await fetch(`${API_GATEWAY_URL}${ORDER_PATH}/type/${orderType}`, {
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