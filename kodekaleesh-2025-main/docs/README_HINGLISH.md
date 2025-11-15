# Project Explainer (Hinglish)

## Kya Karta Hai (What)
- Legal/contract documents upload karke text extract karta hai (PDF/TXT + images via OCR).
- Smart summarization aur fast search deta hai taaki key points jaldi milen.
- Document integrity ko blockchain par anchor/verify karta hai:
  - Local append-only ledger (chain.json)
  - Ethereum Sepolia via MetaMask (public verifiable proof)
- Secure access: login/register with token-based auth.
- Production-friendly UI: dark mode, toasts, keyboard shortcuts, multi-file upload.

## Kyu Zaroori Hai (Why)
- Review time kam: summarize + search hours bachata hai.
- Tamper-proof integrity: same content ka verifiable proof milta hai (audit/compliance).
- Public trust: Ethereum anchoring se independent verification possible.
- Simple UX + security: adoption easy aur safe.

## Kaise Kaam Karta Hai (How)
- Frontend (React):
  - Login → token store → sab API calls `Authorization: Bearer <token>` ke saath.
  - Upload → progress + errors/success toasts.
  - Documents list/view/delete/search/summary UI se.
  - “Anchor (ETH)” / “Verify (ETH)” buttons MetaMask ke through contract call karte hain.
- Backend (Flask):
  - Upload receive → image ho toh OCR (pytesseract), warna direct parse.
  - Summarizer + search engine text par kaam karte hain.
  - Auth: JSON user store + signed tokens; protected routes.
  - Integrity:
    - Local: `chain.json` me SHA-256 hash store/verify.
    - Ethereum: `/api/proof/hash/<doc_id>` se SHA-256; frontend `bytes32` me convert karke anchor/verify.
- Blockchain (Hardhat + Solidity):
  - `ProofRegistry.sol`:
    - `anchor(bytes32 hash, string docId)`
    - `isAnchored(bytes32 hash) view returns (bool)`
    - `event Anchored(bytes32, string, address indexed, uint256)`
  - Sepolia (11155111) default; MetaMask tx sign karta hai.

## User Journey (End-to-End)
1. Login/Register
2. Document upload → auto process (OCR/parse)
3. Summary dekhna + Search karna
4. Integrity ensure (Local ledger)
5. Public proof (Anchor on Ethereum) → later “Verify (ETH)”

## Tech Stack
- Frontend: React 18, `react-hot-toast`, `ethers.js`, dark mode.
- Backend: Flask, Flask-CORS, tokens (itsdangerous), OCR (pytesseract), local blockchain ledger.
- Web3: Hardhat, Solidity `ProofRegistry`, Sepolia testnet.

## Config (Quick)
- Frontend `.env`:
  - `REACT_APP_API_BASE=http://localhost:5000/api`
  - `REACT_APP_ETH_CHAIN_ID=11155111`
  - `REACT_APP_ETH_CONTRACT=0xDeployedContractAddress`
- Backend env (optional):
  - `FLASK_DEBUG=0` (production-like run)

## Run (Local)
```powershell
# Backend
Push-Location "c:\Users\RARCH\kodekaleesh-2025\backend"; $env:FLASK_DEBUG="0"; ^
  & 'C:\Users\RARCH\AppData\Local\Programs\Python\Python311\python.exe' app.py; Pop-Location

# Frontend
Push-Location "c:\Users\RARCH\kodekaleesh-2025\frontend"; npm install; npm start; Pop-Location
```

## Ethereum (Sepolia)
```powershell
# In eth/
Push-Location "c:\Users\RARCH\kodekaleesh-2025\eth"; npm install; npm run compile; ^
  npm run deploy:sepolia; Pop-Location
# Address copy karke frontend .env me REACT_APP_ETH_CONTRACT set karein; frontend restart/rebuild.
```

## Notes
- MetaMask on Sepolia; test ETH chahiye.
- On-chain sirf hash jata hai, content nahi → privacy safe.
- AWS S3/Textract endpoints present; enable karke cloud OCR/storage flows add ho sakte hain.