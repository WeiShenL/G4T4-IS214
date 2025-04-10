// import Supabase client 
import { supabaseClient } from './supabase';

// Get API gateway URL from environment variables
const API_GATEWAY_URL = import.meta.env.VITE_API_GATEWAY_URL || 'http://localhost:8000';

// API paths through Kong
const RESTAURANT_PATH = '/api/restaurants';
const RESERVATION_PATH = '/api/reservations';
const CANCEL_BOOKING_PATH = '/api/cancel';

// get auth headers
const getAuthHeaders = async () => {
  const { data } = await supabaseClient.auth.getSession();
  const token = data.session?.access_token;
  
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

// Get all restaurants
export const getAllRestaurants = async () => {
  try {
    const response = await fetch(`${API_GATEWAY_URL}${RESTAURANT_PATH}`);
    const data = await response.json();
    
    if (data.code === 200) {
      return data.data.restaurants;
    } else {
      throw new Error(data.message || 'Failed to fetch restaurants');
    }
  } catch (error) {
    console.error('Error fetching restaurants:', error);
    throw error;
  }
};

// Get restaurant by ID
export const getRestaurantById = async (id) => {
  try {
    const response = await fetch(`${API_GATEWAY_URL}${RESTAURANT_PATH}/${id}`);
    const data = await response.json();
    
    if (data.code === 200) {
      return data.data;
    } else if (data.code === 404) {
      return null;
    } else {
      throw new Error(data.message || `Failed to fetch restaurant with ID ${id}`);
    }
  } catch (error) {
    console.error(`Error fetching restaurant with ID ${id}:`, error);
    throw error;
  }
};

// Create a reservation
export const createReservation = async (reservationData) => {
  try {
    const headers = await getAuthHeaders();
    
    const response = await fetch(`${API_GATEWAY_URL}${RESERVATION_PATH}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(reservationData),
    });
    
    const data = await response.json();
    
    if (data.code === 201) {
      return {
        success: true,
        message: data.message,
        data: data.data
      };
    } else {
      throw new Error(data.message || 'Failed to create reservation');
    }
  } catch (error) {
    console.error('Error creating reservation:', error);
    throw error;
  }
};

// Get user reservations
export const getUserReservations = async (userId) => {
  try {
    if (!userId) {
      throw new Error('User ID is required');
    }
    
    const headers = await getAuthHeaders();
    
    // Pass userId as a string
    const response = await fetch(`${API_GATEWAY_URL}${RESERVATION_PATH}/user/${userId}`, {
      headers
    });
    
    const data = await response.json();
    
    if (data.code === 200) {
      return data.data.reservations;
    } else if (data.code === 404) {
      return [];
    } else {
      throw new Error(data.message || 'Failed to fetch user reservations');
    }
  } catch (error) {
    console.error('Error fetching user reservations:', error);
    throw error;
  }
};

// Cancel a reservation
export const cancelReservation = async (reservationId) => {
  try {
    if (!reservationId) {
      throw new Error('Reservation ID is required');
    }
    
    const headers = await getAuthHeaders();
    
    console.log(`Sending cancellation request to: ${API_GATEWAY_URL}${CANCEL_BOOKING_PATH}/${reservationId}`);
    
    const response = await fetch(`${API_GATEWAY_URL}${CANCEL_BOOKING_PATH}/${reservationId}`, {
      method: 'POST',
      headers
    });
    
    const data = await response.json();
    console.log('Cancellation API response:', data);
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to cancel reservation');
    }
    
    return {
      success: true,
      message: data.message || 'Reservation cancelled successfully',
      data: data
    };
  } catch (error) {
    console.error('Error cancelling reservation:', error);
    // Return a structured error response instead of throwing
    return {
      success: false,
      message: error.message || 'An error occurred during cancellation',
      error: error
    };
  }
};

// this is for filtering (might not need though)
export const getRestaurantsByAvailability = async (availability) => {
  try {
    const response = await fetch(`${API_GATEWAY_URL}${RESTAURANT_PATH}/availability/${availability}`);
    const data = await response.json();
    if (data.code === 200) {
      return data.data.restaurants;
    } else if (data.code === 404) {
      return [];
    } else {
      throw new Error(data.message || 'Failed to fetch restaurants by availability');
    }
  } catch (error) {
    console.error('Error fetching restaurants by availability:', error);
    throw error;
  }
};

// Get open restaurants
export const getOpenRestaurants = async () => {
  try {
    // Use the existing availability endpoint with parameter 1 (for open)
    const response = await fetch(`${API_GATEWAY_URL}${RESTAURANT_PATH}/availability/1`);
    const data = await response.json();
    
    if (data.code === 200) {
      // Return only the first 3 restaurants
      return data.data.restaurants.slice(0, 3);
    } else if (data.code === 404) {
      return [];
    } else {
      throw new Error(data.message || 'Failed to fetch open restaurants');
    }
  } catch (error) {
    console.error('Error fetching open restaurants:', error);
    throw error;
  }
};