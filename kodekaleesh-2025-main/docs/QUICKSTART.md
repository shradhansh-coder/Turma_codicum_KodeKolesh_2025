# Quick Start Guide

## Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

## Setup Instructions

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For OCR support (optional but recommended):
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr

# Start the Flask server
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
```

### 2. Frontend Setup (New Terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the React development server
npm start
```

Expected output:
```
On Your Network: http://192.168.x.x:3000
```

Your browser should open to `http://localhost:3000`

## Ethereum (Optional - On-chain Proof)

1) Create env files from templates and fill values

```powershell
Copy-Item "c:\Users\RARCH\kodekaleesh-2025\eth\.env.example" "c:\Users\RARCH\kodekaleesh-2025\eth\.env" -Force
Copy-Item "c:\Users\RARCH\kodekaleesh-2025\frontend\.env.example" "c:\Users\RARCH\kodekaleesh-2025\frontend\.env" -Force
```

- In `eth/.env` (private): set `SEPOLIA_RPC_URL`, `PRIVATE_KEY` (throwaway dev wallet), and optional `ETHERSCAN_API_KEY`.
- In `frontend/.env` (public): set `REACT_APP_API_BASE`, `REACT_APP_ETH_CHAIN_ID`, and `REACT_APP_ETH_CONTRACT` (after deploy).

2) Deploy ProofRegistry to Sepolia

```powershell
Push-Location "c:\Users\RARCH\kodekaleesh-2025\eth"; npm install; npm run compile; npm run deploy:sepolia; Pop-Location
```

3) Configure frontend with the deployed address

```powershell
notepad "c:\Users\RARCH\kodekaleesh-2025\frontend\.env"
# Set REACT_APP_ETH_CONTRACT to the printed address
```

4) Restart frontend to pick up env changes

```powershell
Push-Location "c:\Users\RARCH\kodekaleesh-2025\frontend"; npm start; Pop-Location
```

## Testing the MVP

### Test Document Upload

1. Create a sample text file (e.g., `legal_document.txt`):
```
COURT OF APPEAL DECISION

Case: Smith v. Johnson
Date: November 14, 2025
Judge: Hon. Justice Anderson

FACTS:
The plaintiff, John Smith, filed suit against the defendant, Mary Johnson, 
alleging breach of contract. The contract in question was signed on 
January 15, 2024.

RULING:
The court finds in favor of the plaintiff. The defendant is ordered to pay 
damages of $50,000 plus court costs.

APPEAL:
This decision may be appealed within 30 days of issuance.
```

2. Go to `http://localhost:3000`
3. Click **Upload** tab
4. Drag & drop the file or click to browse
5. Click **Documents** tab to see it listed
6. Click **View** to see the summary

### Test OCR Image Upload

1. Take a screenshot or use an image containing legal text
2. Save as PNG, JPG, BMP, GIF, or TIFF
3. Click **Upload** tab
4. Drag & drop the image file
5. The system will automatically extract text using OCR
6. View the results in **Documents** tab

**Note:** OCR requires Tesseract installation:
- **Windows:** Download installer from https://github.com/UB-Mannheim/tesseract/wiki
- **macOS:** `brew install tesseract`
- **Linux:** `sudo apt-get install tesseract-ocr`

### Test Search

1. In the **Search** tab, try queries like:
   - "Smith v. Johnson"
   - "breach of contract"
   - "damages"
   - "appeal"

2. View the search results with relevance scores and context snippets

### Test Document Management

- **View**: See document summary and metadata
- **Delete**: Remove documents from the system
- **Analyze**: Get keyword and theme insights

## File Structure

```
backend/
├── app.py                  # Main Flask application
├── document_processor.py   # Document handling
├── summarizer.py          # Text summarization
├── search_engine.py       # Search functionality
├── ocr_processor.py       # OCR text extraction
├── requirements.txt       # Python dependencies
└── uploads/              # Uploaded documents (auto-created)

frontend/
├── src/
│   ├── App.jsx            # Main React component
│   ├── App.css            # Styling
│   ├── index.js           # React entry point
│   └── components/        # React components
│       ├── DocumentUpload.jsx
│       ├── DocumentList.jsx
│       ├── SearchPanel.jsx
│       └── SummaryPanel.jsx
├── public/
│   ├── index.html         # HTML entry point
├── package.json           # NPM dependencies
└── Dockerfile             # Docker configuration
```

## Troubleshooting

### Port Already in Use

**Backend (Port 5000)**:
```bash
# Windows - Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or use a different port in app.py
app.run(port=5001)
```

**Frontend (Port 3000)**:
```bash
# Set different port
set PORT=3001 && npm start  # Windows
PORT=3001 npm start          # macOS/Linux
```

### CORS Issues

If you see CORS errors, ensure:
1. Backend is running on `http://localhost:5000`
2. Frontend API_BASE is set to `http://localhost:5000/api`

### Module Not Found

```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

## API Testing with curl

```bash
# Health check
curl http://localhost:5000/api/health

# List documents
curl http://localhost:5000/api/documents

# Search documents
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "breach of contract"}'
```

## Next Steps

1. ✅ Explore the MVP features
2. ⬜ Add more test documents
3. ⬜ Test search functionality
4. ⬜ Integrate with LLMs for better summarization
5. ⬜ Add database integration
6. ⬜ Deploy to cloud platform

## Support

For issues:
1. Check console logs (browser DevTools for frontend, terminal for backend)
2. Ensure ports 3000 and 5000 are available
3. Verify Python and Node versions
4. Check all dependencies are installed

---

Happy hacking! 🚀
