# Video Transcriber AI - Terraform Infrastructure (Minimal Setup)

This directory contains the Terraform configuration for deploying the core AWS services used by the Video Transcriber AI application.

## Architecture Overview (Minimal)

The minimal infrastructure includes the essential services:

- **S3**: Bucket for video and transcript storage with encryption and CORS configuration
- **DynamoDB**: Reference to existing video metadata table (`n11690216-videos`)
- **Cognito**: User Pool and App Client for authentication with email verification
- **ElastiCache**: Memcached cluster for caching (uses existing VPC infrastructure)
- **Systems Manager Parameter Store**: Configuration management for all service endpoints
- **Secrets Manager**: Secure storage for API keys and sensitive data

**Note**: This setup uses existing VPC infrastructure (subnet groups and security groups) for ElastiCache. The DynamoDB table is referenced but not managed by Terraform. For production deployment, additional services like ECS and ALB would be needed.

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0 installed

## Quick Start

1. **Copy the example variables file:**

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Edit terraform.tfvars with your values:**

   ```hcl
   aws_region = "ap-southeast-2"
   environment = "dev"
   qut_username = "your-qut-username@qut.edu.au"
   ```

3. **Initialize Terraform:**

   ```bash
   terraform init
   ```

4. **Plan the deployment:**

   ```bash
   terraform plan
   ```

5. **Deploy the infrastructure:**
   ```bash
   terraform apply
   ```

## Configuration

### Required Variables

- `aws_region`: AWS region for deployment (default: "ap-southeast-2")
- `environment`: Environment name (default: "dev")
- `qut_username`: QUT username for resource naming (default: "n11690216@qut.edu.au")

### Optional Variables

- `allowed_origins`: CORS allowed origins (default: ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"])
- `openai_model`: OpenAI model to use (default: "gpt-4o-mini")
- `elasticache_node_type`: ElastiCache node type (default: "cache.t3.micro")
- `elasticache_num_cache_nodes`: Number of cache nodes (default: 1)

## Post-Deployment Setup

After successful deployment:

1. **Update Secrets Manager values:**

   ```bash
   aws secretsmanager update-secret \
     --secret-id "video-transcriber-ai/dev/openai-api-key" \
     --secret-string "your-actual-openai-api-key"
   ```

   **Note**: The QUT username secret is automatically populated from the Terraform variable.

2. **Update your local environment variables:**

   ```bash
   # Copy the output values to your .env file
   terraform output
   ```

3. **Run your application locally:**
   ```bash
   cd ../server
   python run.py
   ```

## Important Outputs

After deployment, note these important values:

- **S3 Bucket**: `$(terraform output -raw s3_bucket_name)`
- **Cognito User Pool ID**: `$(terraform output -raw cognito_user_pool_id)`
- **Cognito App Client ID**: `$(terraform output -raw cognito_user_pool_client_id)`
- **DynamoDB Table**: `$(terraform output -raw dynamodb_videos_table_name)` (existing table: `n11690216-videos`)
- **ElastiCache Endpoint**: `$(terraform output -raw elasticache_endpoint)`

### Configuration Summary

You can also get a complete configuration summary:

```bash
terraform output configuration_summary
```

### Systems Manager Parameter Store

All configuration values are automatically stored in Systems Manager Parameter Store:

- `/video-transcriber-ai/dev/aws/region`
- `/video-transcriber-ai/dev/aws/s3-bucket`
- `/video-transcriber-ai/dev/aws/ddb-videos-table`
- `/video-transcriber-ai/dev/aws/elasticache-memcached-endpoint`
- `/video-transcriber-ai/dev/cognito/user-pool-id`
- `/video-transcriber-ai/dev/cognito/app-client-id`
- `/video-transcriber-ai/dev/ai/openai-model`
- `/video-transcriber-ai/dev/cors/allowed-origins`
- `/video-transcriber-ai/dev/app/url`
- `/video-transcriber-ai/dev/api/base-url`

## Security Considerations

- All resources are tagged with project and environment
- S3 bucket has public access blocked and server-side encryption enabled
- S3 bucket has CORS configuration for web application access
- ElastiCache uses existing VPC security groups and subnet groups
- Cognito User Pool has advanced security mode enabled
- Secrets Manager stores sensitive data with 7-day recovery window
- Systems Manager Parameter Store manages configuration securely

## Cost Optimization

- ElastiCache uses t3.micro instances (cache.t3.micro)
- Minimal resource configuration with single cache node
- S3 bucket with server-side encryption (AES256) for cost-effective storage
- Systems Manager Parameter Store for configuration management
- Secrets Manager with minimal recovery window (7 days)

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all data including S3 objects. The DynamoDB table (`n11690216-videos`) is not managed by Terraform and will not be affected.

## Troubleshooting

### Common Issues

1. **S3 access denied**: Verify IAM policies and bucket permissions
2. **DynamoDB connection issues**: Ensure the existing table `n11690216-videos` exists and has proper permissions
3. **Cognito authentication issues**: Verify User Pool and App Client configuration
4. **ElastiCache connection issues**: Check that the existing subnet group `cab432-subnets` and security group `sg-07707a36aa1599475` are accessible

### Useful Commands

```bash
# Check S3 bucket
aws s3 ls s3://$(terraform output -raw s3_bucket_name)

# Check DynamoDB table (existing table)
aws dynamodb describe-table --table-name n11690216-videos

# Check Cognito User Pool
aws cognito-idp describe-user-pool --user-pool-id $(terraform output -raw cognito_user_pool_id)

# Check ElastiCache cluster
aws elasticache describe-cache-clusters --cache-cluster-id $(terraform output -raw elasticache_cluster_address | cut -d'.' -f1)
```
