# Using existing subnet group and security groups (no VPC resources managed here)

# ElastiCache Memcached cluster
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${local.project_name}-${local.environment}-memcached"
  engine               = "memcached"
  node_type            = var.elasticache_node_type
  num_cache_nodes      = var.elasticache_num_cache_nodes
  parameter_group_name = "default.memcached1.6"
  port                 = 11211
  subnet_group_name    = "cab432-subnets"
  security_group_ids   = ["sg-07707a36aa1599475"]  # CAB432MemcachedSG

  tags = local.common_tags
}
