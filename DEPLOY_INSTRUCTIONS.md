# 🚀 KRAI v0.7.1 Deployment Guide

## 📋 Overview
This guide will help you deploy KRAI v0.7.1 to your Ubuntu Linux server with HTTP Basic Authentication enabled.

## 🛡️ Security Features
- **HTTP Basic Authentication** protects your application
- **PostgreSQL database** with secure user credentials
- **Nginx reverse proxy** for optimal performance

## 📦 What You'll Need
- Ubuntu Linux server (minimal specs: 1 core, 1GB RAM)
- SSH access to the server
- Root or sudo privileges

## 🎯 Quick Access After Deployment
- **URL**: `http://YOUR_SERVER_IP` 
- **Login**: `admin`
- **Password**: `KraiSystem2024!SecurePassword`

---

## 🔧 Step 1: Server Preparation

### Connect to your server:
```bash
ssh your_username@YOUR_SERVER_IP
```

### Update system:
```bash
sudo apt update && sudo apt upgrade -y
```

### Install required packages:
```bash
sudo apt install -y postgresql postgresql-contrib nginx python3 python3-pip python3-venv git nodejs npm
```

---

## 🗄️ Step 2: Database Setup

### Create database and user:
```bash
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE USER krai_user WITH PASSWORD 'change-me-to-secure-password';
CREATE DATABASE krai_mrp_v06 OWNER krai_user;
GRANT ALL PRIVILEGES ON DATABASE krai_mrp_v06 TO krai_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO krai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO krai_user;
\q
```

### Test database connection:
```bash
psql -h localhost -U krai_user -d krai_mrp_v06
# Enter password when prompted, then \q to exit
```

---

## 📥 Step 3: Deploy Application

### Clone repository:
```bash
cd /opt
sudo git clone https://github.com/BabtuKaptu/kraisys.git krai
sudo chown -R $USER:$USER /opt/krai
cd /opt/krai
```

### Setup backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure environment:
```bash
cp env.production.example .env
nano .env
```

Edit `.env` file:
```bash
# Database
DATABASE_URL=postgresql://krai_user:your_secure_password@localhost:5432/krai_mrp_v06

# Basic Authentication
ENABLE_BASIC_AUTH=true
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=KraiSystem2024!SecurePassword

# CORS (replace with your server IP)
ALLOWED_HOSTS=["http://YOUR_SERVER_IP", "https://YOUR_SERVER_IP"]
```

### Initialize database:
```bash
python3 -c "from app.db.init_db import init_database; import asyncio; asyncio.run(init_database())"
```

### Setup frontend:
```bash
cd ../frontend
npm install
```

### Update frontend API URL:
```bash
echo "VITE_API_URL=http://YOUR_SERVER_IP/api/v1" > .env
```

### Build frontend:
```bash
npm run build
```

---

## ⚙️ Step 4: System Services

### Create systemd service for backend:
```bash
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
```

### Enable and start backend service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable krai-backend
sudo systemctl start krai-backend
sudo systemctl status krai-backend
```

---

## 🌐 Step 5: Nginx Configuration

### Create Nginx configuration:
```bash
sudo tee /etc/nginx/sites-available/krai > /dev/null <<EOF
server {
    listen 80;
    server_name YOUR_SERVER_IP;
    
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
        
        # Handle CORS preflight
        if (\$request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }
    
    # Docs (protected by basic auth)
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
```

### Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/krai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 🎯 Step 6: Final Verification

### Check services:
```bash
sudo systemctl status krai-backend
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Test application:
```bash
curl -I http://YOUR_SERVER_IP
# Should return 200 OK

curl -u admin:KraiSystem2024!SecurePassword http://YOUR_SERVER_IP/api/v1/models
# Should return JSON data
```

---

## 🌐 Access Your Application

1. **Open browser** and go to: `http://YOUR_SERVER_IP`
2. **Enter credentials**:
   - Username: `admin`
   - Password: `KraiSystem2024!SecurePassword`
3. **Start using KRAI** - create models, materials, manage warehouse!

---

## 🛡️ Security Recommendations

### Change default password:
```bash
cd /opt/krai/backend
nano .env
# Change BASIC_AUTH_PASSWORD to something more secure
sudo systemctl restart krai-backend
```

### Enable firewall:
```bash
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### Regular updates:
```bash
cd /opt/krai
git pull origin main
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install && npm run build
sudo systemctl restart krai-backend
```

---

## 🚨 Troubleshooting

### Backend not starting:
```bash
sudo journalctl -u krai-backend -f
```

### Database connection issues:
```bash
sudo -u postgres psql -c "\l"  # List databases
sudo systemctl status postgresql
```

### Nginx issues:
```bash
sudo nginx -t  # Test configuration
sudo journalctl -u nginx -f
```

### View application logs:
```bash
tail -f /opt/krai/backend/logs/observer.log
```

---

## 📞 Support

If you encounter issues:
1. Check service logs: `sudo journalctl -u krai-backend -f`
2. Verify database connectivity
3. Ensure all environment variables are set correctly
4. Check firewall settings

**Your KRAI v0.7.1 system is now ready for production use!** 🎉
