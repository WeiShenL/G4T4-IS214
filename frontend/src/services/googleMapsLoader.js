// lad Google Maps API dynamically
export const loadGoogleMapsApi = (callback = null) => {
    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    
    // Check if the API is already loaded
    if (window.google && window.google.maps) {
      if (callback) callback();
      return;
    }
  
    // Set the callback function for when the API is loaded
    window.initMap = callback || function() {};
    
    // Create script element
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=initMap`;
    script.async = true;
    script.defer = true;
    
    // Append to document
    document.head.appendChild(script);
    console.log('Google Maps API loaded');
  };