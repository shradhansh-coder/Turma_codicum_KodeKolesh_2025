# Legal Document Intelligence MVP - Project Structure

## Project Overview

```
kodekaleesh-2025/
├── backend/                    # Flask REST API
│   ├── app.py                 # Main Flask application (270 lines)
│   ├── document_processor.py  # Document handling & storage (190 lines)
│   ├── summarizer.py          # Text summarization engine (100 lines)
│   ├── search_engine.py       # Search functionality (150 lines)
│   ├── Dockerfile             # Docker image for backend
│   ├── requirements.txt       # Python dependencies
│   └── uploads/               # Directory for uploaded files (auto-created)
│
├── frontend/                   # React Web Application
│   ├── App.jsx                # Main React component (150 lines)
│   ├── App.css                # Global styling (400+ lines)
│   ├── index.jsx              # React entry point
│   ├── components/            # Reusable components
│   │   ├── DocumentUpload.jsx # File upload with drag-drop
│   │   ├── DocumentList.jsx   # Document list table
│   │   ├── SearchPanel.jsx    # Search interface
│   │   └── SummaryPanel.jsx   # Document preview
│   ├── Dockerfile             # Docker image for frontend
│   ├── package.json           # Node dependencies
│   └── public/                # Static files (auto-created)
│
├── docs/                       # Documentation
│   ├── README.md              # Main documentation
│   ├── QUICKSTART.md          # Quick start guide
│   ├── ARCHITECTURE.md        # Technical architecture
│   ├── TESTING.md             # Testing guide
│   └── PROJECT_STRUCTURE.md   # This file
│
├── docker-compose.yml         # Docker Compose configuration
├── run.sh                      # Linux/macOS startup script
├── run.bat                     # Windows startup script
├── .gitignore                  # Git ignore rules
└── README.md                   # Root README

```

## Key Files

### Backend Files

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | Flask REST API with 9 endpoints | ~270 |
| `document_processor.py` | Document upload, storage, metadata extraction | ~190 |
| `summarizer.py` | Extractive text summarization | ~100 |
| `search_engine.py` | Full-text search and filtering | ~150 |
| `requirements.txt` | Python dependencies | 4 |

### Frontend Files

| File | Purpose | Lines |
|------|---------|-------|
| `App.jsx` | Main app component with routing | ~150 |
| `App.css` | Complete styling (responsive) | ~400+ |
| `components/*.jsx` | Reusable UI components | ~250 |
| `package.json` | Node.js dependencies | ~30 |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Complete MVP documentation |
| `QUICKSTART.md` | Setup and testing instructions |
| `ARCHITECTURE.md` | Technical design and future enhancements |
| `TESTING.md` | Testing strategies and examples |

## Code Statistics

### Backend
- **Total Lines**: ~810
- **Python Version**: 3.9+
- **Main Dependencies**: Flask 3.0, Flask-CORS 4.0
- **API Endpoints**: 9
- **Classes**: 3 (DocumentProcessor, DocumentSummarizer, SearchEngine)

### Frontend
- **Total Lines**: ~800+
- **React Version**: 18.2
- **Components**: 5 (App + 4 sub-components)
- **Pages**: 3 (Upload, Documents, Search)
- **CSS Lines**: 400+

## API Endpoints

### Document Management
```
POST   /api/upload                    Upload document
GET    /api/documents                 List all documents
GET    /api/documents/<id>/summary    Get document summary
GET    /api/documents/<id>/metadata   Get document metadata
DELETE /api/documents/<id>            Delete document
```

### Search & Analysis
```
POST   /api/search                    Search documents
POST   /api/analyze                   Analyze multiple documents
```

### Health
```
GET    /api/health                    Health check
```

## Data Flow

### Document Upload
```
1. User selects file → 2. Frontend validates → 3. POST /api/upload
4. Backend saves file → 5. Extract metadata → 6. Store in JSON
7. Return document_id → 8. UI updates
```

### Search
```
1. User enters query → 2. POST /api/search
3. Backend indexes documents → 4. Score and rank
5. Extract snippets → 6. Return results → 7. Display in UI
```

### Summarization
```
1. User clicks View → 2. GET /api/documents/{id}/summary
3. Split into sentences → 4. Score sentences
5. Select top 3 → 6. Return in order → 7. Display in sidebar
```

## Configuration

### Environment Variables

Create `.env` in root:
```
FLASK_ENV=development
FLASK_DEBUG=True
REACT_APP_API_URL=http://localhost:5000/api
```

### Flask Configuration

```python
# app.py
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

## Dependencies

### Backend (requirements.txt)
```
Flask==3.0.0
Flask-CORS==4.0.0
Werkzeug==3.0.1
python-dotenv==1.0.0
```

### Frontend (package.json)
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-scripts": "5.0.1"
}
```

## File Size Limits

- **Upload**: 50MB max (configured in app.py)
- **Storage**: JSON-based (no practical limit)
- **Search Index**: In-memory (RAM usage scales with documents)

## Performance Targets

- **Upload**: < 2 seconds (for 5MB)
- **Search**: < 500ms (for 100 documents)
- **Summarization**: < 200ms
- **Page Load**: < 1 second

## Future Enhancements

### Short Term (v0.2)
- [ ] Database integration (PostgreSQL)
- [ ] Elasticsearch for search
- [ ] User authentication
- [ ] Docker deployment

### Medium Term (v0.3)
- [ ] LLM-based summarization
- [ ] Named entity recognition
- [ ] Document similarity
- [ ] Batch processing

### Long Term (v1.0)
- [ ] Multi-language support
- [ ] Case timeline visualization
- [ ] ML-based case prediction
- [ ] Mobile app
- [ ] Enterprise licensing

## Testing Checklist

- [ ] Unit tests (backend functions)
- [ ] Integration tests (API endpoints)
- [ ] End-to-end tests (full workflow)
- [ ] Load testing (100+ documents)
- [ ] Security testing (CORS, input validation)
- [ ] Browser compatibility (Chrome, Firefox, Safari)

## Deployment Options

### Development
```bash
./run.sh         # Linux/macOS
run.bat         # Windows
```

### Docker
```bash
docker-compose up
```

### Production
- Cloud Platform: AWS, GCP, Azure
- Container Orchestration: Kubernetes
- Database: PostgreSQL
- Search: Elasticsearch

## Support & Troubleshooting

### Common Issues

1. **Port in use**: Change port in app.py or use different PORT
2. **Module not found**: Run `pip install -r requirements.txt`
3. **CORS errors**: Ensure backend running on localhost:5000
4. **File upload fails**: Check upload folder permissions

### Debug Logs

```bash
# Backend
export FLASK_DEBUG=1
python app.py

# Frontend  
npm start -- --debug
```

---

**Total Code Lines**: ~1,600+ lines of production code
**Complexity**: MVP suitable for hackathon submission
**Time to Setup**: < 5 minutes
**Time to Deploy**: < 10 minutes

Ready for development! 🚀
