# AWS CLI Quick Reference

## 🚀 Start Everything

```powershell
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend  
cd frontend
npm start

# Terminal 3: AWS CLI commands (optional)
cd backend
```

---

## 📝 AWS CLI Commands

### Account & Credentials
```powershell
# Check AWS configuration
aws configure list

# Verify credentials (shows Account ID and ARN)
aws sts get-caller-identity

# List IAM users
aws iam list-users
```

### S3 Bucket Operations
```powershell
# List all buckets
aws s3 ls

# List bucket contents
aws s3 ls s3://legalchain-documents-2025/

# List with recursion and details
aws s3 ls s3://legalchain-documents-2025/ --recursive --human-readable

# Upload file
aws s3 cp ./document.pdf s3://legalchain-documents-2025/docs/

# Download file
aws s3 cp s3://legalchain-documents-2025/docs/document.pdf ./

# Sync directory
aws s3 sync ./uploads s3://legalchain-documents-2025/uploads/

# Delete file
aws s3 rm s3://legalchain-documents-2025/docs/document.pdf

# Delete entire bucket
aws s3 rb s3://legalchain-documents-2025 --force
```

### S3 Advanced
```powershell
# List with file sizes
aws s3api list-objects-v2 --bucket legalchain-documents-2025 --output table

# Get file metadata
aws s3api head-object --bucket legalchain-documents-2025 --key docs/document.pdf

# Copy between buckets
aws s3 cp s3://source-bucket/file s3://legalchain-documents-2025/file

# Set object permissions
aws s3api put-object-acl --bucket legalchain-documents-2025 --key docs/file.pdf --acl public-read
```

### Textract OCR
```powershell
# Detect text (synchronous, small files)
aws textract detect-document-text \
  --document-location '{"S3Object":{"Bucket":"legalchain-documents-2025","Name":"docs/document.pdf"}}' \
  --region us-east-1

# Analyze document (forms, tables)
aws textract analyze-document \
  --document-location '{"S3Object":{"Bucket":"legalchain-documents-2025","Name":"docs/form.pdf"}}' \
  --feature-types TABLES FORMS \
  --region us-east-1

# Get analysis results
aws textract get-document-text-detection --job-id <job-id> --region us-east-1
```

---

## 🌐 API Endpoints

### Health Check
```
GET http://localhost:5000/api/health
```

### Document Operations
```
POST   http://localhost:5000/api/upload           # Upload document
GET    http://localhost:5000/api/documents        # List all documents
GET    http://localhost:5000/api/documents/<id>/summary
GET    http://localhost:5000/api/documents/<id>/metadata
DELETE http://localhost:5000/api/documents/<id>   # Delete document
```

### Search & Analysis
```
POST http://localhost:5000/api/search             # Search documents
POST http://localhost:5000/api/analyze            # Analyze documents
```

### OCR (Local Tesseract)
```
GET  http://localhost:5000/api/ocr/status         # Check OCR status
POST http://localhost:5000/api/ocr/extract        # Extract from image
```

### AWS Services
```
GET  http://localhost:5000/api/aws/status         # Check AWS status
POST http://localhost:5000/api/aws/upload         # Upload to S3
POST http://localhost:5000/api/aws/textract/extract    # Extract with Textract
POST http://localhost:5000/api/aws/textract/analyze    # Analyze with Textract
GET  http://localhost:5000/api/aws/documents      # List S3 documents
```

---

## 🧪 Test Commands

### Test Backend is Running
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/health" | ConvertFrom-Json
```

### Test AWS Status
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/aws/status" | ConvertFrom-Json
```

### Upload Document (PowerShell)
```powershell
$file = Get-Item ".\backend\uploads\SAMPLE_LEGAL_DOCUMENT.txt"
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/upload" `
    -Method POST `
    -InFile $file.FullName `
    -ContentType "text/plain"
$response.Content | ConvertFrom-Json
```

### Search Documents (PowerShell)
```powershell
$query = @{query = "legal"; limit = 5} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/api/search" `
    -Method POST `
    -Body $query `
    -ContentType "application/json" | ForEach-Object {$_.Content | ConvertFrom-Json}
```

---

## 📋 Configuration Files

### `.env` (backend)
```
AWS_ENABLED=true
AWS_REGION=us-east-1
AWS_S3_BUCKET=legalchain-documents-2025
```

### AWS Credentials (`~/.aws/credentials`)
```ini
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
```

### AWS Config (`~/.aws/config`)
```ini
[default]
region = us-east-1
output = json
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| AWS CLI not found | Use full path: `& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli <cmd>` |
| Credentials not found | Run `aws configure` to set up credentials |
| Bucket not found | Check spelling: `aws s3 ls` to list buckets |
| Access Denied | Verify IAM policy includes needed permissions |
| Backend won't start | Check `.env` file exists in backend directory |
| Port 5000 in use | Change PORT in `.env` and restart |

---

## 🔗 Useful Links

- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/latest/userguide/)
- [AWS S3 CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/s3/index.html)
- [AWS Textract Documentation](https://docs.aws.amazon.com/textract/latest/dg/)
- [IAM User Guide](https://docs.aws.amazon.com/iam/latest/userguide/)

---

## 💡 Pro Tips

1. **Alias AWS CLI** for shorter commands:
   ```powershell
   function aws { & 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli $args }
   ```

2. **Use AWS CLI filters** to reduce output:
   ```powershell
   aws s3 ls --query 'Buckets[?contains(Name, `legal`)]'
   ```

3. **Enable CLI output formatting**:
   ```powershell
   aws configure set output json
   aws configure set output table
   ```

4. **Use AWS CLI profiles** for multiple accounts:
   ```powershell
   aws configure --profile production
   aws s3 ls --profile production
   ```

---

**Last Updated**: November 14, 2025
