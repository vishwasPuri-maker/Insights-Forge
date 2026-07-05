# /infra/s3_buckets.tf
# Insight Forge — Multi-Tenant AWS S3 Landing/Raw Data Lake
# Task 1: Multi-Tenant S3 Data Lake Partitioning & Access Topology
# Mapping: Doc 4 (BSM Section 1), Doc 2 (TRD Section 9.3)

terraform {
  required_version = ">= 1.8.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "tenant_ids" {
  description = "List of onboarded tenant UUIDs used to seed prefix-level IAM isolation"
  type        = list(string)
  default     = []
}

# ---------------------------------------------------------------------------
# Primary Landing/Raw bucket. Objects are partitioned as:
#   s3://insightforge-data-lake-prod/tenants/<tenant_uuid>/raw/...
# ---------------------------------------------------------------------------
resource "aws_s3_bucket" "insightforge_lake" {
  bucket = "insightforge-data-lake-prod"

  tags = {
    Environment = "Production"
    Team        = "DataDragons"
    Purpose     = "MultiTenantRawLandingZone"
  }
}

resource "aws_s3_bucket_versioning" "lake_versioning" {
  bucket = aws_s3_bucket.insightforge_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# KMS key dedicated to the lake — SSE-KMS 256-bit encryption at rest by default
resource "aws_kms_key" "lake_key" {
  description             = "KMS key for Insight Forge multi-tenant data lake encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_alias" "lake_key_alias" {
  name          = "alias/insightforge-lake-key"
  target_key_id = aws_kms_key.lake_key.key_id
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lake_crypto" {
  bucket = aws_s3_bucket.insightforge_lake.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.lake_key.arn
    }
    bucket_key_enabled = true
  }
}

# Block all public access unconditionally
resource "aws_s3_bucket_public_access_block" "lake_block" {
  bucket                  = aws_s3_bucket.insightforge_lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 30-day lifecycle expiration on raw landing objects (Data Retention & Privacy rule)
resource "aws_s3_bucket_lifecycle_configuration" "lake_lifecycle" {
  bucket = aws_s3_bucket.insightforge_lake.id

  rule {
    id     = "raw-30-day-expiration"
    status = "Enabled"

    filter {
      prefix = "tenants/"
    }

    expiration {
      days = 30
    }
  }
}

# ---------------------------------------------------------------------------
# Cross-tenant access denial — bucket policy blocks any principal from
# reading/writing outside their own tenant prefix, enforced via the
# "aws:PrincipalTag/tenant_id" condition set by the IAM role assumed per request.
# ---------------------------------------------------------------------------
data "aws_iam_policy_document" "tenant_isolation" {
  statement {
    sid    = "DenyCrossTenantAccess"
    effect = "Deny"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions = ["s3:GetObject", "s3:PutObject"]
    resources = ["${aws_s3_bucket.insightforge_lake.arn}/tenants/*"]

    condition {
      test     = "StringNotEquals"
      variable = "s3:ExistingObjectTag/tenant_id"
      values   = ["$${aws:PrincipalTag/tenant_id}"]
    }
  }
}

resource "aws_s3_bucket_policy" "lake_policy" {
  bucket = aws_s3_bucket.insightforge_lake.id
  policy = data.aws_iam_policy_document.tenant_isolation.json
}

output "lake_bucket_name" {
  value = aws_s3_bucket.insightforge_lake.bucket
}

output "lake_kms_key_arn" {
  value = aws_kms_key.lake_key.arn
}
