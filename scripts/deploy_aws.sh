#!/bin/bash

# Script to deploy the Health Score API to AWS using Terraform

# Ensure the script is run from the project root directory
if [ ! -d "health_score_api/infrastructure/terraform" ]; then
  echo "Error: This script must be run from the project root directory."
  exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
  echo "Terraform is not installed. Please install Terraform first."
  echo "Installation instructions: https://learn.hashicorp.com/tutorials/terraform/install-cli"
  exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
  echo "AWS CLI is not installed. Please install AWS CLI first."
  echo "Installation instructions: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
  exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
  echo "AWS credentials are not configured. Please configure AWS CLI with your credentials."
  echo "Run 'aws configure' to set up your credentials."
  exit 1
fi

# Navigate to Terraform directory
echo "Navigating to Terraform directory..."
cd health_score_api/infrastructure/terraform

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Plan Terraform deployment
echo "Planning Terraform deployment..."
terraform plan -out=tfplan

# Prompt user to confirm deployment
echo "Review the Terraform plan above. Do you want to proceed with the deployment? (yes/no)"
read confirm
if [ "$confirm" != "yes" ]; then
  echo "Deployment cancelled."
  cd ../../..
  exit 0
fi

# Apply Terraform deployment
echo "Applying Terraform deployment..."
terraform apply tfplan

# Check if deployment was successful
if [ $? -eq 0 ]; then
  echo "Terraform deployment successful."
  echo "Retrieving EC2 instance public IP..."
  INSTANCE_IP=$(terraform output -raw ec2_public_ip)
  echo "EC2 Instance Public IP: $INSTANCE_IP"
  echo "You can SSH into the instance with: ssh -i ~/.ssh/health_score_api_key.pem ec2-user@$INSTANCE_IP"
  echo "After connecting, start the application with Docker Compose."
else
  echo "Terraform deployment failed. Check the error messages above for details."
  cd ../../..
  exit 1
fi

# Return to project root
cd ../../..

echo "Deployment script complete. Make sure to set up the EC2 instance with the application and start the services."
