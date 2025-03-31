// import Supabase client 
import { supabaseClient } from './supabase';

// base URLs for the API
const RESTAURANT_API_URL = 'http://localhost:5001/api';
const RESERVATION_API_URL = 'http://localhost:5002/api';
const CANCEL_BOOKING_URL = 'http://localhost:5002/cancel';


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
    const response = await fetch(`${RESTAURANT_API_URL}/restaurants`);
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
    const response = await fetch(`${RESTAURANT_API_URL}/restaurants/${id}`);
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
    
    const response = await fetch(`${RESERVATION_API_URL}/reservations`, {
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
    const response = await fetch(`${RESERVATION_API_URL}/reservations/user/${userId}`, {
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
    
    const response = await fetch(`${CANCEL_BOOKING_API_URL}/${reservationId}`, {
      method: 'POST',
      headers
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to cancel reservation');
    }
    
    const data = await response.json();
    
    return {
      success: true,
      message: data.message || 'Reservation cancelled successfully',
      data: data
    };
  } catch (error) {
    console.error('Error cancelling reservation:', error);
    throw error;
  }
};

// this is for filtering (might not need though)
export const getRestaurantsByAvailability = async (availability) => {
  try {
    const response = await fetch(`${RESTAURANT_API_URL}/restaurants/availability/${availability}`);
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

// this is for filtering (might not need though)
export const getRestaurantsByCuisine = async (cuisine) => {
  try {
    const response = await fetch(`${RESTAURANT_API_URL}/restaurants/cuisine/${cuisine}`);
    const data = await response.json();
    if (data.code === 200) {
      return data.data.restaurants;
    } else if (data.code === 404) {
      return [];
    } else {
      throw new Error(data.message || 'Failed to fetch restaurants by cuisine');
    }
  } catch (error) {
    console.error('Error fetching restaurants by cuisine:', error);
    throw error;
  }
};