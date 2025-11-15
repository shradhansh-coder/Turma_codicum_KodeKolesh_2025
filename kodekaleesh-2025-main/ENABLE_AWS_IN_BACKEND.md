# Enable AWS Integration in Backend

Create a `.env` file in the `backend/` directory with:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
PORT=5000

# AWS Configuration
AWS_ENABLED=true
AWS_REGION=us-east-1
AWS_S3_BUCKET=legalchain-documents-2025

# Note: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are NOT needed here
# They are automatically loaded from ~/.aws/credentials (configured via AWS CLI)
```

## Steps to Enable AWS

### 1. Create `.env` file in backend directory
```powershell
cd backend
New-Item -ItemType File -Name ".env" -Value @"
FLASK_ENV=production
FLASK_DEBUG=false
PORT=5000
AWS_ENABLED=true
AWS_REGION=us-east-1
AWS_S3_BUCKET=legalchain-documents-2025
"@
```

### 2. Start Backend Server
```powershell
cd backend
python app.py
```

### 3. Test AWS Integration
```powershell
# Test AWS status endpoint
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/aws/status" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

Expected output:
```json
{
  "aws_enabled": true,
  "services": {
    "s3_enabled": true,
    "textract_enabled": true
  },
  "bucket": "legalchain-documents-2025",
  "region": "us-east-1",
  "message": "AWS integration fully configured and ready"
}
```

### 4. Test Upload Endpoint
```powershell
# Upload a document
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/upload" `
  -Method POST `
  -InFile ".\uploads\SAMPLE_LEGAL_DOCUMENT.txt" `
  -ContentType "text/plain" `
  -UseBasicParsing

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 5. Test AWS S3 Operations (via CLI)
```powershell
# List documents in S3
aws s3 ls s3://legalchain-documents-2025/ --recursive

# Download document from S3
aws s3 cp s3://legalchain-documents-2025/docs/sample.txt ./downloaded.txt
```

## Verification

Check that:
- ✅ `.env` file exists in `backend/`
- ✅ `AWS_ENABLED=true` is set
- ✅ `AWS_S3_BUCKET=legalchain-documents-2025` is correct
- ✅ Backend starts without AWS errors
- ✅ `/api/aws/status` returns `aws_enabled: true`
- ✅ Documents upload to S3 automatically

## Files Created/Updated

- ✅ `AWS_CLI_SETUP.md` - Complete AWS CLI installation guide
- ✅ `AWS_CLI_STATUS.md` - Current AWS configuration status
- ✅ `aws-cli-helper.ps1` - PowerShell helper script
- 📝 `backend/.env` - Configuration file (you need to create)

---

**Everything is ready!** Just create the `.env` file and restart the backend.
