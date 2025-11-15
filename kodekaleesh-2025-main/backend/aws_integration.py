"""AWS integration for document storage and OCR"""

import boto3
import os
from typing import Dict, Any, List
from datetime import datetime

class AWSIntegration:
    """AWS services integration (S3, Textract)"""
    
    def __init__(self):
        # Initialize AWS clients if credentials are available
        self.s3_client = None
        self.textract_client = None
        self.bucket_name = os.getenv('AWS_S3_BUCKET', 'legal-documents')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.enabled = os.getenv('AWS_ENABLED', 'false').lower() == 'true'
        
        if self.enabled:
            try:
                self.s3_client = boto3.client('s3', region_name=self.region)
                self.textract_client = boto3.client('textract', region_name=self.region)
            except Exception as e:
                print(f"Warning: AWS initialization failed: {e}")
                self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if AWS integration is enabled"""
        return self.enabled
    
    def upload_to_s3(self, file_path: str, document_id: str, filename: str) -> Dict[str, Any]:
        """
        Upload document to AWS S3
        
        Args:
            file_path: Local file path
            document_id: Document ID for organization
            filename: Original filename
            
        Returns:
            Upload result with S3 key and URL
        """
        if not self.enabled or not self.s3_client:
            return {'success': False, 'error': 'AWS S3 not enabled'}
        
        try:
            # Organize in S3 by date
            today = datetime.now().strftime('%Y/%m/%d')
            s3_key = f"documents/{today}/{document_id}/{filename}"
            
            # Upload file
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': 'application/octet-stream'}
            )
            
            # Generate presigned URL (valid for 7 days)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=604800  # 7 days
            )
            
            return {
                'success': True,
                'bucket': self.bucket_name,
                's3_key': s3_key,
                'url': url,
                'message': f'Document uploaded to S3: {s3_key}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_text_with_textract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from document using AWS Textract
        
        Args:
            file_path: Path to document (PDF or image)
            
        Returns:
            Extracted text, confidence, and metadata
        """
        if not self.enabled or not self.textract_client:
            return {'success': False, 'error': 'AWS Textract not enabled'}
        
        try:
            with open(file_path, 'rb') as f:
                document_bytes = f.read()
            
            # Detect document text
            response = self.textract_client.detect_document_text(
                Document={'Bytes': document_bytes}
            )
            
            # Extract text blocks
            text_blocks = []
            confidence_scores = []
            
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    text_blocks.append(block['Text'])
                    if 'Confidence' in block:
                        confidence_scores.append(block['Confidence'])
            
            # Combine text
            extracted_text = '\n'.join(text_blocks)
            
            # Calculate average confidence
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            return {
                'success': True,
                'text': extracted_text,
                'confidence': round(avg_confidence, 2),
                'block_count': len(text_blocks),
                'character_count': len(extracted_text),
                'word_count': len(extracted_text.split()),
                'page_count': response.get('DocumentMetadata', {}).get('Pages', 1)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_document_with_textract(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze document structure with Textract
        
        Args:
            file_path: Path to document
            
        Returns:
            Structured analysis with forms and tables
        """
        if not self.enabled or not self.textract_client:
            return {'success': False, 'error': 'AWS Textract not enabled'}
        
        try:
            with open(file_path, 'rb') as f:
                document_bytes = f.read()
            
            # Analyze document (includes forms, tables, signatures)
            response = self.textract_client.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['TABLES', 'FORMS']
            )
            
            analysis = {
                'success': True,
                'blocks': len(response['Blocks']),
                'tables': [],
                'forms': [],
                'confidence': 0
            }
            
            # Extract tables
            for block in response['Blocks']:
                if block['BlockType'] == 'TABLE':
                    analysis['tables'].append({
                        'id': block['Id'],
                        'rows': block.get('RowSpan', 0),
                        'columns': block.get('ColumnSpan', 0)
                    })
                elif block['BlockType'] == 'KEY_VALUE_SET':
                    if block['EntityTypes'][0] == 'KEY':
                        analysis['forms'].append({
                            'key': block['Text'],
                            'confidence': block.get('Confidence', 0)
                        })
            
            return analysis
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_from_s3(self, s3_key: str) -> Dict[str, Any]:
        """
        Delete document from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Deletion result
        """
        if not self.enabled or not self.s3_client:
            return {'success': False, 'error': 'AWS S3 not enabled'}
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return {
                'success': True,
                'message': f'Document deleted from S3: {s3_key}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_documents_in_s3(self, prefix: str = 'documents/') -> Dict[str, Any]:
        """
        List documents in S3
        
        Args:
            prefix: S3 prefix to filter
            
        Returns:
            List of documents and metadata
        """
        if not self.enabled or not self.s3_client:
            return {'success': False, 'error': 'AWS S3 not enabled'}
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            documents = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    documents.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'storage_class': obj['StorageClass']
                    })
            
            return {
                'success': True,
                'count': len(documents),
                'documents': documents
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_aws_info(self) -> Dict[str, Any]:
        """Get AWS integration status and information"""
        return {
            'aws_enabled': self.enabled,
            'services': {
                's3_enabled': self.s3_client is not None,
                'textract_enabled': self.textract_client is not None
            },
            'bucket': self.bucket_name if self.enabled else None,
            'region': self.region if self.enabled else None,
            'message': 'AWS integration is active' if self.enabled else 'AWS integration not configured. Set AWS_ENABLED=true and provide AWS credentials.'
        }
