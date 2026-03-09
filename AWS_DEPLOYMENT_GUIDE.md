# AWS Deployment Guide - GramSense AI

Complete guide for deploying GramSense AI to AWS EC2.

---

## Prerequisites

- AWS Account with Free Tier access
- AWS CLI installed locally
- SSH client (PuTTY for Windows, built-in for Mac/Linux)
- Git installed
- Basic Linux command line knowledge

---

## Section 4.1: AWS Account Setup

### 4.1.1 Verify AWS Account and Credits

1. Log in to [AWS Console](https://console.aws.amazon.com/)
2. Check Free Tier eligibility:
   - Navigate to Billing Dashboard
   - Verify Free Tier status
   - Check available credits (if any)

### 4.1.2 Create IAM User with Appropriate Permissions

```bash
# Required permissions for deployment:
- AmazonEC2FullAccess
- AmazonVPCFullAccess
- IAMReadOnlyAccess
```

**Steps:**
1. Go to IAM Console → Users → Add User
2. Username: `gramsense-deployer`
3. Access type: Programmatic access + AWS Management Console access
4. Attach policies: `AmazonEC2FullAccess`
5. Download credentials CSV

### 4.1.3 Generate and Secure Access Keys

1. In IAM Console, select your user
2. Security credentials tab → Create access key
3. Download and save securely:
   - Access Key ID
   - Secret Access Key
4. **NEVER commit these to Git!**

### 4.1.4 Configure AWS CLI Locally

```bash
# Install AWS CLI (if not installed)
# Windows: Download from https://aws.amazon.com/cli/
# Mac: brew install awscli
# Linux: sudo apt install awscli

# Configure AWS CLI
aws configure

# Enter when prompted:
AWS Access Key ID: [YOUR_ACCESS_KEY]
AWS Secret Access Key: [YOUR_SECRET_KEY]
Default region name: us-east-1
Default output format: json

# Verify configuration
aws sts get-caller-identity
```

---

## Section 4.2: EC2 Instance Setup

### 4.2.1 Launch EC2 t3.micro Instance (Free Tier)

```bash
# Using AWS CLI
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.micro \
    --key-name gramsense-key \
    --security-group-ids sg-xxxxxxxxx \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=GramSense-AI}]'
```

**Or via AWS Console:**
1. EC2 Dashboard → Launch Instance
2. Name: `GramSense-AI`
3. AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
4. Instance type: t3.micro
5. Proceed to next steps

### 4.2.2 Configure Security Group (ports 22, 80, 443, 8000)

```bash
# Create security group
aws ec2 create-security-group \
    --group-name gramsense-sg \
    --description "Security group for GramSense AI"

# Add inbound rules
aws ec2 authorize-security-group-ingress \
    --group-name gramsense-sg \
    --protocol tcp --port 22 --cidr 0.0.0.0/0  # SSH

aws ec2 authorize-security-group-ingress \
    --group-name gramsense-sg \
    --protocol tcp --port 80 --cidr 0.0.0.0/0  # HTTP

aws ec2 authorize-security-group-ingress \
    --group-name gramsense-sg \
    --protocol tcp --port 443 --cidr 0.0.0.0/0  # HTTPS

aws ec2 authorize-security-group-ingress \
    --group-name gramsense-sg \
    --protocol tcp --port 8000 --cidr 0.0.0.0/0  # FastAPI
```

**Or via AWS Console:**
1. EC2 → Security Groups → Create security group
2. Add inbound rules:
   - SSH (22) from 0.0.0.0/0
   - HTTP (80) from 0.0.0.0/0
   - HTTPS (443) from 0.0.0.0/0
   - Custom TCP (8000) from 0.0.0.0/0

### 4.2.3 Create and Download SSH Key Pair

```bash
# Create key pair
aws ec2 create-key-pair \
    --key-name gramsense-key \
    --query 'KeyMaterial' \
    --output text > gramsense-key.pem

# Set permissions (Linux/Mac)
chmod 400 gramsense-key.pem
```

**Or via AWS Console:**
1. EC2 → Key Pairs → Create key pair
2. Name: `gramsense-key`
3. File format: .pem (for Linux/Mac) or .ppk (for Windows/PuTTY)
4. Download and save securely

### 4.2.4 Allocate Elastic IP Address

```bash
# Allocate Elastic IP
aws ec2 allocate-address --domain vpc

# Associate with instance
aws ec2 associate-address \
    --instance-id i-xxxxxxxxx \
    --allocation-id eipalloc-xxxxxxxxx
```

**Or via AWS Console:**
1. EC2 → Elastic IPs → Allocate Elastic IP address
2. Select the IP → Actions → Associate Elastic IP address
3. Select your instance

### 4.2.5 Connect to Instance via SSH

```bash
# Get instance public IP
aws ec2 describe-instances \
    --instance-ids i-xxxxxxxxx \
    --query 'Reservations[0].Instances[0].PublicIpAddress'

# Connect via SSH
ssh -i gramsense-key.pem ubuntu@YOUR_ELASTIC_IP
```

---

## Section 4.3: Server Configuration

### 4.3.1 Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### 4.3.2 Install Python 3.8+ and pip

```bash
# Install Python 3.10
sudo apt install python3.10 python3.10-venv python3-pip -y

# Verify installation
python3 --version
pip3 --version
```

### 4.3.3 Install Nginx Web Server

```bash
sudo apt install nginx -y

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify Nginx is running
sudo systemctl status nginx
```

### 4.3.4 Install Git and Clone Repository

```bash
# Install Git
sudo apt install git -y

# Clone repository
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/gramsense-ai-prototype.git
cd gramsense-ai-prototype
```

### 4.3.5 Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

---

## Section 4.4: Application Deployment

### 4.4.1 Configure Environment Variables

```bash
# Create .env file
cat > .env << EOF
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
ENVIRONMENT=production
EOF

# Secure the file
chmod 600 .env
```

### 4.4.2 Set up Gunicorn for FastAPI Backend

```bash
# Install Gunicorn
pip install gunicorn

# Test Gunicorn
gunicorn backend.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Create Gunicorn config
cat > gunicorn_config.py << EOF
bind = "0.0.0.0:8000"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
accesslog = "/var/log/gramsense/access.log"
errorlog = "/var/log/gramsense/error.log"
EOF

# Create log directory
sudo mkdir -p /var/log/gramsense
sudo chown ubuntu:ubuntu /var/log/gramsense
```

### 4.4.3 Configure Nginx as Reverse Proxy

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/gramsense << EOF
server {
    listen 80;
    server_name YOUR_ELASTIC_IP;

    # Frontend
    location / {
        root /home/ubuntu/gramsense-ai-prototype/frontend;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }

    # Query assistant
    location /query_assistant {
        proxy_pass http://localhost:8000/query_assistant;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Other endpoints
    location ~ ^/(prices|forecast|recommendation|regional_demand|demand_insights) {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/gramsense /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 4.4.4 Set up systemd Service for Auto-Restart

```bash
# Create systemd service file
sudo tee /etc/systemd/system/gramsense.service << EOF
[Unit]
Description=GramSense AI FastAPI Application
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/gramsense-ai-prototype
Environment="PATH=/home/ubuntu/gramsense-ai-prototype/venv/bin"
ExecStart=/home/ubuntu/gramsense-ai-prototype/venv/bin/gunicorn backend.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start gramsense

# Enable auto-start on boot
sudo systemctl enable gramsense

# Check status
sudo systemctl status gramsense
```

### 4.4.5 Deploy Frontend Files to Nginx Web Root

```bash
# Frontend files are already in place
# Update API_BASE in frontend/index.html
sed -i "s|http://localhost:8000|http://YOUR_ELASTIC_IP|g" /home/ubuntu/gramsense-ai-prototype/frontend/index.html

# Restart Nginx
sudo systemctl restart nginx
```

---

## Section 4.5: Domain & SSL (Optional)

### 4.5.1 Configure Custom Domain

1. Purchase domain from provider (Namecheap, GoDaddy, etc.)
2. Add A record pointing to your Elastic IP
3. Update Nginx config with domain name

### 4.5.2 Install Certbot for Let's Encrypt SSL

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

### 4.5.3 Configure HTTPS Redirect

Certbot automatically configures HTTPS redirect.

---

## Section 4.6: Monitoring & Maintenance

### 4.6.1 Set up Basic Logging

```bash
# View application logs
sudo journalctl -u gramsense -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View application logs
tail -f /var/log/gramsense/access.log
tail -f /var/log/gramsense/error.log
```

### 4.6.2 Configure Log Rotation

```bash
# Create logrotate config
sudo tee /etc/logrotate.d/gramsense << EOF
/var/log/gramsense/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload gramsense > /dev/null 2>&1 || true
    endscript
}
EOF
```

### 4.6.3 Test Application Restart After Reboot

```bash
# Reboot instance
sudo reboot

# After reboot, verify services
sudo systemctl status gramsense
sudo systemctl status nginx

# Test application
curl http://YOUR_ELASTIC_IP/health
```

### 4.6.4 Document Deployment Process

This guide serves as the deployment documentation.

---

## Verification Checklist

- [ ] EC2 instance running
- [ ] Security groups configured
- [ ] Elastic IP associated
- [ ] SSH access working
- [ ] Python and dependencies installed
- [ ] Nginx configured and running
- [ ] Backend service running
- [ ] Frontend accessible
- [ ] API endpoints responding
- [ ] Logs being written
- [ ] Auto-restart on reboot working

---

## Troubleshooting

### Backend not starting
```bash
# Check logs
sudo journalctl -u gramsense -n 50

# Check if port 8000 is in use
sudo lsof -i :8000

# Restart service
sudo systemctl restart gramsense
```

### Nginx errors
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

### Cannot connect to instance
- Verify security group allows inbound traffic on port 22
- Check Elastic IP is associated
- Verify SSH key permissions (chmod 400)

---

## Cost Optimization

- Use t3.micro (Free Tier eligible)
- Stop instance when not in use
- Use Elastic IP only when instance is running
- Monitor Free Tier usage in Billing Dashboard

**Estimated Monthly Cost:** $0-$10 (within Free Tier limits)

---

## Quick Deployment Script

See `deploy.sh` for automated deployment script.

---

## Support

For issues or questions:
- Check logs: `sudo journalctl -u gramsense -f`
- Verify services: `sudo systemctl status gramsense nginx`
- Test endpoints: `curl http://YOUR_IP/health`
