#!/bin/bash

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test service health endpoint and display detailed response
test_health() {
  local service_name=$1
  local endpoint=$2
  
  echo -e "${YELLOW}Testing ${service_name} health...${NC}"
  
  # Make the request and capture both status code and response body
  response=$(curl -s http://localhost:8000${endpoint})
  status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000${endpoint})
  
  if [ "$status_code" = "200" ]; then
    echo -e "${GREEN}✓ ${service_name} - HEALTHY (Status: ${status_code})${NC}"
    echo -e "${BLUE}  Response: ${response}${NC}"
    return 0
  else
    echo -e "${RED}✗ ${service_name} - UNHEALTHY (Status: ${status_code})${NC}"
    if [ ! -z "$response" ]; then
      echo -e "${BLUE}  Response: ${response}${NC}"
    fi
    return 1
  fi
}

# Start tests
echo "============================================="
echo "Testing all microservices health through Kong"
echo "============================================="

# Track test results
passed=0
failed=0

echo -e "\n${YELLOW}SIMPLE SERVICES${NC}"
echo "------------------------------------------"

# Test simple services
if test_health "User Service" "/api/user/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Restaurant Service" "/api/restaurant/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Reservation Service" "/api/reservation/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Menu Service" "/api/menu/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Order Service" "/api/order/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Payment Service" "/api/payment/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Notification Service" "/api/notification/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Driver Service" "/api/driver/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Driver Details Service" "/api/driverdetails/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Geo Service" "/api/geo/health"; then
  ((passed++))
else
  ((failed++))
fi

echo -e "\n${YELLOW}COMPOSITE SERVICES${NC}"
echo "------------------------------------------"

if test_health "Create Booking Service" "/api/create/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Accept Reallocation Service" "/api/accept-reallocation/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Cancel Booking Service" "/api/cancel/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Reallocate Reservation Service" "/api/reallocate/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "Driver Status Service" "/api/driver-status/health"; then
  ((passed++))
else
  ((failed++))
fi

if test_health "DMS Service" "/api/dms/health"; then
  ((passed++))
else
  ((failed++))
fi

# Print summary
echo -e "\n============================================="
echo "Test Summary:"
echo "${GREEN}${passed} services healthy${NC}"
echo "${RED}${failed} services unhealthy${NC}"
echo "============================================="

if [ $failed -eq 0 ]; then
  echo -e "${GREEN}All services are healthy! Kong is configured correctly.${NC}"
  exit 0
else
  echo -e "${YELLOW}Some services are unhealthy. Check your service logs or Kong configuration.${NC}"
  exit 1
fi