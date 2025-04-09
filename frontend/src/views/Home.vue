<template>
  <div>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg fixed-top" :class="{ 'navbar-scrolled': hasScrolled }">
      <div class="container">
        <a class="navbar-brand" href="#">
          <span class="brand-text">FeastFinder</span>
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link btn-login" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link btn-signup" to="/signup">Sign Up</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Hero Banner Section -->
    <div id="heroSection" class="hero-section">
      <div class="hero-background">
        <div class="overlay"></div>
      </div>
      <div class="hero-content container">
        <div class="hero-text">
          <h1 class="hero-title" :class="{ 'active': animateHero }">All-in-One Platform for Restaurants</h1>
          <p class="hero-subtitle" :class="{ 'active': animateHero }">Order, deliver, and enjoy delicious meals from your favorite local restaurants</p>
          <div class="hero-buttons" :class="{ 'active': animateHero }">
            <router-link to="/login" class="btn btn-primary btn-lg">Login Now</router-link>
            <router-link to="/signup" class="btn btn-outline btn-lg">Become a Customer / Driver</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <h2 class="text-center mb-5 section-title fade-in" :class="{ 'show': isVisible('features-section') }">Why Choose FeastFinder?</h2>
        <div class="row justify-content-center">
          <div 
            v-for="(feature, index) in features" 
            :key="index"
            class="col-md-4 col-sm-6 feature-item fade-in"
            :class="{ 'show': isVisible('features-section') && visibleFeatures > index }"
          >
            <div class="feature-icon">
              <i :class="feature.icon"></i>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="how-it-works fade-in" :class="{ 'show': isVisible('how-it-works') }">
      <div class="container">
        <h2 class="text-center mb-5 section-title">How It Works</h2>
        <div class="row">
          <div class="col-lg-6 mb-4">
            <div class="process-card customer-card">
              <h3 class="process-title">For Customers</h3>
              <div class="process-steps">
                <div class="process-step" v-for="(step, index) in customerSteps" :key="index">
                  <div class="step-number">{{ index + 1 }}</div>
                  <div class="step-content">
                    <h4>{{ step.title }}</h4>
                    <p>{{ step.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-6 mb-4">
            <div class="process-card driver-card">
              <h3 class="process-title">For Delivery Partners</h3>
              <div class="process-steps">
                <div class="process-step" v-for="(step, index) in driverSteps" :key="index">
                  <div class="step-number">{{ index + 1 }}</div>
                  <div class="step-content">
                    <h4>{{ step.title }}</h4>
                    <p>{{ step.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Call to Action Section -->
    <section class="cta-section fade-in" :class="{ 'show': isVisible('cta-section') }">
      <div class="container text-center">
        <h2>Ready to Get Started?</h2>
        <p class="mb-4">Join thousands of satisfied customers and delivery partners today!</p>
        <div class="cta-buttons">
          <router-link to="/signup" class="btn btn-primary btn-lg me-3">Sign Up as Customer</router-link>
          <router-link to="/signup?type=driver" class="btn btn-secondary btn-lg">Become a Driver</router-link>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer-section">
      <div class="container">
        <div class="row">
          <div class="col-lg-4 mb-4 mb-lg-0">
            <h3 class="footer-brand">FeastFinder</h3>
            <p>Connecting food lovers with local restaurants through a seamless delivery experience.</p>
            <div class="social-icons">
              <a href="#"><i class="fab fa-facebook-f"></i></a>
              <a href="#"><i class="fab fa-twitter"></i></a>
              <a href="#"><i class="fab fa-instagram"></i></a>
              <a href="#"><i class="fab fa-linkedin-in"></i></a>
            </div>
          </div>
          <div class="col-lg-2 col-md-4 col-6 mb-4 mb-md-0">
            <h5>Quick Links</h5>
            <ul class="footer-links">
              <li><router-link to="/">Home</router-link></li>
              <li><a href="#">Restaurants</a></li>
            </ul>
          </div>
          <div class="col-lg-2 col-md-4 col-6 mb-4 mb-md-0">
            <h5>For Customers</h5>
            <ul class="footer-links">
              <li><router-link to="/signup">Sign Up</router-link></li>
              <li><router-link to="/login">Log In</router-link></li>
            </ul>
          </div>
          <div class="col-lg-2 col-md-4 col-6 mb-4 mb-md-0">
            <h5>For Drivers</h5>
            <ul class="footer-links">
              <li><router-link to="/signup?type=driver">Become a Driver</router-link></li>
              <li><router-link to="/login?type=driver">Driver Login</router-link></li>
            </ul>
          </div>
        </div>
        <hr>
        <div class="text-center py-3">
          <p>&copy; 2025 FeastFinder. All rights reserved.</p>
        </div>
      </div>
    </footer>

    <!-- Back to Top Button -->
    <button @click="scrollToTop" class="btn back-to-top">
      <i class="fas fa-arrow-up"></i>
    </button>

    <!-- Scroll Indicator -->
    <div class="scroll-indicator" :class="{ 'hidden': hasScrolled }">
      <div class="scroll-arrow">
        <i class="fas fa-chevron-down"></i>
      </div>
      <span class="scroll-text">Scroll</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      hasScrolled: false,
      animateHero: false,
      visibleFeatures: 0,
      features: [
        {
          icon: 'fas fa-utensils',
          title: 'Restaurant Selection',
          description: 'Easily select from our list of local restaurants to satisfy your craving.'
        },
        {
          icon: 'fas fa-undo',
          title: 'Easy Cancellation & Refund',
          description: 'Hassle-free cancellation process with quick refunds to ensure customer satisfaction.'
        },
        {
          icon: 'fas fa-mobile-alt',
          title: 'Easy Ordering',
          description: 'Simple, intuitive interface makes ordering your favorite meals quick and hassle-free.'
        },
        {
          icon: 'fas fa-calendar-check',
          title: 'Table Reservations & Pre-Order',
          description: 'Book a table and pre-order your meals to have everything ready when you arrive.'
        },
        {
          icon: 'fas fa-shopping-bag',
          title: 'Food Delivery Orders',
          description: 'Get your favorite meals delivered right to your doorstep with our reliable delivery service.'
        },
        {
          icon: 'fas fa-bell',
          title: 'SMS Notifications',
          description: 'Receive real-time update notifications about your order status directly on your device.'
        }
      ],
      customerSteps: [
        {
          title: 'Browse Restaurants',
          description: 'Explore local restaurants and view their menus'
        },
        {
          title: 'Place Order for Delivery or Dine-in',
          description: 'Select your favorite dishes for dine-in or delivery'
        },
        {
          title: 'Stay Updated',
          description: 'Receive notifications and updates about your order or reservation status'
        },
        {
          title: 'Enjoy Your Meal',
          description: ''
        }
      ],
      driverSteps: [
        {
          title: 'Sign Up',
          description: 'Create your account'
        },
        {
          title: 'Accept Orders',
          description: 'Receive nearby delivery requests and choose which to accept'
        },
        {
          title: 'Set Your Schedule',
          description: 'Choose when you want to work - full flexibility'
        },
        {
          title: 'Get Paid!',
          description: ''
        }
      ]
    };
  },
  mounted() {
    // Animate hero section
    setTimeout(() => {
      this.animateHero = true;
    }, 300);

    // Add scroll event listener
    window.addEventListener('scroll', this.handleScroll);
    
    // Initial check for visible elements
    this.handleScroll();
    
    // Handle Bootstrap navbar
    this.initBootstrap();
  },
  beforeUnmount() {
    // Remove scroll event listener
    window.removeEventListener('scroll', this.handleScroll);
  },
  methods: {
    scrollToTop() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    },
    handleScroll() {
      // Update navbar style
      this.hasScrolled = window.scrollY > 50;
      
      // Update features animation
      if (this.isVisible('features-section')) {
        this.animateFeatures();
      }
      
      // Other animations
      const elements = document.querySelectorAll('.fade-in');
      const windowHeight = window.innerHeight;

      elements.forEach(el => {
        if (el) {
          const position = el.getBoundingClientRect().top;
          if (position < windowHeight - 100) {
            el.classList.add('show');
          }
        }
      });
    },
    isVisible(className) {
      const element = document.querySelector(`.${className}`);
      if (!element) return false;
      
      const rect = element.getBoundingClientRect();
      return rect.top < window.innerHeight - 100;
    },
    animateFeatures() {
      // Animate features sequentially
      const interval = setInterval(() => {
        if (this.visibleFeatures < this.features.length) {
          this.visibleFeatures++;
        } else {
          clearInterval(interval);
        }
      }, 150);
    },
    initBootstrap() {
      // This is needed to integrate with Bootstrap's JavaScript
      // Normally you would use Bootstrap Vue or another integration
      // but for simplicity, we'll just use window.bootstrap if available
      if (typeof window !== 'undefined' && window.bootstrap) {
        // Initialize Bootstrap components here if needed
      }
    }
  }
};
</script>