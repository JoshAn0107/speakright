#  ILP Pronunciation Portal - Docker Deployment Package

This package contains everything you need to deploy the ILP English Pronunciation Portal on a new server.
You can visit https://speakright.uk to try things out without needing to deploy
It is strongly recommended that this project should be build on linux machine like a dice machine.
All the work should be done in docker-deployment folder.
This readme is a copy of readme in docker-deployment folder.

## What This Deploys

Three separate Docker containers:

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| **Frontend** | `ilp-frontend` | 80 | React + Nginx web interface |
| **Backend** | `ilp-backend` | 8000 | FastAPI REST API server |
| **Database** | `ilp-postgres` | 5432 | PostgreSQL 15 database |


##  Requirements (Check These FIRST)

**Before starting deployment, ensure you have:**

### System Requirements
- **Operating System**:
  - Linux server (CentOS/RHEL 7+, Ubuntu 18.04+, or Debian 10+)
- **Privileges**: Root or sudo access (Administrator for Windows)
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk Space**: Minimum 5GB free space
- **Network**: Internet connection for initial setup
- **Ports Available**: 80 (frontend), 8000 (backend), 5432 (database)

### Prerequisites
- **Docker**: Version 20.10 or higher
  - Linux: `deploy.sh` will install it automatically
  - Windows: Docker Desktop with WSL2 backend (see Windows/WSL section below)
  - Manual installation: https://docs.docker.com/engine/install/
- **Azure Speech Service Key**: Required for pronunciation assessment, I have put my key in the .env file it should work without needing you getting one
  - Get free key at: https://portal.azure.com/ → Create Speech Service
  - Region: France Central (default) or your preferred region

### Check Ports
```bash
sudo netstat -tuln | grep -E ':(80|8000|5432) '
# If any ports show up, you need to stop those services first
```

###  Run Deployment Script
```bash
# SSH into your server
ssh user@your-server-ip

# Navigate to deployment directory
cd docker-deployment

# Make deploy script executable (if needed)
chmod +x deploy.sh

# Run deployment script with sudo
sudo ./deploy.sh
```


**The `deploy.sh` script will:**
1. Check if Docker is installed (install if missing on Linux)
2. Load all Docker images from .tar files
3. Create `.env` file from template
4. Start all containers using docker compose





##  Configuration

**Required environment variables in `.env`:**
- `AZURE_SPEECH_KEY` - Get from https://portal.azure.com/
- `AZURE_REGION` - Default: `francecentral`

**Recommended for production:**
- Change `POSTGRES_PASSWORD` from default
- Generate new `SECRET_KEY` with `openssl rand -hex 32`
- Set `DEBUG=False`

##  Useful Commands

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f ilp-backend
docker compose logs -f ilp-frontend

# Check container status
docker compose ps

# Restart services
docker compose restart

# Restart specific service
docker compose restart ilp-backend

# Stop services
docker compose stop

# Start services
docker compose start

# Remove everything (WARNING: deletes data)
docker compose down -v
```

##  Troubleshooting -Some error that I encountered

### Common Error 1: Permission Denied
```bash
# Error: "Permission denied when running deploy.sh"
# Solution: Make script executable and run with sudo
chmod +x deploy.sh
sudo ./deploy.sh
```

### Common Error 2: Docker Command Not Found After Installation
```bash
# Error: "docker: command not found" even after deploy.sh ran
# Solution: Reload shell or re-login
source ~/.bashrc
# OR
exit  # then SSH back in
```

### Common Error 3: Port Already in Use
```bash
# Error: "port is already allocated"
# Solution: Check what's using the port
sudo netstat -tuln | grep -E ':(80|8000|5432)'
# Stop conflicting service, e.g.:
sudo systemctl stop httpd    # If Apache is on port 80
sudo systemctl stop nginx    # If Nginx is on port 80
```

### Common Error 4: Image Load Failed
```bash
# Error: "cannot load image from ilp-backend.tar"
# Solution: Verify tar files exist and are not corrupted
ls -lh *.tar
# If corrupted, re-download the deployment package
```

### Common Error 5: Container Exits Immediately
```bash
# Check why container exited
docker compose logs ilp-backend
docker compose logs ilp-frontend

# Common cause: Missing or invalid .env configuration
# Solution: Verify .env file exists and has valid values
cat .env
```

### Common Error 6: Database Connection Failed
```bash
# Error in backend logs: "could not connect to database"
# Solution: Wait for database to initialize (30-60 seconds)
docker compose ps  # Check postgres is "healthy"

# If still failing, restart backend
docker compose restart ilp-backend
```


### Manual Deployment (If deploy.sh Completely Fails)

If `deploy.sh` fails, refer to the comprehensive **[MANUAL_DEPLOY.md](./MANUAL_DEPLOY.md)** guide for complete step-by-step instructions.

**Quick manual deployment:**

```bash
# 1. Install Docker manually
# For Ubuntu/Debian:
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker

# For CentOS/RHEL:
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker

# 2. Load images manually
sudo docker load -i ilp-backend.tar
sudo docker load -i ilp-frontend.tar
sudo docker load -i postgres-15-alpine.tar

# 3. Create .env file
cp .env.example .env
nano .env  # Edit to add your AZURE_SPEECH_KEY

# 4. Start services
sudo docker compose up -d

# 5. Check status
sudo docker compose ps
sudo docker compose logs -f
```

**📖 For detailed manual deployment with troubleshooting, see [MANUAL_DEPLOY.md](./MANUAL_DEPLOY.md)**