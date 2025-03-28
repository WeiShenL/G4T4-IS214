import { supabaseClient } from './supabase';

// Base URLs for the API
const MENU_API_URL = 'http://localhost:5003/api';
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

// Get menu items for a specific restaurant
export const getRestaurantMenu = async (restaurantId) => {
  try {
    const response = await fetch(`${MENU_API_URL}/menu/${restaurantId}`);
    const data = await response.json();
    
    if (data.code === 200) {
      return data.data.menu_items;
    } else if (data.code === 404) {
      return [];
    } else {
      throw new Error(data.message || `Failed to fetch menu for restaurant ID ${restaurantId}`);
    }
  } catch (error) {
    console.error(`Error fetching menu for restaurant ID ${restaurantId}:`, error);
    throw error;
  }
};

// Get specific menu item by ID, idt this is needed
export const getMenuItemById = async (menuId) => {
  try {
    const response = await fetch(`${MENU_API_URL}/menu/item/${menuId}`);
    const data = await response.json();
    
    if (data.code === 200) {
      return data.data;
    } else {
      throw new Error(data.message || `Failed to fetch menu item with ID ${menuId}`);
    }
  } catch (error) {
    console.error(`Error fetching menu item with ID ${menuId}:`, error);
    throw error;
  }
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

// get all orders for a specific user (not used for now) --> order history page? idk
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