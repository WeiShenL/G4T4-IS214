// Base URL for the API
const API_BASE_URL = 'http://localhost:5001/api';

// Get all restaurants
export const getAllRestaurants = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/restaurants`);
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
    const response = await fetch(`${API_BASE_URL}/restaurants/${id}`);
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
    const response = await fetch(`${API_BASE_URL}/reservations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
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
    const response = await fetch(`${API_BASE_URL}/reservations/user/${userId}`);
    const data = await response.json();
    
    if (data.code === 200) {
      return data.data.reservations;
    } else {
      throw new Error(data.message || 'Failed to fetch user reservations');
    }
  } catch (error) {
    console.error('Error fetching user reservations:', error);
    throw error;
  }
};

// Get restaurants by availability
export const getRestaurantsByAvailability = async (availability) => {
    try {
      const response = await fetch(`${API_BASE_URL}/restaurants/availability/${availability}`);
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