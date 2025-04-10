// Simple test service to verify Kong connectivity

// Get API gateway URL from environment variables
const API_GATEWAY_URL = import.meta.env.VITE_API_GATEWAY_URL || 'http://localhost:8000';

// Test Kong connectivity
export const testKongConnectivity = async () => {
  try {
    console.log('Testing Kong connectivity to restaurant service health endpoint...');
    const response = await fetch(`${API_GATEWAY_URL}/api/restaurant/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    
    const data = await response.json();
    console.log('Kong connectivity test response:', data);
    
    return {
      success: response.ok,
      status: response.status,
      data: data,
      message: response.ok ? 'Successfully connected to Kong' : 'Failed to connect to Kong'
    };
  } catch (error) {
    console.error('Error testing Kong connectivity:', error);
    return {
      success: false,
      error: error.message,
      message: 'Error connecting to Kong'
    };
  }
};

// Test connectivity to all critical services
export const testAllServices = async () => {
  try {
    const results = {};
    const endpoints = [
      { name: 'Restaurant', path: '/api/restaurant/health' },
      { name: 'User', path: '/api/user/health' },
      { name: 'Reservation', path: '/api/reservation/health' },
      { name: 'Menu', path: '/api/menu/health' },
      { name: 'Order', path: '/api/order/health' }
    ];
    
    console.log(`Testing connectivity to ${endpoints.length} services through Kong...`);
    
    // Test each endpoint
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(`${API_GATEWAY_URL}${endpoint.path}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        results[endpoint.name] = {
          success: response.ok,
          status: response.status,
          data: data
        };
      } catch (error) {
        results[endpoint.name] = {
          success: false,
          error: error.message
        };
      }
    }
    
    return {
      success: Object.values(results).some(r => r.success),
      results: results,
      message: Object.values(results).some(r => r.success) 
        ? 'Some services are accessible through Kong' 
        : 'Failed to connect to any services through Kong'
    };
  } catch (error) {
    console.error('Error testing services connectivity:', error);
    return {
      success: false,
      error: error.message,
      message: 'Error testing service connectivity'
    };
  }
}; 