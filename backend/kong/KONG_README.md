# Kong API Gateway

This directory contains the configuration and setup files for the Kong API Gateway used in the FeastFinder application.

## Overview

Kong serves as the API Gateway for our microservices architecture, providing:
- Single entry point for all client requests
- Service discovery
- Rate limiting
- Authentication (when configured)
- Request routing
- Load balancing

## Directory Structure

- `setup_kong.sh` - Script to configure all services and routes in Kong (This file will auto run when u docker compose up inside /backend)
- `kong_one_click_setup.sh` - One-click script to restart and reconfigure Kong
- `test_kong.sh` - Script to test all service endpoints

## Kong Components

Our Kong setup consists of:
1. **Kong Database** (PostgreSQL) - Stores Kong's configuration
2. **Kong Migration** - Sets up the database schema
3. **Kong** - The API Gateway service
4. **Kong Setup** - A container that runs the setup script

## Quick Start

For a quick and easy setup, use the one-click setup script:

```bash
  cd backend
  docker-compose up -d --build
```

## Service Configuration

Kong is configured with the following services and routes:

### Simple Services
- **User Service**: `/api/user`
- **Restaurant Service**: `/api/restaurants`
- **Reservation Service**: `/api/reservations`
- **Menu Service**: `/api/menu`
- **Order Service**: `/api/orders`
- **Payment Service**: `/api/payment`
- **Notification Service**: `/api/notification`
- **Driver Service**: `/api/driver`
- **Driver Details Service**: `/api/driverdetails`
- **Geo Service**: `/api/geo`

### Complex Services
- **Create Booking**: `/api/create`
- **Accept Reallocation**: `/api/accept-reallocation`
- **Cancel Booking**: `/api/cancel`
- **Reallocate Reservation**: `/api/reallocate`
- **Driver Status**: `/api/driver-status`
- **DMS**: `/api/dms`

## Testing

To verify Kong is working correctly:

```bash
chmod +x kong/test_kong.sh
./kong/test_kong.sh
```

The test script checks if all services are accessible and returns their health status.

## Kong Management Interfaces

- **Kong Gateway**: http://localhost:8000
  - All API requests go through this port
- **Kong Admin API**: http://localhost:8001
  - Used to configure Kong programmatically
- **Kong Manager (GUI)**: http://localhost:8002
  - Web interface for Kong configuration

## Manual Configuration

If you need to manually configure services or routes:

### Add a Service
```bash
curl -i -X POST http://localhost:8001/services \
  --data name=example-service \
  --data url=http://example-service:5000
```

### Add a Route
```bash
curl -i -X POST http://localhost:8001/services/example-service/routes \
  --data name=example-route \
  --data paths=/api/example \
  --data strip_path=false
```

### List Services
```bash
curl -i http://localhost:8001/services
```

### List Routes
```bash
curl -i http://localhost:8001/routes
```

## Troubleshooting

If services are unavailable through Kong:

1. Check if Kong is running: `docker compose ps kong`
2. View Kong logs: `docker compose logs kong`
3. Check service registration: `curl http://localhost:8001/services`
4. Check route registration: `curl http://localhost:8001/routes`
5. Restart Kong setup: `./kong/kong_one_click_setup.sh`

## Adding New Services

To add a new service:

1. Add the service container to `docker-compose.yaml`
2. Update `setup_kong.sh` to include your service configuration
3. Restart Kong: `docker compose restart kong-setup` 