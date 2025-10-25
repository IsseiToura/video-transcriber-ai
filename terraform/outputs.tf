# Video Transcriber AI - Outputs

# S3 Outputs (needed by app)
output "s3_bucket_name" {
  description = "Name of the S3 bucket for video storage"
  value       = aws_s3_bucket.video_storage.bucket
}

# DynamoDB Outputs (needed by app)
output "dynamodb_videos_table_name" {
  description = "Name of the DynamoDB videos table"
  value       = local.dynamodb_table_name
}

# Cognito Outputs (needed by app)
output "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_user_pool_client_id" {
  description = "ID of the Cognito User Pool Client"
  value       = aws_cognito_user_pool_client.main.id
}

# ElastiCache Output (needed by app)
output "elasticache_endpoint" {
  description = "Full endpoint of the ElastiCache cluster"
  value       = "${aws_elasticache_cluster.main.cluster_address}:${aws_elasticache_cluster.main.port}"
}

# SQS Outputs (needed by app)
output "sqs_video_processing_queue_url" {
  description = "URL of the SQS video processing queue"
  value       = aws_sqs_queue.video_processing_queue.url
}

output "sqs_video_processing_dlq_url" {
  description = "URL of the SQS video processing dead letter queue"
  value       = aws_sqs_queue.video_processing_dlq.url
}

# Lambda Outputs
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.s3_trigger_handler.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.s3_trigger_handler.arn
}

output "lambda_log_group_name" {
  description = "Name of the CloudWatch Log Group for Lambda"
  value       = aws_cloudwatch_log_group.lambda_log_group.name
}

output "ecr_repository_url" {
  description = "URL of the ECR repository for Lambda images"
  value       = aws_ecr_repository.lambda_repository.repository_url
}

# ECS Outputs (commented out for minimal setup)
# output "ecs_cluster_id" {
#   description = "ID of the ECS cluster"
#   value       = aws_ecs_cluster.main.id
# }

# ALB Outputs (commented out for minimal setup)
# output "alb_dns_name" {
#   description = "DNS name of the Application Load Balancer"
#   value       = aws_lb.main.dns_name
# }


# Configuration Summary
output "configuration_summary" {
  description = "Summary of the deployed configuration"
  value = {
    environment        = local.environment
    region            = var.aws_region
    s3_bucket         = aws_s3_bucket.video_storage.bucket
    dynamodb_table    = local.dynamodb_table_name
    cognito_user_pool = aws_cognito_user_pool.main.id
    cognito_client_id = aws_cognito_user_pool_client.main.id
    elasticache       = "${aws_elasticache_cluster.main.cluster_address}:${aws_elasticache_cluster.main.port}"
    sqs_queue         = aws_sqs_queue.video_processing_queue.url
    sqs_dlq           = aws_sqs_queue.video_processing_dlq.url
    lambda_function   = aws_lambda_function.s3_trigger_handler.function_name
    ecr_repository    = aws_ecr_repository.lambda_repository.repository_url
  }
}
