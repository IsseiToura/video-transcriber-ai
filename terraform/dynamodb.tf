# Reference to existing DynamoDB table created via AWS Console
# Using a simpler approach to avoid continuous backups permission issues
locals {
  dynamodb_table_name = "n11690216-videos"
}
