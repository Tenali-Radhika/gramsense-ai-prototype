#!/bin/bash

# GramSense AI - AWS Deployment Script
# This script helps deploy the GramSense AI prototype to AWS

set -e

echo "🚀 GramSense AI - AWS Deployment Script"
echo "======================================"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'"
    echo "   unzip awscliv2.zip"
    echo "   sudo ./aws/install"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run:"
    echo "   aws configure"
    echo "   Enter your Access Key ID, Secret Access Key, region (e.g., us-east-1), and output format (json)"
    exit 1
fi

echo "✅ AWS CLI and credentials are configured"

# Get user input
read -p "Enter your AWS region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

read -p "Enter EC2 instance type (default: t3.micro): " INSTANCE_TYPE
INSTANCE_TYPE=${INSTANCE_TYPE:-t3.micro}

read -p "Enter your key pair name (for SSH access): " KEY_NAME

if [ -z "$KEY_NAME" ]; then
    echo "❌ Key pair name is required for EC2 access"
    exit 1
fi

echo "📦 Creating deployment package..."

# Create deployment directory
DEPLOY_DIR="deploy-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DEPLOY_DIR"

# Copy application files
cp -r backend "$DEPLOY_DIR/"
cp -r frontend "$DEPLOY_DIR/"
cp README.md "$DEPLOY_DIR/"
cp -r .venv "$DEPLOY_DIR/" 2>/dev/null || echo "Virtual environment not copied (will be recreated on server)"

# Create deployment script for EC2
cat > "$DEPLOY_DIR/setup.sh" << 'EOF'
#!/bin/bash
set -e

echo "🔧 Setting up GramSense AI on EC2..."

# Update system
sudo yum update -y

# Install Python 3.8+ if not available
if ! python3 --version &> /dev/null; then
    sudo yum install -y python3 python3-pip
fi

# Install required packages
sudo yum install -y git nginx

# Create application directory
sudo mkdir -p /var/www/gramsense
sudo chown ec2-user:ec2-user /var/www/gramsense

# Copy application files
cp -r * /var/www/gramsense/
cd /var/www/gramsense

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Create systemd service for the backend
sudo tee /etc/systemd/system/gramsense.service > /dev/null <<EOL
[Unit]
Description=GramSense AI Backend
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/var/www/gramsense
ExecStart=/var/www/gramsense/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Configure nginx
sudo tee /etc/nginx/conf.d/gramsense.conf > /dev/null <<EOL
server {
    listen 80;
    server_name _;

    # Serve frontend
    location / {
        root /var/www/gramsense/frontend;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Start services
sudo systemctl daemon-reload
sudo systemctl enable gramsense
sudo systemctl start gramsense
sudo systemctl enable nginx
sudo systemctl start nginx

# Configure firewall
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "🔗 API available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/api/"
EOF

chmod +x "$DEPLOY_DIR/setup.sh"

echo "📦 Creating CloudFormation template for EC2 instance..."

# Create CloudFormation template
cat > "$DEPLOY_DIR/cloudformation.yaml" << EOF
AWSTemplateFormatVersion: '2010-09-09'
Description: 'GramSense AI Prototype Deployment'

Parameters:
  InstanceType:
    Type: String
    Default: $INSTANCE_TYPE
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
    Description: EC2 instance type

  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Default: $KEY_NAME
    Description: Name of an existing EC2 KeyPair

Resources:
  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyName
      ImageId: ami-0c7217cdde317cfec  # Amazon Linux 2 in us-east-1
      SecurityGroups:
        - !Ref SecurityGroup
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y awscli

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for GramSense AI
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0

Outputs:
  InstanceId:
    Description: Instance ID
    Value: !Ref EC2Instance
  PublicIP:
    Description: Public IP address
    Value: !GetAtt EC2Instance.PublicIp
  WebsiteURL:
    Description: Website URL
    Value: !Sub 'http://\${EC2Instance.PublicIp}'
EOF

echo "📤 Ready to deploy!"
echo ""
echo "Next steps:"
echo "1. Upload the deployment package to S3:"
echo "   aws s3 cp $DEPLOY_DIR s3://your-bucket-name/ --recursive"
echo ""
echo "2. Deploy using CloudFormation:"
echo "   aws cloudformation create-stack --stack-name gramsense-ai --template-body file://$DEPLOY_DIR/cloudformation.yaml --parameters ParameterKey=InstanceType,ParameterValue=$INSTANCE_TYPE ParameterKey=KeyName,ParameterValue=$KEY_NAME"
echo ""
echo "3. Or launch EC2 instance manually and run the setup script"
echo ""
echo "📁 Deployment files created in: $DEPLOY_DIR"