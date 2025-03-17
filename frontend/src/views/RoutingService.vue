<template>
    <div class="routing-service">
      <p v-if="!isFoodPickedUp">Route to Restaurant: <strong>{{ order.restaurant }}</strong></p>
      <p v-else>Route to Destination: <strong>{{ order.destination }}</strong></p>
  
      <!-- Pickup Confirmation Button -->
      <button v-if="!isFoodPickedUp" @click="confirmPickup" class="pickup-button">
        Confirm Food Pickup
      </button>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      order: {
        type: Object,
        required: true,
      },
    },
    data() {
      return {
        isFoodPickedUp: false,
      };
    },
    methods: {
      confirmPickup() {
        this.isFoodPickedUp = true;
        this.$emit('pickup-complete', this.order.id);
      },
    },
  };
  </script>
  
  <style scoped>
  .routing-service {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .routing-service p {
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #333;
  }
  
  .pickup-button {
    background-color: #28a745;
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .pickup-button:hover {
    background-color: #218838;
  }
  </style>