<template>
  <div>
    <!-- Dashboard Header -->
    <div class="dashboard-header">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <router-link to="/" class="dashboard-logo">
            <span>FeastFinder</span>
          </router-link>
          <div class="dashboard-user">
            <div class="dropdown">
              <button class="btn dropdown-toggle" type="button" id="userDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="fas fa-user-circle"></i>
                <span v-if="routingData">{{ routingData.driver.name }}</span>
                <span v-else>Loading...</span>
              </button>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                <li><router-link class="dropdown-item" to="/driver-profile"><i class="fas fa-user-cog"></i> My Profile</router-link></li>
                <li><router-link class="dropdown-item" to="/driver-deliveries"><i class="fas fa-history"></i> Delivery History</router-link></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click.prevent="goHome"><i class="fas fa-sign-out-alt"></i> Return to Dashboard</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Dashboard Content -->
    <div class="dashboard-container">
      <div class="container">
        <!-- Error Message -->
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
          {{ errorMessage }}
        </div>
        
        <!-- Loading State -->
        <div v-if="!routingData" class="loading-container text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p>Loading order information...</p>
        </div>
        
        <div v-else>
          <!-- Order Information Card -->
          <div class="row mb-4">
            <div class="col-12">
              <div class="card">
                <div class="card-body">
                  <h4 class="card-title">Order #{{ routingData.order.order_id }}</h4>
                  <div class="row">
                    <div class="col-md-4">
                      <div class="info-group">
                        <span class="info-label"><i class="fas fa-utensils"></i> Restaurant</span>
                        <span class="info-value">{{ routingData.restaurant.name }}</span>
                        <span class="info-address">{{ routingData.restaurant.location }}</span>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div class="info-group">
                        <span class="info-label"><i class="fas fa-shopping-bag"></i> Order</span>
                        <span class="info-value">{{ routingData.order.item_name }}</span>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div class="info-group">
                        <span class="info-label"><i class="fas fa-user"></i> Customer</span>
                        <span class="info-value">{{ routingData.order.customer.name }}</span>
                        <span class="info-address">{{ routingData.order.customer.location }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Order State Content -->
          <div class="row mb-4">
            <div class="col-12">
              <!-- Before accepting -->
              <div v-if="!accepted" class="card">
                <div class="card-body text-center">
                  <h3 class="section-heading mb-4">Delivery Request</h3>
                  <p class="lead">Do you want to accept this order?</p>
                  <div class="d-flex justify-content-center gap-3 mt-4">
                    <button @click="acceptOrder" class="btn btn-success btn-lg">
                      <i class="fas fa-check"></i> Accept Order
                    </button>
                    <button @click="cancelOrder" class="btn btn-outline-secondary btn-lg">
                      <i class="fas fa-times"></i> Cancel
                    </button>
                  </div>
                </div>
              </div>

              <!-- Route to Restaurant -->
              <div v-else-if="accepted && !pickedUp" class="card">
                <div class="card-body">
                  <h3 class="section-heading mb-3">Route to Restaurant</h3>
                  <div class="map-container" id="map-container"></div>
                  <div class="text-center mt-4">
                    <button @click="pickUpOrder" class="btn btn-primary btn-lg">
                      <i class="fas fa-hand-holding"></i> Pick Up Order
                    </button>
                  </div>
                </div>
              </div>

              <!-- Route to Customer (after pickup) -->
              <div v-else-if="pickedUp && !orderCompleted" class="card">
                <div class="card-body">
                  <h3 class="section-heading mb-3">Route to Customer</h3>
                  <div class="map-container" id="map-container"></div>
                  <div class="text-center mt-4">
                    <button @click="completeOrder" class="btn btn-success btn-lg">
                      <i class="fas fa-check-circle"></i> Complete Delivery
                    </button>
                  </div>
                </div>
              </div>

              <!-- Completed -->
              <div v-else-if="orderCompleted" class="card">
                <div class="card-body text-center">
                  <div class="py-4">
                    <i class="fas fa-check-circle text-success" style="font-size: 5rem;"></i>
                    <h3 class="section-heading mt-3">Order Completed!</h3>
                    <p class="lead">Thank you for delivering with FeastFinder</p>
                    <button @click="goHome" class="btn btn-primary btn-lg mt-3">
                      <i class="fas fa-home"></i> Return to Dashboard
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { loadGoogleMapsApi } from '@/services/googleMapsLoader';

export default {
  name: 'RoutingPage',
  setup() {
  

    const route = useRoute();
    const router = useRouter();

    const routingData = ref(null);
    const errorMessage = ref('');
    const accepted = ref(false);
    const orderId = route.query.order_id;

    
    const pickedUp = ref(false); // New state to track if the order is picked up
    const orderCompleted = ref(false);

    const acceptOrder = () => {
      accepted.value = true;
      initRoutingAndTrigger();
    };

    const cancelOrder = () => {
      router.back();
    };


    // ACCEPT
    const initRoutingAndTrigger = () => {
      if (!routingData.value) {
        console.error('No routing data available');
        return;
      }

      const restaurantCoords = routingData.value.restaurant.coordinates;
      const driverId = routingData.value.driver.id;

      // Convert "lat,lng" string to object
      const [destLat, destLng] = restaurantCoords.split(',').map(Number);
      const destination = { lat: destLat, lng: destLng };

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const driverCoords = {
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            };

            // Use the loadGoogleMapsApi function to ensure the API is loaded
            console.log('Loading Google Maps API for restaurant routing');
            loadGoogleMapsApi(() => {
              console.log('Google Maps API loaded, initializing map to restaurant');
              try {
                const mapElement = document.getElementById('map-container');
                if (!mapElement) {
                  console.error('Map container element not found');
                  return;
                }

                const map = new google.maps.Map(mapElement, {
                  zoom: 14,
                  center: driverCoords,
                });

                const directionsService = new google.maps.DirectionsService();
                const directionsRenderer = new google.maps.DirectionsRenderer();
                directionsRenderer.setMap(map);

                const routeRequest = {
                  origin: driverCoords,
                  destination,
                  travelMode: 'DRIVING',
                };

                directionsService.route(routeRequest, (result, status) => {
                  if (status === 'OK') {
                    directionsRenderer.setDirections(result);
                    console.log('Directions rendered successfully');
                  } else {
                    console.error('Routing failed:', status);
                    alert('Routing failed: ' + status);
                  }
                });
              } catch (error) {
                console.error('Error initializing map:', error);
              }

              // Trigger API
              fetch('http://localhost:5101/accept-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  driver_id: driverId,
                  order_id: orderId,
                }),
              })
                .then((res) => res.json())
                .then((data) => {
                  console.log('Driver status updated:', data);
                })
                .catch((err) => {
                  console.error('Failed to update driver status:', err);
                });
            });
          },
          (positionError) => {
            console.error('Location access denied:', positionError);
            alert('Location access denied.');
          },
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
      } else {
        console.error('Geolocation not supported by browser');
        alert('Geolocation not supported.');
      }
    };

    // picked up order
    const pickUpOrder = () => {
      pickedUp.value = true; // Update state to trigger UI update
      if (!routingData.value) {
        console.error('No routing data available for pickup');
        return;
      }

      const driverId = routingData.value.driver.id;

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const driverCoords = {
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            };

            const customerCoords = routingData.value.order.customer.coordinates.split(',').map(Number);
            const customerLocation = { lat: customerCoords[0], lng: customerCoords[1] };

            // Use the loadGoogleMapsApi function to ensure the API is loaded
            console.log('Loading Google Maps API for customer routing');
            loadGoogleMapsApi(() => {
              console.log('Google Maps API loaded, initializing map to customer');
              try {
                const mapElement = document.getElementById('map-container');
                if (!mapElement) {
                  console.error('Map container element not found');
                  return;
                }

                const map = new google.maps.Map(mapElement, {
                  zoom: 14,
                  center: driverCoords,
                });

                const directionsService = new google.maps.DirectionsService();
                const directionsRenderer = new google.maps.DirectionsRenderer();
                directionsRenderer.setMap(map);

                const routeRequest = {
                  origin: driverCoords,
                  destination: customerLocation,
                  travelMode: 'DRIVING',
                };

                directionsService.route(routeRequest, (result, status) => {
                  if (status === 'OK') {
                    directionsRenderer.setDirections(result);
                    console.log('Directions to customer rendered successfully');
                  } else {
                    console.error('Routing to customer failed:', status);
                    alert('Routing failed: ' + status);
                  }
                });
              } catch (error) {
                console.error('Error initializing map to customer:', error);
              }
            });

            // Call API to mark order as picked up
            fetch('http://localhost:5101/pick-up-order', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                driver_id: driverId,
                order_id: orderId,
              }),
            })
              .then((res) => res.json())
              .then((data) => {
                console.log('Order picked up:', data);
              
              })
              .catch((err) => {
                console.error('Failed to mark order as picked up:', err);
              });
          },
          (positionError) => {
            console.error('Location access denied:', positionError);
            alert('Location access denied.');
          },
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
      }
    };

    // complete order
    const completeOrder = () => {
      orderCompleted.value = true;

      // Call the deliver-order API after completing the order
      fetch('http://localhost:5101/deliver-order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          driver_id: routingData.value.driver.id,
          order_id: orderId
        })
      })
        .then((res) => res.json())
        .then((data) => {
          console.log('Order delivered successfully:', data);
        })
        .catch((err) => {
          console.error('Failed to deliver order:', err);
        });
    };

    const goHome = () => {
      router.back();  // Navigate back to the previous page
    };


    onMounted(() => {
      // Initial Google Maps API load
      console.log('Loading Google Maps API on RoutingPage mount');
      loadGoogleMapsApi();
      
      // Check if order_id is in the query params and if data exists in localStorage
      const storedData = localStorage.getItem('routingData');
      if (storedData) {
        routingData.value = JSON.parse(storedData);
        console.log('Loaded routing data:', routingData.value);
      } else {
        // Handle case where data is missing or invalid, or you may want to fetch it via an API
        if (orderId) {
          // Here you can fetch the data from an API if needed, based on orderId
          console.log('Fetching data for order_id:', orderId);
          // Example: Fetch from API or another storage
          fetch(`/api/routing-data/${orderId}`)
            .then((res) => res.json())
            .then((data) => {
              // remember to chagne backkkkkkkkkkkkkkkkkkk to thissssssssssssssss
              routingData.value = data;
              localStorage.setItem('routingData', JSON.stringify(data)); 
              // use static for now
              // routingData.value = staticData;
              // console.log('Loaded static routing data:', routingData.value);

              // Optionally store the static data in localStorage
              // localStorage.setItem('routingData', JSON.stringify(staticData));
            })
            .catch((err) => {
              errorMessage.value = 'Error fetching routing data.';
              console.error('Error:', err);
            });
        } else {
          errorMessage.value = 'Missing routing data. Please return to dashboard.';
          console.error('Missing routing data');
        }
      }
    });


    return {
      routingData,
      errorMessage,
      orderId,
      
      acceptOrder,
      cancelOrder,
      pickUpOrder,
      completeOrder,
      
      accepted,
      pickedUp,
      orderCompleted,
      goHome,
      
    };
  },
};
</script>

<style scoped>
.map-container {
  height: 500px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.info-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.info-label {
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 5px;
}

.info-value {
  font-size: 1.1rem;
  font-weight: 500;
  color: #2c3e50;
}

.info-address {
  font-size: 0.9rem;
  color: #6c757d;
}

.section-heading {
  color: #2c3e50;
  font-weight: 600;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}
</style>