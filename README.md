# G4T4-IS214

## FeastFinder
![image](https://raw.githubusercontent.com/WeiShenL/G4T4-IS214/refs/heads/main/assets/FeastFinder.png?token=GHSAT0AAAAAAC7CYRFLAZQW36R2JG7XEGJCZ7YHN3Q)

## Prerequisites

Ensure you have the following installed:

- [Node.js](https://nodejs.org/) (v16 or newer recommended)
- npm (comes with Node.js)
- [GitHub Desktop](https://desktop.github.com/) or Git CLI
- Docker
- IDE (any)


## Getting Started

**Important** Put .env files into backend and frontend directory

Follow these steps to set up the FeastFinder application on your local machine:

### 1. Open terminal and run the following command:
```bash
  cd backend
  docker-compose up -d --build
  docker-compose down
```

### 2. Open another terminal to Install Dependencies
Navigate to the frontend directory:
```bash
cd frontend
npm install
```

### 3. Run the Development Server
After installing dependencies, start the development server:
```bash
npm run dev
```
This will launch the application, typically at [http://localhost:5173](http://localhost:5173).

## Technical Architecture Diagram
![image]()

## Frameworks and Databases Utilised
<p align="center"><strong>Microservices and UI</strong></p>
<p align="center">
<a href="https://vitejs.dev/"><img src="https://upload.wikimedia.org/wikipedia/commons/f/f1/Vitejs-logo.svg" alt="Vite" height="40"/></a>&nbsp;&nbsp;
<a href="https://vuejs.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/9/95/Vue.js_Logo_2.svg" alt="Vue" height="40"/></a>&nbsp;&nbsp;
<a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6a/JavaScript-logo.png" alt="JavaScript" height="40"/></a>&nbsp;&nbsp;
<a href="https://www.python.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext.svg.png" alt="Python" height="40"/></a>&nbsp;&nbsp;
<a href="https://flask.palletsprojects.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/3/3c/Flask_logo.svg" alt="Flask" width="100"/></a>&nbsp;&nbsp;
<a href="https://supabase.com/"><img src="https://www.vectorlogo.zone/logos/supabase/supabase-icon.svg" alt="Supabase" height="55" /></a>&nbsp;&nbsp;
<br>
<i>Vite · Vue · JavaScript · Python · Flask · Supabase Auth</i>
</p>
<br>

<p align="center"><strong>Low Code Platform</strong></p>
<p align="center">
<a href="https://www.outsystems.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/8/82/OS-logo-color_500x108.png" alt="outsystems" width="100"/></a>
<br>
<i>outsystems</i>
</p>
<br> 

<p align="center"><strong>External API</strong></p>  
<p align="center">
<a href="https://maps.google.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Google_Maps_Logo_2020.svg/533px-Google_Maps_Logo_2020.svg.png" alt="Google Maps" height="40"/></a>&nbsp;&nbsp;
<a href="https://stripe.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Stripe_Logo%2C_revised_2016.svg/1280px-Stripe_Logo%2C_revised_2016.svg.png" alt="Stripe" height="40"/></a>&nbsp;&nbsp;
<a href="https://www.twilio.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/c/c0/Twilio_logo.png" alt="Twilio" height="40" /></a>&nbsp;&nbsp;
<a href="https://openstreetmap.com/"><img src="https://www.openstreetmap.org/assets/osm_logo-4b074077c29e100f40ee64f5177886e36b570d4cc3ab10c7b263003d09642e3f.svg" alt="Open Street Map" height="40"/></a>&nbsp;&nbsp;
<br>
<i>Google Maps API · Stripe · Twilio · Open Street Map</i>
</p>
<br>

<p align="center"><strong>Storage Solutions</strong></p>  
<p align="center">
<a href="https://supabase.com/"><img src="https://www.vectorlogo.zone/logos/supabase/supabase-icon.svg" alt="Supabase" height="55" /></a>&nbsp;&nbsp;
<br>
<i>Supabase</i>
</p>
<br> 

<p align="center"><strong>Message Brokers</strong></p>
<p align="center">
<a href="https://www.rabbitmq.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/7/71/RabbitMQ_logo.svg" alt="RabbitMQ" width="100"/></a>
<br>
<i>rabbitMQ</i>
</p>
<br> 

<p align="center"><strong>Inter-service Communications</strong></p>
<p align="center">
<a href="https://restfulapi.net/"><img src="https://keenethics.com/wp-content/uploads/2022/01/rest-api-1.svg" alt="REST API" height="40"/></a>
<br>
<i>REST API</i>
</p> 
<br>

<p align="center"><strong>API Gateway</strong></p>
<p align="center">
<a href="https://konghq.com/"><img src="https://konghq.com/wp-content/uploads/2018/08/kong-combination-mark-color-256px.png" alt="Kong API Gateway" width="88"/></a>
<br>
<i>Kong</i>
</p>
<br> 

<p align="center"><strong>Deployment & Containerization</strong></p>
<p align="center">
<a href="https://github.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" alt="GitHub" height="60"/></a>&nbsp;&nbsp;
<a href="https://www.docker.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/4/4e/Docker_%28container_engine%29_logo.svg" alt="Docker" height="30"/></a>&nbsp;&nbsp;
</p>
<p align="center">
<i>Github · Docker Compose</i>
</p>
<br> 
