#!/bin/bash

###############################################################################
# ILP English Pronunciation Portal - Docker Deployment Script
# This script automates the deployment process on a new server
###############################################################################

set -e  # Exit on error

echo "======================================================================"
echo "  ILP English Pronunciation Portal - Docker Deployment"
echo "======================================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_warning "This script should be run as root for Docker installation"
    print_info "You can run: sudo ./deploy.sh"
fi

# Step 1: Check Docker installation
print_info "Step 1: Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_warning "Docker not found. Installing Docker..."

    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    fi

    if [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        print_info "Detected CentOS/RHEL. Installing Docker..."
        yum install -y yum-utils
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        print_info "Detected Ubuntu/Debian. Installing Docker..."
        apt-get update
        apt-get install -y ca-certificates curl gnupg
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    else
        print_error "Unsupported OS. Please install Docker manually from https://docs.docker.com/engine/install/"
        exit 1
    fi

    print_info "Starting Docker service..."
    systemctl start docker
    systemctl enable docker
    print_info "Docker installed successfully!"
else
    print_info "Docker is already installed: $(docker --version)"
fi

# Step 2: Load Docker images
print_info "Step 2: Loading Docker images..."

if [ -f "ilp-backend.tar" ]; then
    print_info "Loading backend image..."
    docker load -i ilp-backend.tar
    print_info "Backend image loaded successfully!"
else
    print_error "Backend image file (ilp-backend.tar) not found!"
    exit 1
fi

if [ -f "ilp-frontend.tar" ]; then
    print_info "Loading frontend image..."
    docker load -i ilp-frontend.tar
    print_info "Frontend image loaded successfully!"
else
    print_error "Frontend image file (ilp-frontend.tar) not found!"
    exit 1
fi

if [ -f "postgres-15-alpine.tar" ]; then
    print_info "Loading PostgreSQL image..."
    docker load -i postgres-15-alpine.tar
    print_info "PostgreSQL image loaded successfully!"
else
    print_error "PostgreSQL image file (postgres-15-alpine.tar) not found!"
    exit 1
fi

# Step 3: Verify images
print_info "Step 3: Verifying loaded images..."
docker images | grep -E "ilp-backend|ilp-frontend|postgres"

# Step 4: Set up environment
print_info "Step 4: Setting up environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Created .env file from .env.example"
        print_warning "⚠️  IMPORTANT: Edit .env and set your AZURE_SPEECH_KEY before starting services!"
    else
        print_error ".env.example not found. Please create a .env file manually."
        exit 1
    fi
else
    print_info ".env file already exists"
fi

# Step 5: Create Docker network and volumes
print_info "Step 5: Cleaning up any existing resources..."
# Docker Compose will create the network with proper labels
# Docker Compose will create volumes if needed
# Docker Compose will create volumes if needed

# Step 6: Start containers
print_info "Step 6: Starting containers..."
docker compose up -d

# Step 7: Wait for services to be healthy
print_info "Step 7: Waiting for services to start..."
sleep 10

# Step 8: Check container status
print_info "Step 8: Checking container status..."
docker compose ps

echo ""
echo "======================================================================"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo "======================================================================"
echo ""
echo "Services are running:"
echo "  • Frontend:    http://$(hostname -I | awk '{print $1}')"
echo "  • Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "  • API Docs:    http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "Useful commands:"
echo "  • View logs:       docker compose logs -f"
echo "  • Stop services:   docker compose stop"
echo "  • Restart:         docker compose restart"
echo "  • Remove all:      docker compose down -v"
echo ""
print_warning "Remember to configure your AZURE_SPEECH_KEY in .env file!"
echo ""