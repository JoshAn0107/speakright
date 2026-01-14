# Manual Deployment Guide - ILP Pronunciation Portal

This guide provides step-by-step instructions for manually deploying the ILP Pronunciation Portal without using the automated `deploy.sh` script.

Use this guide if:
- `deploy.sh` fails or encounters errors
- You prefer manual control over the deployment process
- You need to customize the deployment for your environment

---

## Prerequisites Check

Before starting, verify you have:
- Root or sudo access
- At least 2GB RAM and 5GB disk space
- Ports 80, 8000, and 5432 available
- Internet connection

```bash
# Check available resources
free -h         # Check RAM
df -h           # Check disk space
whoami          # Verify user (should be root or have sudo)
```

---

## Step 1: Install Docker

### For Ubuntu/Debian Systems

```bash
# Update package index
sudo apt-get update

# Install required packages
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
sudo apt-get update

# Install Docker Engine and Docker Compose
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
sudo docker --version
sudo docker compose version
```

### For CentOS/RHEL Systems

```bash
# Install required packages
sudo yum install -y yum-utils

# Add Docker repository
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker Engine and Docker Compose
sudo yum install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
sudo docker --version
sudo docker compose version
```

### Verify Docker Installation

```bash
# Test Docker is working
sudo docker run hello-world

# You should see a "Hello from Docker!" message
```

---

## Step 2: Navigate to Deployment Directory

```bash
# Navigate to the docker-deployment folder
cd /path/to/docker-deployment

# Verify all required files are present
ls -lh

# You should see:
# - ilp-backend.tar (approximately 96-100 MB)
# - ilp-frontend.tar (approximately 22-25 MB)
# - postgres-15-alpine.tar (approximately 105-110 MB)
# - docker-compose.yml
# - .env.example
```

---

## Step 3: Load Docker Images

Load each Docker image from the tar files:

```bash
# Load backend image
sudo docker load -i ilp-backend.tar

# Expected output:
# Loaded image: ilp-backend:latest

# Load frontend image
sudo docker load -i ilp-frontend.tar

# Expected output:
# Loaded image: ilp-frontend:latest

# Load PostgreSQL image
sudo docker load -i postgres-15-alpine.tar

# Expected output:
# Loaded image: postgres:15-alpine
```

### Verify Images are Loaded

```bash
# List all Docker images
sudo docker images

# You should see three images:
# - ilp-backend        latest
# - ilp-frontend       latest
# - postgres           15-alpine
```

---

### Verify .env File

```bash
# Check that .env exists and has content
cat .env

---

## Step 5: Review docker-compose.yml

```bash
# View the docker-compose configuration
cat docker-compose.yml
```

The file should define three services:
- `ilp-postgres` - Database on port 5432
- `ilp-backend` - API server on port 8000
- `ilp-frontend` - Web interface on port 80

**If you need to modify ports**, edit docker-compose.yml:
```bash
nano docker-compose.yml
```

---

## Step 6: Start Docker Containers

```bash
# Start all containers in detached mode
sudo docker compose up -d

# Expected output:
# [+] Running 4/4
#  ✔ Network docker-deployment_default        Created
#  ✔ Container ilp-postgres                   Started
#  ✔ Container ilp-backend                    Started
#  ✔ Container ilp-frontend                   Started
```

### What This Command Does:
1. Creates a Docker network for the services
2. Creates and starts the PostgreSQL container
3. Creates and starts the backend API container
4. Creates and starts the frontend web server container
5. Sets up volume mounts for data persistence

---

## Step 7: Verify Deployment

### Check Container Status

```bash
# View running containers
sudo docker compose ps

# Expected output:
# NAME            IMAGE                  STATUS          PORTS
# ilp-backend     ilp-backend:latest     Up 30 seconds   0.0.0.0:8000->8000/tcp
# ilp-frontend    ilp-frontend:latest    Up 30 seconds   0.0.0.0:80->80/tcp
# ilp-postgres    postgres:15-alpine     Up 30 seconds   0.0.0.0:5432->5432/tcp
```

All containers should show `Up` status.

### Check Container Logs

```bash
# View all logs
sudo docker compose logs

# View specific service logs
sudo docker compose logs ilp-backend
sudo docker compose logs ilp-frontend
sudo docker compose logs ilp-postgres

# Follow logs in real-time
sudo docker compose logs -f
```

### Check Database Initialization

```bash
# The backend should automatically create database tables
# Check backend logs for "Database initialized" or similar message
sudo docker compose logs ilp-backend | grep -i "database"

# Wait 30-60 seconds for database to be ready
sleep 30
```

---

## Step 8: Test the Application

### Test Backend API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}

# Test API documentation (from browser or curl)
curl http://localhost:8000/docs

# Should return HTML content
```

### Test Frontend

```bash
# Test frontend (from browser)
# Visit: http://your-server-ip

# Or test with curl
curl http://localhost:80

# Should return HTML content
```

### Test from External Machine

From your local computer (not the server):
```bash
# Replace YOUR_SERVER_IP with actual IP
curl http://YOUR_SERVER_IP:8000/health

# Open in browser:
# http://YOUR_SERVER_IP
```



## Step 9: Configure Firewall (If Applicable)

### For UFW (Ubuntu)

```bash
# Allow HTTP (port 80)
sudo ufw allow 80/tcp

# Allow backend API (port 8000)
sudo ufw allow 8000/tcp

# Enable firewall if not already enabled
sudo ufw enable

# Check status
sudo ufw status
```

### For firewalld (CentOS/RHEL)

```bash
# Allow HTTP (port 80)
sudo firewall-cmd --permanent --add-port=80/tcp

# Allow backend API (port 8000)
sudo firewall-cmd --permanent --add-port=8000/tcp

# Reload firewall
sudo firewall-cmd --reload

# Check status
sudo firewall-cmd --list-ports
```

---

## Common Issues and Solutions

### Issue 1: Container Won't Start

```bash
# Check detailed logs
sudo docker compose logs ilp-backend

# Common causes:
# - Missing AZURE_SPEECH_KEY in .env
# - Database not ready yet (wait 60 seconds)
# - Port already in use

# Check ports
sudo netstat -tuln | grep -E ':(80|8000|5432)'

# Stop conflicting services
sudo systemctl stop httpd
sudo systemctl stop nginx
```

### Issue 2: Database Connection Failed

```bash
# Wait for database to initialize (can take 30-60 seconds)
sleep 30

# Restart backend
sudo docker compose restart ilp-backend

# Check database is healthy
sudo docker compose ps ilp-postgres
```

### Issue 3: Permission Errors

```bash
# Ensure you're using sudo
sudo docker compose up -d

# Or add your user to docker group (requires re-login)
sudo usermod -aG docker $USER
# Log out and back in
```

### Issue 4: "Image Not Found" Error

```bash
# Verify images are loaded
sudo docker images | grep -E "ilp|postgres"

# If missing, reload the tar files
sudo docker load -i ilp-backend.tar
sudo docker load -i ilp-frontend.tar
sudo docker load -i postgres-15-alpine.tar
```

### Issue 5: Frontend Shows "Cannot Connect to Backend"

```bash
# Check backend is running
sudo docker compose ps ilp-backend

# Check backend logs
sudo docker compose logs ilp-backend

# Verify backend is accessible
curl http://localhost:8000/health

# Check CORS settings in .env
grep FRONTEND_URL .env
```

---

## Useful Management Commands

### Viewing Logs

```bash
# All services
sudo docker compose logs -f

# Specific service
sudo docker compose logs -f ilp-backend

# Last 100 lines
sudo docker compose logs --tail=100
```

### Restarting Services

```bash
# Restart all
sudo docker compose restart

# Restart specific service
sudo docker compose restart ilp-backend
```

### Stopping Services

```bash
# Stop all containers
sudo docker compose stop

# Start again
sudo docker compose start
```

### Updating Configuration

```bash
# After editing .env, restart services
nano .env
sudo docker compose restart
```

### Database Backup

```bash
# Backup database
sudo docker exec ilp-postgres pg_dump -U ilp_user ilp_db > backup.sql

# Restore database
cat backup.sql | sudo docker exec -i ilp-postgres psql -U ilp_user ilp_db
```

### Complete Removal

```bash
# Stop and remove all containers, networks, volumes
sudo docker compose down -v

# Remove images (if needed)
sudo docker rmi ilp-backend:latest ilp-frontend:latest postgres:15-alpine
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Changed `POSTGRES_PASSWORD` from default
- [ ] Generated new `SECRET_KEY` with `openssl rand -hex 32`
- [ ] Set `DEBUG=False` in .env
- [ ] Added valid `AZURE_SPEECH_KEY`
- [ ] Updated `FRONTEND_URL` with actual domain/IP
- [ ] Configured firewall rules
- [ ] Set up SSL/HTTPS (use nginx proxy or Certbot)
- [ ] Configured backup strategy for database
- [ ] Set up monitoring/logging
- [ ] Tested all functionality
- [ ] Documented any custom configurations

---

## Success Indicators

Your deployment is successful when:

1. **All containers are running:**
   ```bash
   sudo docker compose ps
   # All show "Up" status
   ```

2. **Backend API responds:**
   ```bash
   curl http://localhost:8000/health
   # Returns: {"status":"healthy"}
   ```

3. **Frontend loads:**
   - Open browser to `http://your-server-ip`
   - See the login/registration page

4. **No errors in logs:**
   ```bash
   sudo docker compose logs
   # No ERROR or CRITICAL messages
   ```

5. **Can register and login:**
   - Register a new user through the web interface
   - Login successfully

---

## Getting Help

If you encounter issues:

1. Check logs: `sudo docker compose logs -f`
2. Verify .env configuration: `cat .env`
3. Check container status: `sudo docker compose ps`
4. Verify network connectivity: `curl http://localhost:8000/health`
5. Review this guide's troubleshooting section

---

**Deployment Complete!** 

Visit `http://your-server-ip` to access your ILP Pronunciation Portal.
