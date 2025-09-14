# Systems Manager Parameter Store parameters
resource "aws_ssm_parameter" "aws_region" {
  name  = "/${local.project_name}/${local.environment}/aws/region"
  type  = "String"
  value = var.aws_region

  tags = local.common_tags
}

resource "aws_ssm_parameter" "s3_bucket" {
  name  = "/${local.project_name}/${local.environment}/aws/s3-bucket"
  type  = "String"
  value = aws_s3_bucket.video_storage.bucket

  tags = local.common_tags
}

resource "aws_ssm_parameter" "ddb_videos_table" {
  name  = "/${local.project_name}/${local.environment}/aws/ddb-videos-table"
  type  = "String"
  value = local.dynamodb_table_name

  tags = local.common_tags
}

resource "aws_ssm_parameter" "elasticache_memcached_endpoint" {
  name  = "/${local.project_name}/${local.environment}/aws/elasticache-memcached-endpoint"
  type  = "String"
  value = "${aws_elasticache_cluster.main.cluster_address}:${aws_elasticache_cluster.main.port}"

  tags = local.common_tags
}

resource "aws_ssm_parameter" "cognito_user_pool_id" {
  name  = "/${local.project_name}/${local.environment}/cognito/user-pool-id"
  type  = "String"
  value = aws_cognito_user_pool.main.id

  tags = local.common_tags
}

resource "aws_ssm_parameter" "cognito_app_client_id" {
  name  = "/${local.project_name}/${local.environment}/cognito/app-client-id"
  type  = "String"
  value = aws_cognito_user_pool_client.main.id

  tags = local.common_tags
}

resource "aws_ssm_parameter" "openai_model" {
  name  = "/${local.project_name}/${local.environment}/ai/openai-model"
  type  = "String"
  value = var.openai_model

  tags = local.common_tags
}

resource "aws_ssm_parameter" "cors_allowed_origins" {
  name  = "/${local.project_name}/${local.environment}/cors/allowed-origins"
  type  = "String"
  value = join(",", var.allowed_origins)

  tags = local.common_tags
}

resource "aws_ssm_parameter" "app_url" {
  name  = "/${local.project_name}/${local.environment}/app/url"
  type  = "String"
  value = "http://localhost:5173"

  tags = local.common_tags
}

resource "aws_ssm_parameter" "api_base_url" {
  name  = "/${local.project_name}/${local.environment}/api/base-url"
  type  = "String"
  value = "http://localhost:8000/api/v1"

  tags = local.common_tags
}
