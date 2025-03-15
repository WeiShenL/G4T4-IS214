import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// other CSS files
import './assets/css/styles.css'
import './assets/css/dashboard.css'

// font Awesome CSS
import '@fortawesome/fontawesome-free/css/all.min.css';

createApp(App).use(router).mount('#app')