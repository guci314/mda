#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting PIM Execution Engine...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose is not available. Please install Docker Compose.${NC}"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
fi

# Build and start containers
echo -e "${GREEN}Building and starting containers...${NC}"
docker compose up -d --build

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check health
echo -e "${GREEN}Checking engine health...${NC}"
curl -s http://localhost:8001/health | python -m json.tool

echo -e "\n${GREEN}PIM Engine is ready!${NC}"
echo -e "- API: ${YELLOW}http://localhost:8001${NC}"
echo -e "- Docs: ${YELLOW}http://localhost:8001/docs${NC}"
echo -e "- Adminer: ${YELLOW}http://localhost:8080${NC}"
echo -e "\nTo view logs: ${YELLOW}docker compose logs -f pim-engine${NC}"
echo -e "To stop: ${YELLOW}docker compose down${NC}"