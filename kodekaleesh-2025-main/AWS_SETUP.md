# AWS Configuration Guide

## Setup AWS Integration

The Legal Document Intelligence system now supports AWS services:
- **S3**: Document storage and management
- **Textract**: Advanced OCR with form and table detection

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured: https://aws.amazon.com/cli/
3. **IAM User** with S3 and Textract permissions

### Step 1: Create IAM User

```bash
# Using AWS CLI
aws iam create-user --user-name legal-docs-app

# Attach S3 policy
aws iam attach-user-policy --user-name legal-docs-app \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Attach Textract policy
aws iam attach-user-policy --user-name legal-docs-app \
  --policy-arn arn:aws:iam::aws:policy/AmazonTextractFullAccess

# Create access keys
aws iam create-access-key --user-name legal-docs-app
```

### Step 2: Configure AWS Credentials

**Option A: Environment Variables**
```bash
# Windows PowerShell
$env:AWS_ACCESS_KEY_ID = "your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"
$env:AWS_REGION = "us-east-1"
$env:AWS_S3_BUCKET = "your-bucket-name"
$env:AWS_ENABLED = "true"

# macOS/Linux
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
export AWS_S3_BUCKET="your-bucket-name"
export AWS_ENABLED="true"
```

**Option B: AWS Credentials File**
```bash
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format
```

**Option C: .env File**
```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
AWS_ENABLED=true
```

### Step 3: Create S3 Bucket

```bash
# Create bucket
aws s3 mb s3://your-bucket-name --region us-east-1

# Enable versioning (recommended)
aws s3api put-bucket-versioning \
  --bucket your-bucket-name \
  --versioning-configuration Status=Enabled

# Set lifecycle policy (optional - archive old documents)
aws s3api put-bucket-lifecycle-configuration \
  --bucket your-bucket-name \
  --lifecycle-configuration file://lifecycle.json
```

Example `lifecycle.json`:
```json
{
  "Rules": [
    {
      "Id": "archive-old-docs",
      "Status": "Enabled",
      "Prefix": "documents/",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

### Step 4: Install AWS SDK

```bash
cd backend
pip install boto3
```

### Step 5: Enable AWS in Application

Update `backend/app.py` to initialize AWS:
```python
from aws_integration import AWSIntegration
aws = AWSIntegration()
```

## API Endpoints

### Check AWS Status
```
GET /api/aws/status
Response: {
  "aws_enabled": true,
  "services": {
    "s3_enabled": true,
    "textract_enabled": true
  },
  "bucket": "legal-documents",
  "region": "us-east-1"
}
```

### Upload to S3
```
POST /api/aws/upload
Body: {
  "document_id": "abc12345",
  "file_path": "/local/path/document.pdf"
}
Response: {
  "success": true,
  "s3_key": "documents/2025/11/14/abc12345/document.pdf",
  "url": "https://bucket.s3.amazonaws.com/..."
}
```

### Extract with Textract
```
POST /api/aws/textract/extract
Body: {
  "file_path": "/local/path/document.pdf"
}
Response: {
  "success": true,
  "text": "extracted text...",
  "confidence": 95.2,
  "word_count": 500,
  "page_count": 2
}
```

### Analyze Document Structure
```
POST /api/aws/textract/analyze
Body: {
  "file_path": "/local/path/form.pdf"
}
Response: {
  "success": true,
  "tables": [...],
  "forms": [{"key": "Name", "confidence": 98.5}]
}
```

### List S3 Documents
```
GET /api/aws/documents
Response: {
  "success": true,
  "count": 42,
  "documents": [
    {
      "key": "documents/2025/11/14/abc12345/file.pdf",
      "size": 1048576,
      "last_modified": "2025-11-14T10:30:00"
    }
  ]
}
```

## Features

### S3 Integration
- **Automatic Upload**: Store documents in AWS S3
- **Presigned URLs**: 7-day access links for secure sharing
- **Organization**: Documents organized by date (YYYY/MM/DD)
- **Versioning**: Maintain document history
- **Lifecycle Policies**: Archive old documents to Glacier

### Textract Integration
- **OCR**: Extract text from PDFs and images
- **Form Detection**: Identify and extract form fields
- **Table Recognition**: Extract structured table data
- **Confidence Scores**: Quality metrics for extracted content
- **Multi-page**: Process multi-page PDFs

## Pricing (AWS Free Tier Eligible)

**S3**: 5 GB free storage per month
**Textract**: 100 pages free per month

After free tier:
- S3: $0.023 per GB
- Textract: $1.50 per 1000 pages

## Security Best Practices

1. **Use IAM Roles**: Don't use root credentials
2. **Enable MFA**: Multi-factor authentication for AWS account
3. **Bucket Policies**: Restrict access to specific IPs/users
4. **Encryption**: Enable S3 encryption at rest and in transit
5. **Logging**: Enable CloudTrail and S3 logging
6. **Credentials**: Rotate access keys regularly

Example bucket policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::your-bucket-name/*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

## Testing

```bash
# Test AWS connection
curl http://localhost:5000/api/aws/status

# Upload document to S3
curl -X POST http://localhost:5000/api/aws/upload \
  -H "Content-Type: application/json" \
  -d '{"document_id":"test123","file_path":"./uploads/document.pdf"}'

# Extract text with Textract
curl -X POST http://localhost:5000/api/aws/textract/extract \
  -H "Content-Type: application/json" \
  -d '{"file_path":"./uploads/document.pdf"}'
```

## Troubleshooting

### Credentials Not Found
```
Error: Unable to locate credentials
Solution: Run 'aws configure' or set environment variables
```

### Access Denied to S3
```
Error: An error occurred (AccessDenied)
Solution: Check IAM permissions, ensure user has S3FullAccess policy
```

### Textract Not Available
```
Error: An error occurred (ServiceUnavailable)
Solution: Check region, Textract not available in all regions
```

Supported Textract regions:
- us-east-1, us-west-2
- eu-west-1, eu-central-1
- ap-southeast-1

## Next Steps

1. ✅ Create AWS account and IAM user
2. ✅ Configure credentials
3. ✅ Create S3 bucket
4. ✅ Set AWS_ENABLED=true
5. ✅ Test with /api/aws/status endpoint
6. ⬜ Integrate with CI/CD pipeline
7. ⬜ Set up CloudWatch monitoring
8. ⬜ Configure S3 lifecycle policies

---

**For AWS Sponsorship Recognition**: This integration demonstrates enterprise-grade cloud document management, positioning the solution for scalable production deployment with AWS services.
