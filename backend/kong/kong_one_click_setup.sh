#!/bin/bash

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      Kong API Gateway Setup Tool       ${NC}"
echo -e "${BLUE}========================================${NC}"

# Restart Kong containers to ensure a clean setup
echo -e "\n${YELLOW}Step 1: Restarting Kong containers...${NC}"
docker compose stop kong-database kong-migration kong kong-setup
docker compose rm -f kong-database kong-migration kong kong-setup

# Start Kong components
echo -e "\n${YELLOW}Step 2: Starting Kong components...${NC}"
docker compose up -d kong-database
echo "Waiting for Kong database to be ready..."
sleep 10

docker compose up -d kong-migration
echo "Running Kong migrations..."
sleep 10

docker compose up -d kong
echo "Starting Kong API Gateway..."
sleep 5

# Run the setup script
echo -e "\n${YELLOW}Step 3: Setting up Kong routes and services...${NC}"
docker compose up -d kong-setup
echo "Kong setup running in the background..."
echo "You can check setup logs with: docker compose logs -f kong-setup"

# Wait a bit for routes to be configured
echo -e "\n${YELLOW}Waiting for setup to complete...${NC}"
sleep 15

# Run the test script
echo -e "\n${YELLOW}Step 4: Testing Kong configuration...${NC}"
./test_kong.sh

# Display information
echo -e "\n${GREEN}Kong setup complete!${NC}"
echo -e "Kong API Gateway         : ${BLUE}http://localhost:8000${NC}"
echo -e "Kong Admin API           : ${BLUE}http://localhost:8001${NC}"
echo -e "Kong Manager (GUI)       : ${BLUE}http://localhost:8002${NC}"
echo -e "\n${YELLOW}To access your services, use:${NC}"
echo -e "${BLUE}http://localhost:8000/api/<service-path>${NC}"
echo -e "Example: ${BLUE}http://localhost:8000/api/restaurants${NC}" 