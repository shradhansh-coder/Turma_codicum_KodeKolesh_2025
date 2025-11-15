# Legal Document Intelligence MVP

An AI-powered system for intelligent legal document analysis, summarization, and search.

## 🎯 Problem Statement

Modern judicial ecosystems face overwhelming volumes of legal documents—case files, precedents, statutory updates, and procedural records. Courts and practitioners operate with fragmented information, resulting in:

- Prolonged case cycles
- Inconsistent legal interpretations
- Systemic inefficiencies
- Extended backlogs
- Limited access to justice

## 🚀 Solution

This MVP provides:

1. **Document Upload & Processing**: Upload legal documents (PDF, TXT, DOCX)
2. **Intelligent Summarization**: AI-powered document summaries
3. **Full-Text Search**: Fast semantic search across documents
4. **Document Analysis**: Extract metadata, keywords, and entities
5. **Metadata Extraction**: Automatic case names, dates, and sections detection

## 📋 Features

### Current MVP Capabilities

- ✅ Document upload and processing
- ✅ Document library management
- ✅ Quick summarization
- ✅ Cross-document search
- ✅ Entity extraction (case names, dates, sections)
- ✅ Keyword analysis
- ✅ Document metadata viewing
- ✅ OCR text extraction from images (JPG, PNG, BMP, GIF, TIFF)
- ✅ AWS S3 document storage (optional)
- ✅ AWS Textract advanced OCR (optional)

## 🏗️ Architecture

```
kodekaleesh-2025/
├── backend/              # Flask REST API
│   ├── app.py           # Main Flask application
│   ├── document_processor.py  # Document handling & storage
│   ├── summarizer.py    # Summarization engine
│   ├── search_engine.py # Search functionality
│   ├── ocr_processor.py # OCR text extraction
│   ├── aws_integration.py # AWS S3 & Textract integration
│   └── requirements.txt
│
├── frontend/            # React web application
│   ├── src/
│   │   ├── App.jsx         # Main application
│   │   ├── App.css         # Styling
│   │   ├── index.js        # Entry point
│   │   └── components/
│   │       ├── DocumentUpload.jsx
│   │       ├── DocumentList.jsx
│   │       ├── SearchPanel.jsx
│   │       └── SummaryPanel.jsx
│   ├── public/
│   │   └── index.html
│   └── package.json
│
└── docs/               # Documentation
    ├── README.md
    ├── QUICKSTART.md
    ├── ARCHITECTURE.md
    ├── OCR_INTEGRATION.md
    └── AWS_SETUP.md
```

## 🔌 API Endpoints

### Documents
- `POST /api/upload` - Upload a document (TXT, DOCX, PDF, JPG, PNG with OCR)
- `GET /api/documents` - List all documents
- `GET /api/documents/<id>/summary` - Get document summary
- `GET /api/documents/<id>/metadata` - Get document metadata
- `DELETE /api/documents/<id>` - Delete a document

### OCR
- `GET /api/ocr/status` - Check OCR availability
- `POST /api/ocr/extract` - Extract text from image

### AWS Integration
- `GET /api/aws/status` - Check AWS status
- `POST /api/aws/upload` - Upload to S3
- `POST /api/aws/textract/extract` - Extract with Textract
- `POST /api/aws/textract/analyze` - Analyze document structure
- `GET /api/aws/documents` - List S3 documents

### Search & Analysis
- `POST /api/search` - Search documents
- `POST /api/analyze` - Analyze documents

### Health
- `GET /api/health` - Health check

## 📦 Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend

```bash
cd frontend
npm install
npm start
```

The UI will be available at `http://localhost:3000`

## 💻 Usage

### 1. Upload a Document
- Click the "Upload" tab
- Drag & drop a legal document or click to browse
- Document is processed automatically

### 2. View Documents
- Click "Documents" tab
- See all uploaded documents
- Click "View" to see summary and metadata

### 3. Search
- Click "Search" tab
- Enter search query (e.g., "plaintiff", "contract")
- View results with relevance scores and context snippets

## 🔄 Data Flow

```
Document Upload
    ↓
Processing (extract content, estimate pages)
    ↓
Storage (JSON-based)
    ↓
Indexing (for search)
    ↓
Available for Search, Summarization, Analysis
```

## 📊 Data Storage

Currently uses JSON-based storage (`documents.json`) for MVP simplicity.

**Upgrade Path**: 
- PostgreSQL + Elasticsearch for production
- Vector embeddings for semantic search
- Advanced NLP for better summarization

## 🚀 Future Enhancements

1. **Advanced NLP**
   - LLM-based summarization (GPT-4, Claude)
   - Named entity recognition
   - Legal opinion classification

2. **Machine Learning**
   - Case outcome prediction
   - Document similarity matching
   - Precedent recommendation

3. **Database & Indexing**
   - PostgreSQL integration
   - Elasticsearch for full-text search
   - Vector embeddings for semantic search

4. **Features**
   - Multi-language support
   - Document versioning
   - Collaborative annotations
   - Case timeline visualization
   - Automated document classification

5. **Compliance**
   - Legal document compliance checking
   - Risk assessment
   - Audit trails

## 🛠️ Technology Stack

**Backend**:
- Python 3.9+
- Flask 3.0
- Flask-CORS

**Frontend**:
- React 18
- Vanilla CSS
- Fetch API

**Storage**:
- JSON (MVP)
- PostgreSQL (future)

**Search**:
- Simple regex-based (MVP)
- Elasticsearch (future)

## 📝 Example Workflow

1. **Judge uploads case file** → Automatic processing
2. **System summarizes document** → Quick overview
3. **Search for similar cases** → Find precedents
4. **Analyze multiple documents** → Extract key themes
5. **Generate insights** → Support decision-making

## ⚖️ Legal Considerations

- Document confidentiality
- Data retention policies
- Audit logging
- User authentication & authorization
- Encryption for sensitive data

## 🤝 Contributing

This is an MVP. Contributions welcome for:
- NLP improvements
- Database integration
- UI/UX enhancements
- Testing frameworks
- Deployment automation

## 📄 License

MIT License - See LICENSE file

## 👥 Support

For issues or questions, please open an issue in the repository.

---

**Status**: MVP v0.1.0 - Ready for hackathon submission and feedback
