# AWS CLI Setup in Workspace

## ✅ Installation Status

AWS CLI v1.42.73 is installed and ready to use!

**Python Version**: 3.11.9  
**AWS CLI Version**: 1.42.73  
**botocore Version**: 1.40.73

---

## 🔧 Configuration

### Method 1: Interactive Configuration (Recommended)

Run this command to set up AWS credentials:

```powershell
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli configure
```

You'll be prompted for:
1. **AWS Access Key ID**: Your IAM user's access key
2. **AWS Secret Access Key**: Your IAM user's secret key
3. **Default region**: `us-east-1` (or your preferred region)
4. **Default output format**: `json`

### Method 2: Environment Variables

Set these in your PowerShell session:

```powershell
$env:AWS_ACCESS_KEY_ID = "your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"
$env:AWS_REGION = "us-east-1"
$env:AWS_OUTPUT = "json"
```

Or in `.env` file:
```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_DEFAULT_OUTPUT=json
```

### Method 3: Configuration File

Edit `~\.aws\credentials` (or create it):

```ini
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key

[profile-name]
aws_access_key_id = another-access-key
aws_secret_access_key = another-secret-key
```

Edit `~\.aws\config`:

```ini
[default]
region = us-east-1
output = json

[profile profile-name]
region = eu-west-1
output = json
```

---

## 📋 Quick Start Commands

### Check Configuration
```powershell
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli configure list
```

### Test AWS Connection
```powershell
# Check STS identity
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli sts get-caller-identity

# List S3 buckets
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli s3 ls
```

### Create S3 Bucket
```powershell
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli s3 mb s3://legal-documents-$(Get-Date -Format "yyyy-MM-dd-HHmmss")
```

### Upload Document
```powershell
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli s3 cp .\backend\uploads\SAMPLE_LEGAL_DOCUMENT.txt s3://legal-documents/samples/
```

### List S3 Objects
```powershell
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli s3 ls s3://legal-documents/ --recursive
```

---

## 🔑 Create AWS Credentials

### Step 1: AWS Console Setup
1. Go to [AWS Console](https://console.aws.amazon.com)
2. Navigate to **IAM** → **Users**
3. Click **Create User**
4. Name: `legal-documents-user`
5. Enable **Programmatic access** (Access Key ID + Secret Access Key)

### Step 2: Attach Permissions
Attach this inline policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::legal-documents/*",
                "arn:aws:s3:::legal-documents"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "textract:StartDocumentTextDetection",
                "textract:GetDocumentTextDetection",
                "textract:StartDocumentAnalysis",
                "textract:GetDocumentAnalysis"
            ],
            "Resource": "*"
        }
    ]
}
```

### Step 3: Configure Workspace

Copy the Access Key ID and Secret Access Key, then:

```powershell
# Run interactive configuration
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli configure

# Or set environment variables (temporary, session-only)
$env:AWS_ACCESS_KEY_ID = "paste-your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "paste-your-secret-key"
$env:AWS_REGION = "us-east-1"
```

---

## 🧪 Verify Installation

Run these commands to verify everything works:

```powershell
# Check AWS CLI version
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli --version

# Check configured credentials
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli configure list

# Test AWS connection (if credentials configured)
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli sts get-caller-identity
```

Expected output for `get-caller-identity`:
```json
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/legal-documents-user"
}
```

---

## 🛠️ Alias Setup (Optional)

Create a PowerShell alias for easier typing:

```powershell
# Add to PowerShell profile
$profile_path = $PROFILE
if (-not (Test-Path $profile_path)) {
    New-Item -ItemType File -Path $profile_path -Force
}

Add-Content $profile_path @"
# AWS CLI Alias
function aws {
    & 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli `$args
}
"@

# Reload profile
. $PROFILE
```

Then you can use:
```powershell
aws configure list
aws s3 ls
aws sts get-caller-identity
```

---

## 📚 Useful AWS CLI Commands

### S3 Operations
```powershell
# List all buckets
aws s3 ls

# Create bucket
aws s3 mb s3://legal-documents

# Upload file
aws s3 cp file.pdf s3://legal-documents/docs/

# Download file
aws s3 cp s3://legal-documents/docs/file.pdf ./

# List bucket contents
aws s3 ls s3://legal-documents/ --recursive

# Delete file
aws s3 rm s3://legal-documents/docs/file.pdf

# Sync directory
aws s3 sync ./uploads s3://legal-documents/uploads/
```

### Textract Operations
```powershell
# Start document analysis (async)
aws textract start-document-text-detection --document-location '{"S3Object":{"Bucket":"legal-documents","Name":"docs/file.pdf"}}' --region us-east-1

# Get analysis results (provide JobId from above)
aws textract get-document-text-detection --job-id <job-id> --region us-east-1
```

### Other Useful Commands
```powershell
# List user identity
aws sts get-caller-identity

# List IAM users
aws iam list-users

# Get account information
aws sts get-account-authorization-details
```

---

## 🔒 Security Best Practices

1. **Never commit credentials**: Add to `.gitignore`:
   ```
   ~/.aws/credentials
   .env
   AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY
   ```

2. **Use IAM roles in production**: Don't use long-term credentials

3. **Rotate access keys regularly**: Change credentials every 90 days

4. **Use specific permissions**: Limit IAM policy to only needed resources

5. **Enable MFA**: Require multi-factor authentication for sensitive operations

---

## 🐛 Troubleshooting

### "aws: command not found"
Add Python to PATH or use full path:
```powershell
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli <command>
```

### "Unable to locate credentials"
Run configuration:
```powershell
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli configure
```

### "AccessDenied" errors
Check IAM policy has required permissions for S3 and Textract

### Region-related errors
Verify region is set:
```powershell
& 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' -m awscli configure list
```

---

## 📝 Next Steps

1. ✅ **AWS CLI installed** - Done!
2. 📋 **Create IAM user** - Go to AWS Console → IAM
3. 🔑 **Get credentials** - Download Access Key ID and Secret
4. ⚙️ **Configure workspace** - Run `aws configure` or set env vars
5. 🧪 **Test connection** - Run `aws sts get-caller-identity`
6. 🪣 **Create S3 bucket** - Run `aws s3 mb s3://legal-documents`
7. 🚀 **Enable AWS in app** - Set `AWS_ENABLED=true` in `.env`
8. 🔗 **Test integration** - Call `/api/aws/status` endpoint

---

**AWS CLI Version**: 1.42.73  
**Installation Date**: November 14, 2025  
**Status**: ✅ Ready for Configuration
