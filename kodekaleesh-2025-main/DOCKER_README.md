# Containerization Guide

## Images
- Backend: Python 3.11, Flask, Tesseract, runs as non-root `appuser`.
- Frontend: Multi-stage build; Node 18 builds static React, served by Nginx.

## Production Compose
`docker-compose.prod.yml` defines two services:
- `backend` on port 5000
- `frontend` (Nginx) on port 8080 serving React build

## Build & Run (Production)
```powershell
# From repository root
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
```
Visit: http://localhost:8080
Backend API: http://localhost:5000/api/health

## Environment Variables
Backend:
- `FLASK_DEBUG`: 0 for production
- `AWS_ENABLED`: toggle AWS integration
- `AWS_REGION`, `AWS_S3_BUCKET`: S3/Textract settings
- `SECRET_KEY`: token generation (change in production!)

Frontend build args (baked into static bundle):
- `REACT_APP_API_BASE`
- `REACT_APP_ETH_CHAIN_ID`
- `REACT_APP_ETH_CONTRACT`
Change them via compose `args` and rebuild.

## Development vs Production
Existing `docker-compose.yml` (dev): mounts source and runs hot-reload (`npm start`, `python app.py`).
Production file removes source mounts, uses optimized static build and non-root execution.

## Rebuild After Changes
Frontend env or code changes require:
```powershell
docker compose -f docker-compose.prod.yml build frontend
```
Backend dependency changes:
```powershell
docker compose -f docker-compose.prod.yml build backend
```

## Executing One-off Commands
```powershell
docker compose -f docker-compose.prod.yml run --rm backend python -m pytest -q
```

## Cleaning Up
```powershell
docker compose -f docker-compose.prod.yml down
# Remove dangling images
docker image prune -f
```

## Hardhat / Ethereum
For Sepolia, no local chain container needed. If you later want a local Hardhat node:
Add service:
```yaml
  hardhat:
    image: node:18-alpine
    working_dir: /workspace
    volumes:
      - ./eth:/workspace
    command: sh -c "npm install && npx hardhat node"
    ports:
      - "8545:8545"
```
Then point `REACT_APP_ETH_CHAIN_ID` to `31337` and redeploy contract locally.

## Security Checklist
- Replace `SECRET_KEY` with a strong secret.
- Set AWS credentials via docker secrets or environment (not committed).
- Restrict S3 bucket policies appropriately.
- Consider adding a WSGI server (gunicorn) for backend high-concurrency:
```dockerfile
# Example CMD:
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Troubleshooting
- Missing OCR: ensure Tesseract packages are present (already installed in Dockerfile).
- Incorrect contract: update compose args and rebuild frontend.
- CORS issues: verify frontend uses correct `REACT_APP_API_BASE`.

## Next Enhancements
- Add healthcheck to backend service.
- Implement gunicorn.
- Add CI pipeline to build & push images.

Enjoy your containerized stack!
