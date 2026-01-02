#!/bin/bash

# Fix EC2 disk space issues

EC2_HOST="ubuntu@3.239.116.3"
KEY_PATH="~/Downloads/text-to-code-key.pem"

echo "🔍 Checking disk usage on EC2..."

ssh -i $KEY_PATH $EC2_HOST << 'ENDSSH'
set -e

echo "📊 Current disk usage:"
df -h /

echo ""
echo "🧹 Cleaning up system..."

# Clean apt cache
echo "Cleaning apt cache..."
sudo apt-get clean
sudo apt-get autoclean
sudo apt-get autoremove -y

# Clean journal logs
echo "Cleaning journal logs..."
sudo journalctl --vacuum-time=2d

# Clean old Docker data
echo "Cleaning Docker..."
docker system prune -a -f --volumes

# Clean temp files
echo "Cleaning temp files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Find large files
echo ""
echo "🔎 Top 10 largest files:"
sudo find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -10

echo ""
echo "📊 Disk usage after cleanup:"
df -h /

ENDSSH

echo ""
echo "✅ Cleanup complete!"

