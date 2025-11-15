from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from document_processor import DocumentProcessor
from summarizer import DocumentSummarizer
from search_engine import SearchEngine
from ocr_processor import OCRProcessor
from auth import register_user, authenticate_user, create_token, auth_required
from blockchain import SimpleChain

# Load environment variables from .env file
load_dotenv()

# Optional AWS import
try:
    from aws_integration import AWSIntegration
    aws = AWSIntegration()
except ImportError:
    aws = None

app = Flask(__name__)
CORS(app)
# Initialize simple blockchain ledger for integrity proofs
CHAIN_FILE = os.path.join(os.path.dirname(__file__), 'chain.json')
ledger = SimpleChain(CHAIN_FILE)


# ============ Response Wrapper Utilities ============

def error_response(message, error_code=400, details=None):
    """Standardized error response"""
    response = {
        'success': False,
        'error': message,
        'error_code': error_code
    }
    if details:
        response['details'] = details
    return jsonify(response), error_code

def success_response(data=None, message=None, status_code=200):
    """Standardized success response"""
    response = {'success': True}
    if message:
        response['message'] = message
    if data:
        response.update(data)
    return jsonify(response), status_code

def validate_json(required_fields=None):
    """Validate JSON request and required fields"""
    if not request.is_json:
        return error_response('Content-Type must be application/json', 400)
    
    try:
        data = request.get_json()
    except Exception as e:
        return error_response('Invalid JSON format', 400, str(e))
    
    if required_fields:
        missing = [f for f in required_fields if f not in data]
        if missing:
            return error_response(
                'Missing required fields',
                400,
                {'missing_fields': missing}
            )
    
    return None  # No error

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff'}
OCR_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize services
processor = DocumentProcessor()
summarizer = DocumentSummarizer()
search_engine = SearchEngine()
ocr = OCRProcessor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return success_response({
        'status': 'healthy',
        'service': 'Legal Document Intelligence API'
    })

# ============ Authentication ============

@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    json_error = validate_json(required_fields=['email', 'password'])
    if json_error:
        return json_error
    data = request.get_json()
    ok, res = register_user(data.get('email'), data.get('password'))
    if not ok:
        return error_response(str(res), 400)
    token = create_token(os.environ.get('SECRET_KEY', 'dev-secret'), res)
    return success_response({'token': token, 'user': res}, 'Registered')


@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    json_error = validate_json(required_fields=['email', 'password'])
    if json_error:
        return json_error
    data = request.get_json()
    ok, res = authenticate_user(data.get('email'), data.get('password'))
    if not ok:
        return error_response(str(res), 401)
    token = create_token(os.environ.get('SECRET_KEY', 'dev-secret'), res)
    return success_response({'token': token, 'user': res}, 'Logged in')


@app.route('/api/auth/me', methods=['GET'])
@auth_required
def auth_me():
    return success_response({'user': g.user})

@app.route('/api/upload', methods=['POST'])
@auth_required
def upload_document():
    """Upload and process a legal document or image"""
    try:
        if 'file' not in request.files:
            return error_response('No file provided in request', 400)
        
        file = request.files['file']
        
        if file.filename == '':
            return error_response('No file selected', 400)
        
        if not allowed_file(file.filename):
            return error_response(
                'File type not allowed',
                400,
                {
                    'allowed_types': list(ALLOWED_EXTENSIONS),
                    'provided': file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'unknown'
                }
            )
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return error_response(
                'File too large',
                413,
                {'max_size_mb': MAX_FILE_SIZE / (1024*1024), 'file_size_mb': file_size / (1024*1024)}
            )
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Check if file is an image (needs OCR)
        file_ext = filename.rsplit('.', 1)[1].lower()
        document_data = None
        ocr_result = None
        
        if file_ext in OCR_EXTENSIONS:
            # Process with OCR
            ocr_result = ocr.extract_text_with_preprocessing(filepath)
            if ocr_result['success']:
                document_data = processor.process_ocr_result(filepath, filename, ocr_result)
            else:
                return error_response(
                    'OCR processing failed',
                    400,
                    {
                        'error': ocr_result.get('error'),
                        'hint': 'Install Tesseract OCR: pip install pytesseract pillow'
                    }
                )
        else:
            document_data = processor.process(filepath, filename)
        
        response_data = {
            'document_id': document_data['id'],
            'filename': filename,
            'pages': document_data['pages'],
            'text_length': document_data['text_length'],
            'file_type': 'image_ocr' if file_ext in OCR_EXTENSIONS else 'document'
        }
        
        if ocr_result:
            response_data['ocr_confidence'] = ocr_result.get('confidence', 0)
        
        message = 'Image processed with OCR' if file_ext in OCR_EXTENSIONS else 'Document uploaded successfully'
        return success_response(response_data, message, 201)
    
    except Exception as e:
        return error_response('Upload failed', 500, str(e))


# ============ Proof of Integrity (Simple Chain) ============

@app.route('/api/proof/anchor', methods=['POST'])
@auth_required
def proof_anchor():
    json_error = validate_json(required_fields=['document_id'])
    if json_error:
        return json_error
    try:
        data = request.get_json()
        doc_id = data.get('document_id', '').strip()
        if not doc_id:
            return error_response('document_id is required', 400)
        doc = processor.get_document(doc_id)
        if not doc:
            return error_response('Document not found', 404)
        # compute hash from file path if exists
        filepath = None
        # document_processor stores filename and path conventionally
        filename = doc.get('filename')
        if filename:
            fp = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(fp):
                filepath = fp
        if not filepath:
            # fallback to content hash
            content = doc.get('content', '')
            import hashlib
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        else:
            file_hash = SimpleChain.sha256_file(filepath)
        block = ledger.add_block({'document_id': doc_id, 'sha256': file_hash})
        return success_response({'block': block}, 'Anchored')
    except Exception as e:
        return error_response('Anchor failed', 500, str(e))


@app.route('/api/proof/verify/<doc_id>', methods=['GET'])
@auth_required
def proof_verify(doc_id):
    try:
        matches = ledger.find_by_document_id(doc_id)
        return success_response({'anchored': len(matches) > 0, 'entries': matches})
    except Exception as e:
        return error_response('Verify failed', 500, str(e))


@app.route('/api/proof/chain', methods=['GET'])
@auth_required
def proof_chain():
    try:
        valid = ledger.verify()
        # return limited info for brevity
        import json as _json
        with open(CHAIN_FILE, 'r', encoding='utf-8') as f:
            chain = _json.load(f)
        return success_response({'valid': valid, 'length': len(chain), 'tip': chain[-1] if chain else None})
    except Exception as e:
        return error_response('Chain retrieval failed', 500, str(e))


@app.route('/api/proof/hash/<doc_id>', methods=['GET'])
@auth_required
def proof_hash(doc_id):
    """Return the SHA-256 hash of the stored document file or content for Ethereum anchoring."""
    try:
        if not doc_id or len(doc_id.strip()) == 0:
            return error_response('Invalid document ID', 400)
        doc = processor.get_document(doc_id)
        if not doc:
            return error_response('Document not found', 404)
        filename = doc.get('filename')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) if filename else None
        if filepath and os.path.exists(filepath):
            digest = SimpleChain.sha256_file(filepath)
        else:
            import hashlib
            digest = hashlib.sha256((doc.get('content') or '').encode('utf-8')).hexdigest()
        return success_response({'document_id': doc_id, 'sha256': digest})
    except Exception as e:
        return error_response('Failed to compute hash', 500, str(e))

@app.route('/api/documents', methods=['GET'])
@auth_required
def list_documents():
    """List all uploaded documents"""
    try:
        documents = processor.list_documents()
        return success_response({
            'documents': documents,
            'total': len(documents)
        })
    except Exception as e:
        return error_response('Failed to list documents', 500, str(e))

@app.route('/api/documents/<doc_id>/summary', methods=['GET'])
@auth_required
def summarize_document(doc_id):
    """Generate summary of a document"""
    try:
        if not doc_id or len(doc_id.strip()) == 0:
            return error_response('Invalid document ID', 400)
        
        doc = processor.get_document(doc_id)
        if not doc:
            return error_response('Document not found', 404)
        
        try:
            max_length = int(request.args.get('max_length', 500))
            if max_length < 50 or max_length > 2000:
                return error_response('max_length must be between 50 and 2000', 400)
        except ValueError:
            return error_response('max_length must be an integer', 400)
        
        summary = summarizer.summarize(doc['content'], max_length=max_length)
        
        return success_response({
            'document_id': doc_id,
            'summary': summary,
            'original_length': len(doc['content']),
            'summary_length': len(summary)
        })
    except Exception as e:
        return error_response('Summarization failed', 500, str(e))

@app.route('/api/documents/<doc_id>/metadata', methods=['GET'])
@auth_required
def document_metadata(doc_id):
    """Get document metadata and extracted information"""
    try:
        if not doc_id or len(doc_id.strip()) == 0:
            return error_response('Invalid document ID', 400)
        
        doc = processor.get_document(doc_id)
        if not doc:
            return error_response('Document not found', 404)
        
        metadata = processor.extract_metadata(doc_id)
        
        return success_response({
            'document_id': doc_id,
            'filename': doc['filename'],
            'uploaded_at': doc['created_at'],
            'metadata': metadata
        })
    except Exception as e:
        return error_response('Failed to retrieve metadata', 500, str(e))

@app.route('/api/documents/<doc_id>', methods=['DELETE'])
@auth_required
def delete_document(doc_id):
    """Delete a document"""
    try:
        if not doc_id or len(doc_id.strip()) == 0:
            return error_response('Invalid document ID', 400)
        
        success = processor.delete_document(doc_id)
        if not success:
            return error_response('Document not found', 404)
        
        return success_response({'document_id': doc_id}, 'Document deleted successfully')
    except Exception as e:
        return error_response('Failed to delete document', 500, str(e))

@app.route('/api/search', methods=['POST'])
@auth_required
def search_documents():
    """Search across documents"""
    # Validate JSON
    json_error = validate_json(required_fields=['query'])
    if json_error:
        return json_error
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return error_response('Search query cannot be empty', 400)
        
        if len(query) > 500:
            return error_response('Search query too long (max 500 chars)', 400)
        
        limit = min(int(data.get('limit', 10)), 100)  # Max 100 results
        
        results = search_engine.search(query, limit=limit)
        
        return success_response({
            'query': query,
            'results': results,
            'count': len(results)
        })
    except ValueError as e:
        return error_response('Invalid request parameters', 400, str(e))
    except Exception as e:
        return error_response('Search failed', 500, str(e))

@app.route('/api/analyze', methods=['POST'])
@auth_required
def analyze_documents():
    """Analyze documents for legal insights"""
    # Validate JSON
    json_error = validate_json(required_fields=['document_ids'])
    if json_error:
        return json_error
    
    try:
        data = request.get_json()
        doc_ids = data.get('document_ids', [])
        analysis_type = data.get('type', 'general')
        
        if not isinstance(doc_ids, list) or not doc_ids:
            return error_response('document_ids must be a non-empty list', 400)
        
        if len(doc_ids) > 50:
            return error_response('Cannot analyze more than 50 documents at once', 400)
        
        analysis = processor.analyze(doc_ids, analysis_type)
        
        return success_response({
            'analysis_type': analysis_type,
            'documents_analyzed': len(doc_ids),
            'insights': analysis
        })
    except Exception as e:
        return error_response('Analysis failed', 500, str(e))

@app.route('/api/ocr/status', methods=['GET'])
def ocr_status():
    """Check if OCR is available"""
    return success_response({
        'ocr_available': ocr.is_available(),
        'supported_formats': list(ocr.SUPPORTED_FORMATS),
        'status': 'available' if ocr.is_available() else 'not_installed'
    })

@app.route('/api/ocr/extract', methods=['POST'])
@auth_required
def ocr_extract():
    """Extract text from image using OCR"""
    try:
        if 'file' not in request.files:
            return error_response('No file provided in request', 400)
        
        file = request.files['file']
        
        if file.filename == '':
            return error_response('No file selected', 400)
        
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in OCR_EXTENSIONS:
            return error_response(
                'File format not supported for OCR',
                400,
                {
                    'supported_formats': list(OCR_EXTENSIONS),
                    'provided': file_ext or 'unknown'
                }
            )
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'ocr_' + filename)
        file.save(filepath)
        
        # Process with preprocessing for better results
        result = ocr.extract_text_with_preprocessing(filepath)
        
        if result['success']:
            return success_response({
                'text': result.get('text', ''),
                'confidence': result.get('confidence', 0),
                'word_count': result.get('word_count', 0),
                'character_count': result.get('character_count', 0)
            }, 'Text extracted successfully')
        else:
            return error_response(
                'OCR extraction failed',
                400,
                {'error': result.get('error', 'Unknown error')}
            )
    
    except Exception as e:
        return error_response('OCR extraction failed', 500, str(e))

# ============ AWS Integration Endpoints ============

@app.route('/api/aws/status', methods=['GET'])
def aws_status():
    """Check AWS integration status"""
    if not aws:
        return success_response({
            'aws_enabled': False,
            'message': 'AWS integration not available'
        })
    
    return success_response(aws.get_aws_info())

@app.route('/api/aws/upload', methods=['POST'])
@auth_required
def aws_upload():
    """Upload document to AWS S3"""
    if not aws or not aws.is_enabled():
        return error_response('AWS S3 not enabled or configured', 400)
    
    try:
        json_error = validate_json(required_fields=['document_id', 'file_path'])
        if json_error:
            return json_error
        
        data = request.get_json()
        document_id = data.get('document_id', '').strip()
        file_path = data.get('file_path', '').strip()
        filename = data.get('filename', 'document').strip()
        
        if not document_id or not file_path:
            return error_response(
                'Missing required fields',
                400,
                {'required': ['document_id', 'file_path']}
            )
        
        if not os.path.exists(file_path):
            return error_response(
                'File not found',
                404,
                {'path': file_path}
            )
        
        result = aws.upload_to_s3(file_path, document_id, filename)
        
        if result['success']:
            return success_response(result, 'Document uploaded to S3')
        else:
            return error_response(
                'S3 upload failed',
                400,
                {'error': result.get('error')}
            )
    
    except Exception as e:
        return error_response('AWS upload failed', 500, str(e))

@app.route('/api/aws/textract/extract', methods=['POST'])
@auth_required
def aws_textract_extract():
    """Extract text from document using AWS Textract"""
    if not aws or not aws.is_enabled():
        return error_response('AWS Textract not enabled or configured', 400)
    
    try:
        json_error = validate_json(required_fields=['file_path'])
        if json_error:
            return json_error
        
        data = request.get_json()
        file_path = data.get('file_path', '').strip()
        
        if not file_path:
            return error_response('file_path is required', 400)
        
        if not os.path.exists(file_path):
            return error_response(
                'File not found',
                404,
                {'path': file_path}
            )
        
        result = aws.extract_text_with_textract(file_path)
        
        if result['success']:
            return success_response(result, 'Text extracted using Textract')
        else:
            return error_response(
                'Textract extraction failed',
                400,
                {'error': result.get('error')}
            )
    
    except Exception as e:
        return error_response('Textract extraction failed', 500, str(e))

@app.route('/api/aws/textract/analyze', methods=['POST'])
@auth_required
def aws_textract_analyze():
    """Analyze document structure with AWS Textract"""
    if not aws or not aws.is_enabled():
        return error_response('AWS Textract not enabled or configured', 400)
    
    try:
        json_error = validate_json(required_fields=['file_path'])
        if json_error:
            return json_error
        
        data = request.get_json()
        file_path = data.get('file_path', '').strip()
        
        if not file_path:
            return error_response('file_path is required', 400)
        
        if not os.path.exists(file_path):
            return error_response(
                'File not found',
                404,
                {'path': file_path}
            )
        
        result = aws.analyze_document_with_textract(file_path)
        
        if result['success']:
            return success_response(result, 'Document analyzed using Textract')
        else:
            return error_response(
                'Textract analysis failed',
                400,
                {'error': result.get('error')}
            )
    
    except Exception as e:
        return error_response('Textract analysis failed', 500, str(e))

@app.route('/api/aws/documents', methods=['GET'])
@auth_required
def aws_list_documents():
    """List documents in S3"""
    if not aws or not aws.is_enabled():
        return error_response('AWS S3 not enabled or configured', 400)
    
    try:
        prefix = request.args.get('prefix', 'documents/').strip()
        result = aws.list_documents_in_s3(prefix)
        
        if result['success']:
            return success_response(result, 'Documents listed from S3')
        else:
            return error_response(
                'Failed to list S3 documents',
                400,
                {'error': result.get('error')}
            )
    
    except Exception as e:
        return error_response('S3 listing failed', 500, str(e))

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request"""
    return error_response('Bad request', 400)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found"""
    return error_response('Endpoint not found', 404)

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 Payload Too Large"""
    return error_response(
        'File too large. Maximum size is 50MB',
        413,
        {'max_size_mb': MAX_FILE_SIZE / (1024*1024)}
    )

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error"""
    return error_response('Internal server error', 500)

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed"""
    return error_response('Method not allowed', 405)

if __name__ == '__main__':
    debug_flag = os.environ.get('FLASK_DEBUG', '1')
    debug = True if debug_flag == '1' else False
    app.run(debug=debug, host='0.0.0.0', port=5000)
