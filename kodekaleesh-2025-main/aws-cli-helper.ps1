#!/usr/bin/env powershell
# AWS CLI Quick Setup & Testing Script
# Location: aws-cli-helper.ps1

param(
    [string]$Action = "status",
    [string]$BucketName = "legal-documents"
)

$PythonExe = "C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe"

function Get-AWSStatus {
    Write-Host "🔍 Checking AWS CLI Configuration..." -ForegroundColor Cyan
    & $PythonExe -m awscli configure list
}

function Test-AWSConnection {
    Write-Host "`n🧪 Testing AWS Connection..." -ForegroundColor Cyan
    try {
        $result = & $PythonExe -m awscli sts get-caller-identity
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Connection successful!" -ForegroundColor Green
            Write-Host $result
            return $true
        } else {
            Write-Host "❌ Connection failed. Please configure credentials:" -ForegroundColor Red
            Write-Host "  & '$PythonExe' -m awscli configure" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
        return $false
    }
}

function List-S3Buckets {
    Write-Host "`n📦 Listing S3 Buckets..." -ForegroundColor Cyan
    & $PythonExe -m awscli s3 ls
}

function Create-S3Bucket {
    Write-Host "`n🪣 Creating S3 Bucket: $BucketName" -ForegroundColor Cyan
    & $PythonExe -m awscli s3 mb "s3://$BucketName"
}

function List-BucketContents {
    Write-Host "`n📄 Listing contents of: $BucketName" -ForegroundColor Cyan
    & $PythonExe -m awscli s3 ls "s3://$BucketName/" --recursive
}

function Upload-File {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-Host "❌ File not found: $FilePath" -ForegroundColor Red
        return
    }
    
    $FileName = Split-Path $FilePath -Leaf
    Write-Host "`n📤 Uploading: $FileName" -ForegroundColor Cyan
    & $PythonExe -m awscli s3 cp $FilePath "s3://$BucketName/uploads/$FileName"
}

function Show-Help {
    Write-Host @"
AWS CLI Helper Script
====================

Usage: .\aws-cli-helper.ps1 -Action <action> -BucketName <bucket>

Actions:
  status              Show AWS configuration status (default)
  test                Test AWS connection
  list-buckets        List all S3 buckets
  create-bucket       Create new S3 bucket
  list-contents       List bucket contents
  upload <file>       Upload file to S3
  configure           Interactive AWS configuration
  help                Show this message

Examples:
  # Check configuration
  .\aws-cli-helper.ps1 -Action status

  # Test connection
  .\aws-cli-helper.ps1 -Action test

  # Create S3 bucket
  .\aws-cli-helper.ps1 -Action create-bucket -BucketName my-legal-docs

  # Upload document
  .\aws-cli-helper.ps1 -Action upload -FilePath .\backend\uploads\document.txt

"@
}

# Execute action
switch ($Action.ToLower()) {
    "status" {
        Get-AWSStatus
    }
    "test" {
        Test-AWSConnection
    }
    "list-buckets" {
        List-S3Buckets
    }
    "create-bucket" {
        Create-S3Bucket
    }
    "list-contents" {
        List-BucketContents
    }
    "upload" {
        Write-Host "❌ Please provide file path: -Action upload -FilePath <path>" -ForegroundColor Red
    }
    "configure" {
        Write-Host "🔧 Starting AWS CLI configuration..." -ForegroundColor Cyan
        & $PythonExe -m awscli configure
    }
    "help" {
        Show-Help
    }
    default {
        if ($Action.StartsWith("upload")) {
            # Handle: upload <file>
            $parts = $Action -split ' ', 2
            if ($parts.Length -eq 2) {
                Upload-File -FilePath $parts[1]
            } else {
                Write-Host "❌ Please provide file path" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
            Show-Help
        }
    }
}
