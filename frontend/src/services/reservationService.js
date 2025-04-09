// import Supabase client 
import { supabaseClient } from './supabase';

// base URLs for the API
const RESTAURANT_API_URL = 'http://localhost:5001/api';
const RESERVATION_API_URL = 'http://localhost:5002/api';
const CANCEL_BOOKING_URL = 'http://localhost:5005/cancel';
const REALLOCATION_URL = 'http://localhost:5002/reservation/reallocate_confirm_booking';
const ACCEPT_BOOKING_URL = 'http://localhost:5010/accept-booking';

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

// Check for pending reservations (status = 'Pending')
export const checkPendingReservations = async (userId) => {
  try {
    if (!userId) {
      throw new Error('User ID is required');
    }
    
    // Get all user reservations
    const reservations = await getUserReservations(userId);
    
    // Filter for pending ones
    return reservations.filter(res => res.status === 'Pending');
  } catch (error) {
    console.error('Error checking pending reservations:', error);
    throw error;
  }
};

// Accept a reallocation
export const acceptReallocation = async (acceptData) => {
  try {
    const reservationId = acceptData.reservation_id;
    if (!reservationId) {
      throw new Error('Reservation ID is required');
    }
    
    const headers = await getAuthHeaders();
    
    console.log(`Accepting reallocation for reservation ID: ${reservationId}`);
    
    // Make a request to the order service to retrieve order details by user_id
    const orderResponse = await fetch(`http://localhost:5004/api/orders/user/${acceptData.user_id}`);
    
    if (!orderResponse.ok) {
      throw new Error('Failed to retrieve order information');
    }
    
    const orderData = await orderResponse.json();
    let orderId = null;
    let paymentId = null;
    let price = 0;
    
    // Extract order details if available
    if (orderData.code === 200 && orderData.data && orderData.data.orders && orderData.data.orders.length > 0) {
      // Assuming the first order is the most recent one
      const order = orderData.data.orders[0];
      orderId = order.order_id;
      paymentId = order.payment_id;
      price = order.order_price;
    } else {
      // if no orders found, generate mock data
      console.log('No order found for user, using default values');
      orderId = Math.floor(Math.random() * 1000);
      paymentId = `py_${Date.now()}`;
      price = 0;
    }
    
    // Prepare data for the accept-booking endpoint
    const bookingData = {
      reservation_id: reservationId,
      user_id: acceptData.user_id,
      count: acceptData.count,
      payment_id: paymentId,
      order_id: orderId,
      price: price,
      booking_time: acceptData.booking_time
    };
    
    // Send the data to the accept-booking endpoint
    const response = await fetch(ACCEPT_BOOKING_URL, {
      method: 'POST',
      headers,
      body: JSON.stringify(bookingData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to confirm reservation');
    }
    
    const data = await response.json();
    console.log('Booking accepted:', data);
    
    return {
      success: true,
      message: 'Reservation confirmed successfully',
      data: data
    };
  } catch (error) {
    console.error('Error accepting reallocation:', error);
    throw error;
  }
};

// Decline a reallocation
export const declineReallocation = async (reservationId) => {
  try {
    if (!reservationId) {
      throw new Error('Reservation ID is required');
    }
    
    const headers = await getAuthHeaders();
    
    // For now, we'll just update the reservation status to 'Declined'
    // In a real implementation, this would call a backend API to decline and process the next user
    console.log(`Declining reallocation for reservation ID: ${reservationId}`);
    
    // Mock successful response
    return {
      success: true,
      message: 'Reservation offer declined successfully'
    };
  } catch (error) {
    console.error('Error declining reallocation:', error);
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
    
    console.log(`Sending cancellation request to: ${CANCEL_BOOKING_URL}/${reservationId}`);
    
    const response = await fetch(`${CANCEL_BOOKING_URL}/${reservationId}`, {
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