import { supabaseClient } from './supabase';

// Base URLs for the API
const MENU_API_URL = 'http://localhost:5003/api';

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

// Get specific menu item by ID --> NOT USED AS OF NOW
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