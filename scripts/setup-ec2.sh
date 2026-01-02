#!/bin/bash
# EC2 Instance Setup Script
# Run this script on your EC2 instance after launch

set -e

# Update system
sudo apt update
sudo apt upgrade -y

# Install Docker
echo "Installing Docker..."
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install AWS CLI
sudo apt install -y awscli

# Install CloudWatch Agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
rm amazon-cloudwatch-agent.deb

# Install monitoring tools
sudo apt install -y htop nethogs

# Create application directory
mkdir -p /home/ubuntu/text-to-code
cd /home/ubuntu/text-to-code

# Set up log rotation
sudo tee /etc/logrotate.d/text-to-code > /dev/null <<EOF
/var/log/text-to-code/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 ubuntu ubuntu
    sharedscripts
}
EOF

# Create log directory
sudo mkdir -p /var/log/text-to-code
sudo chown ubuntu:ubuntu /var/log/text-to-code
