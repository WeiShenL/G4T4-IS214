# G4T4-IS214 (FeastFinder, temp name for now) 

## Project Overview
FeastFinder is an all-in-one platform for food delivery that offers:

- Customer accounts for ordering food
- Driver accounts for food delivery
- User authentication and profile management
- Intuitive dashboards for both customers and drivers

## Prerequisites

Ensure you have the following installed:

- [Node.js](https://nodejs.org/) (v16 or newer recommended)
- npm (comes with Node.js)
- [GitHub Desktop](https://desktop.github.com/) or Git CLI

## Getting Started

**Important** Switch to your branch before starting to code!

Follow these steps to set up the FeastFinder application on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/G4t4.git
cd G4t4
```

### 2. Install Dependencies
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

## Project Structure

```
frontend/
│── src/
│   ├── components/    # UI components
│   ├── views/         # Page components
│   ├── services/      # API services (Supabase connection)
│   ├── router/        # Vue Router configuration
│   ├── assets/        # CSS and other static files
```

## Database

The application uses [Supabase](https://supabase.com/) as its backend database service. The database structure includes:

- Customer profiles
- Driver profiles
- User types
- Authentication

## Technology Stack

- **Frontend Framework:** Vue.js
- **UI Components:** Custom components with CSS
- **Router:** Vue Router
- **Backend/Database:** Supabase
- **Build Tool:** Vite