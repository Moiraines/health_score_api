#!/bin/bash

# Update system
yum update -y

# Install Docker
yum install -y docker
service docker start
usermod -a -G docker ec2-user

# Install docker-compose
curl -L https://github.com/docker/compose/releases/download/1.29.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install git
yum install -y git

# Clone repository (replace with your repo URL)
# git clone <your-repo-url>
# cd <your-repo-directory>

# Setup environment variables
cat <<EOF > /home/ec2-user/.env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/dbname
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=health-score-logs
EOF

# Instructions to build and run Docker containers
# cd /path/to/your/project
# docker-compose up --build -d

# Optionally, setup a cron job or systemd service to start the application on boot

exit 0
