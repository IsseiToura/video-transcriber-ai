# SQS Queue for video processing jobs
resource "aws_sqs_queue" "video_processing_queue" {
  name                       = "${local.project_name}-${local.environment}-video-processing-queue"
  message_retention_seconds  = 1209600  # 14 days
  visibility_timeout_seconds = 600      # 10 minutes (default timeout)
  receive_wait_time_seconds  = 20       # Long polling

  # Dead Letter Queue configuration
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.video_processing_dlq.arn
    maxReceiveCount     = 3
  })

  tags = merge(local.common_tags, {
    Name        = "${local.project_name}-${local.environment}-video-processing-queue"
    Description = "Queue for video transcription processing jobs"
  })
}

# Dead Letter Queue for failed video processing jobs
resource "aws_sqs_queue" "video_processing_dlq" {
  name                      = "${local.project_name}-${local.environment}-video-processing-dlq"
  message_retention_seconds = 1209600  # 14 days

  tags = merge(local.common_tags, {
    Name        = "${local.project_name}-${local.environment}-video-processing-dlq"
    Description = "Dead letter queue for failed video processing jobs"
  })
}

# IAM Policy for SQS access
resource "aws_iam_policy" "sqs_video_processing_policy" {
  name        = "${local.project_name}-${local.environment}-sqs-video-processing-policy"
  description = "Policy for video processing SQS operations"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:ChangeMessageVisibility"
        ]
        Resource = [
          aws_sqs_queue.video_processing_queue.arn,
          aws_sqs_queue.video_processing_dlq.arn
        ]
      }
    ]
  })

  tags = local.common_tags
}

# IAM Role for EC2 instances (if using EC2 instead of ECS)
resource "aws_iam_role" "ec2_sqs_role" {
  name = "${local.project_name}-${local.environment}-ec2-sqs-role"

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

  tags = local.common_tags
}

# Attach policies to EC2 role
resource "aws_iam_role_policy_attachment" "ec2_sqs_policy_attachment" {
  role       = aws_iam_role.ec2_sqs_role.name
  policy_arn = aws_iam_policy.sqs_video_processing_policy.arn
}

# Attach additional policies for S3, DynamoDB, etc.
resource "aws_iam_role_policy_attachment" "ec2_s3_policy_attachment" {
  role       = aws_iam_role.ec2_sqs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "ec2_dynamodb_policy_attachment" {
  role       = aws_iam_role.ec2_sqs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "ec2_elasticache_policy_attachment" {
  role       = aws_iam_role.ec2_sqs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonElastiCacheFullAccess"
}

# Instance profile for EC2
resource "aws_iam_instance_profile" "ec2_sqs_profile" {
  name = "${local.project_name}-${local.environment}-ec2-sqs-profile"
  role = aws_iam_role.ec2_sqs_role.name

  tags = local.common_tags
}
