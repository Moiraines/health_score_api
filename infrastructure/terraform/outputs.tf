output "app_server_public_ip" {
  description = "Public IP of the application server"
  value       = aws_eip.app_eip.public_ip
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for logging"
  value       = aws_dynamodb_table.health_score_logs.name
}
