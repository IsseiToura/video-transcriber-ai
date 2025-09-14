# Secrets Manager secrets
resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = "${local.project_name}/${local.environment}/openai-api-key"
  description             = "OpenAI API key for video transcription"
  recovery_window_in_days = 7

  tags = local.common_tags
}

resource "aws_secretsmanager_secret" "qut_username" {
  name                    = "${local.project_name}/${local.environment}/qut-username"
  description             = "QUT username for the application"
  recovery_window_in_days = 7

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "qut_username" {
  secret_id     = aws_secretsmanager_secret.qut_username.id
  secret_string = var.qut_username
}