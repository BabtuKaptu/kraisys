#!/bin/bash

# 🚀 KRAI v0.7.1 Auto-Deploy Script
# This script automatically deploys KRAI to Ubuntu server

set -e  # Exit on any error

echo "🚀 Starting KRAI v0.7.1 deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get server IP
SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
log_info "Detected server IP: $SERVER_IP"

# Step 1: System Update
log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
log_success "System updated"

# Step 2: Install dependencies
log_info "Installing required packages..."
sudo apt install -y postgresql postgresql-contrib nginx python3 python3-pip python3-venv git nodejs npm curl
log_success "Dependencies installed"

# Step 3: Setup PostgreSQL
log_info "Setting up PostgreSQL database..."

# Generate secure password
DB_PASSWORD=$(openssl rand -base64 32)
log_info "Generated secure database password"

# Create database and user
sudo -u postgres psql <<EOF
CREATE USER krai_user WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE krai_mrp_v06 OWNER krai_user;
GRANT ALL PRIVILEGES ON DATABASE krai_mrp_v06 TO krai_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO krai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO krai_user;
EOF

log_success "Database configured"

# Step 4: Clone and setup application
log_info "Cloning KRAI repository..."
cd /opt
sudo rm -rf krai || true
sudo git clone https://github.com/BabtuKaptu/kraisys.git krai
sudo chown -R $USER:$USER /opt/krai
cd /opt/krai

log_success "Repository cloned"

# Step 5: Setup backend
log_info "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create production environment file
cat > .env <<EOF
# KRAI v0.7.1 Production Configuration
DATABASE_URL=postgresql://krai_user:$DB_PASSWORD@localhost:5432/krai_mrp_v06

# Basic Authentication
ENABLE_BASIC_AUTH=true
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=KraiSystem2024!SecurePassword

# CORS
ALLOWED_HOSTS=["http://$SERVER_IP", "https://$SERVER_IP"]

# FastAPI
API_V1_STR=/api/v1
PROJECT_NAME=KRAI Production System
VERSION=0.7.1
EOF

# Initialize database
log_info "Initializing database..."
python3 -c "from app.db.init_db import init_database; import asyncio; asyncio.run(init_database())"
log_success "Database initialized"

# Step 6: Setup frontend
log_info "Setting up frontend..."
cd ../frontend
npm install

# Configure frontend API URL
echo "VITE_API_URL=http://$SERVER_IP/api/v1" > .env

# Build frontend
npm run build
log_success "Frontend built"

# Step 7: Create systemd service
log_info "Creating systemd service..."
sudo tee /etc/systemd/system/krai-backend.service > /dev/null <<EOF
[Unit]
Description=KRAI Backend Service
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/krai/backend
Environment=PATH=/opt/krai/backend/venv/bin
ExecStart=/opt/krai/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable krai-backend
sudo systemctl start krai-backend

log_success "Backend service started"

# Step 8: Configure Nginx
log_info "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/krai > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_IP _;
    
    # Frontend static files
    location / {
        root /opt/krai/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Docs
    location /docs {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
    }
    
    location /redoc {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/krai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

log_success "Nginx configured"

# Step 9: Setup firewall
log_info "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

log_success "Firewall configured"

# Step 10: Final verification
log_info "Verifying deployment..."
sleep 5

# Check services
if sudo systemctl is-active --quiet krai-backend; then
    log_success "Backend service is running"
else
    log_error "Backend service failed to start"
    sudo journalctl -u krai-backend --no-pager -n 20
fi

if sudo systemctl is-active --quiet nginx; then
    log_success "Nginx is running"
else
    log_error "Nginx failed to start"
fi

if sudo systemctl is-active --quiet postgresql; then
    log_success "PostgreSQL is running"
else
    log_error "PostgreSQL failed to start"
fi

# Test HTTP response
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
    log_success "Application is responding"
else
    log_warning "Application may not be responding correctly"
fi

# Final summary
echo ""
echo "🎉 KRAI v0.7.1 deployment completed!"
echo ""
echo "📋 Access Information:"
echo "   URL: http://$SERVER_IP"
echo "   Username: admin"
echo "   Password: KraiSystem2024!SecurePassword"
echo ""
echo "🔐 Database credentials (save these!):"
echo "   Database: krai_mrp_v06"
echo "   Username: krai_user"
echo "   Password: $DB_PASSWORD"
echo ""
echo "🛠️ Useful commands:"
echo "   Check backend: sudo systemctl status krai-backend"
echo "   View logs: sudo journalctl -u krai-backend -f"
echo "   Restart: sudo systemctl restart krai-backend"
echo ""
echo "🚨 IMPORTANT: Change the default admin password in production!"
echo "   Edit: /opt/krai/backend/.env"
echo "   Restart: sudo systemctl restart krai-backend"
echo ""

log_success "Deployment completed successfully! 🚀"
