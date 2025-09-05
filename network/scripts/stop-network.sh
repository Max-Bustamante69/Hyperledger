#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping University Room Reservation Network${NC}"

# Set the working directory
cd "$(dirname "$0")/.."

# Stop and remove containers
echo -e "${YELLOW}Stopping containers...${NC}"
docker-compose down --volumes --remove-orphans

# Remove chaincode images
echo -e "${YELLOW}Removing chaincode images...${NC}"
docker rmi $(docker images | grep "dev-peer" | awk '{print $3}') 2>/dev/null || true

# Clean up crypto material (optional - comment out if you want to keep it)
echo -e "${YELLOW}Cleaning up crypto material...${NC}"
rm -rf crypto-config
rm -rf channel-artifacts
rm -f *.tar.gz

# Clean up docker volumes
echo -e "${YELLOW}Cleaning up docker volumes...${NC}"
docker volume prune -f

echo -e "${GREEN}Network stopped and cleaned up successfully!${NC}"

