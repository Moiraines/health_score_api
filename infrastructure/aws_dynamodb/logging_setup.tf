provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "dynamodb_table_name" {
  default = "health-score-logs"
}

resource "aws_dynamodb_table" "health_score_logs" {
  name           = var.dynamodb_table_name
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "timestamp"
  range_key      = "log_level"

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "log_level"
    type = "S"
  }

  tags = {
    Name        = "health-score-logs"
    Environment = "production"
  }
}

# IAM Role and Policy for application to access DynamoDB
resource "aws_iam_role" "app_dynamodb_access" {
  name = "health-score-app-dynamodb-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "dynamodb_access_policy" {
  name        = "health-score-dynamodb-access-policy"
  description = "Policy to allow application to write logs to DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:BatchWriteItem"
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.health_score_logs.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "dynamodb_access_attachment" {
  role       = aws_iam_role.app_dynamodb_access.name
  policy_arn = aws_iam_policy.dynamodb_access_policy.arn
}

# Output the IAM role ARN for application configuration
output "dynamodb_access_role_arn" {
  value = aws_iam_role.app_dynamodb_access.arn
}
