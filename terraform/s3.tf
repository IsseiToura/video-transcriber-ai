# S3 Bucket for video and transcript storage
resource "aws_s3_bucket" "video_storage" {
  bucket = "${local.project_name}-${local.environment}-n11690216-videos"

  tags = local.common_tags
}


# S3 Bucket server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "video_storage_encryption" {
  bucket = aws_s3_bucket.video_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket public access block
resource "aws_s3_bucket_public_access_block" "video_storage_pab" {
  bucket = aws_s3_bucket.video_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


# S3 Bucket CORS configuration
resource "aws_s3_bucket_cors_configuration" "video_storage_cors" {
  bucket = aws_s3_bucket.video_storage.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# S3 Bucket notification configuration for Lambda trigger
resource "aws_s3_bucket_notification" "video_upload_notification" {
  bucket = aws_s3_bucket.video_storage.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.s3_trigger_handler.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "videos/"
    filter_suffix       = ".webm"
  }

  depends_on = [aws_lambda_permission.s3_lambda_permission]
}

# Lambda permission for S3 to invoke Lambda function
resource "aws_lambda_permission" "s3_lambda_permission" {
  statement_id  = "AllowS3InvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_trigger_handler.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.video_storage.arn
}
