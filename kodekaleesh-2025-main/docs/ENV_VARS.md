# Environment Variables Guide

This document explains every variable in the template files `eth/.env.example` and `frontend/.env.example`: what it does, where the value comes from, and security considerations.

---
## 1. Hardhat / Deployment (eth/.env.example)

File: `eth/.env.example` (Copy to `eth/.env` and fill values. NEVER commit the real `.env`).

| Variable | Purpose | Where To Get It | Secret? | Notes |
|----------|---------|-----------------|---------|-------|
| `SEPOLIA_RPC_URL` | JSON-RPC endpoint to talk to Sepolia testnet | Infura, Alchemy, QuickNode, Ankr, Chainstack; create a project and copy the HTTPS URL | No (but treat as semi-sensitive; abuse possible) | Format: `https://sepolia.infura.io/v3/<PROJECT_ID>` or provider-specific URL |
| `PRIVATE_KEY` | Deployer account key used by Hardhat to sign deployment transactions | MetaMask (Account Details → Export Private Key) of a throwaway test wallet funded with Sepolia ETH | YES | Must start with `0x`. Never use a production/main wallet. Rotate if leaked. |
| `ETHERSCAN_API_KEY` | Enables contract verification on Etherscan | Sign up on etherscan.io → API Keys | Mild | Optional; omit if not verifying. |

### Obtaining Values
1. **RPC URL**: Log in to Infura (or another provider), create a project, select Sepolia, copy the HTTPS endpoint.
2. **Private Key**: In MetaMask, switch to the test wallet → Settings → Account Details → Export Private Key (store securely while pasting into `.env`).
3. **Etherscan API Key** (optional): User dashboard → Create key → paste value.

### Security Practices
- Keep `eth/.env` out of version control (already ignored via `.gitignore`).
- Use a dedicated test wallet, never a wallet holding real funds.
- If `PRIVATE_KEY` is exposed, generate a new wallet and redeploy; old deployments can stay but future actions should use the new key.
- Limit permissions by using only the RPC project for deployment (avoid mixing with production projects).

### Common Mistakes
- Missing `0x` prefix on `PRIVATE_KEY` → Hardhat fails.
- Using mnemonic instead of private key in this template (Hardhat expects a raw key for our simple config). If you want mnemonic support, update `hardhat.config.js` accordingly.
- Typos in RPC URL leading to `ECONNREFUSED` or timeout errors.

---
## 2. Frontend (frontend/.env.example)

File: `frontend/.env.example` (Copy to `frontend/.env`). These values are exposed in the built React bundle—so never put secrets here.

| Variable | Purpose | Where To Get It | Secret? | Notes |
|----------|---------|-----------------|---------|-------|
| `REACT_APP_API_BASE` | Base URL for backend API calls | Your running Flask server URL (`http://localhost:5000/api` or deployed endpoint) | No | Must include `/api` suffix (as used in fetch calls). |
| `REACT_APP_ETH_CHAIN_ID` | Expected Ethereum chain for MetaMask | Sepolia = `11155111`; Hardhat local = `31337` | No | Used to enforce network match. |
| `REACT_APP_ETH_CONTRACT` | Deployed ProofRegistry contract address | Output from Hardhat deploy script (`deploy.js`) | No | Must be a valid `0x` address. |

### Obtaining Values
1. **API Base**: If running locally: `http://localhost:5000/api`. If deployed (e.g., behind Nginx), use that public endpoint.
2. **Chain ID**: Sepolia testnet → `11155111`. If using local Hardhat node, set to `31337`.
3. **Contract Address**: After running `npm run deploy:sepolia`, copy the printed address (e.g. `ProofRegistry deployed to: 0xABC...`).

### Updating Values
- Change `.env`, then restart `npm start` or rebuild (`npm run build`) so React picks new values.
- In production builds, ensure the hosting environment injects correct values before build time (CRA reads at build, not runtime).

### Security Practices
- Never put `PRIVATE_KEY`, seed phrases, API keys (Infura, Alchemy) or any credentials in frontend `.env`.
- If you accidentally expose a secret in frontend, assume compromise and rotate immediately.

### Common Mistakes
- Forgetting to restart dev server after changing `.env` → old values persist.
- Using incorrect chain ID → MetaMask switch fails.
- Empty `REACT_APP_ETH_CONTRACT` → Anchor/Verify buttons throw "Contract address not configured" errors.

---
## 3. Cross-Cutting Checklist

| Action | Why |
|--------|-----|
| Copy `.env.example` → `.env` (both folders) | Start from safe defaults |
| Keep secrets only in `eth/.env` | Prevent leakage in builds |
| Fund Sepolia wallet via faucet | Pay gas for deployment/anchor |
| Verify contract (optional) | Public transparency & ABI reference |
| Set contract address in frontend `.env` | Enable on-chain anchors |
| Restart frontend after edits | Load updated env vars |

---
## 4. Quick Commands (PowerShell)

```powershell
# Copy templates
Copy-Item "eth/.env.example" "eth/.env" -Force
Copy-Item "frontend/.env.example" "frontend/.env" -Force

# Deploy contract (Sepolia)
Push-Location "eth"; npm install; npm run compile; npm run deploy:sepolia; Pop-Location

# Edit frontend env
notepad "frontend/.env"  # paste deployed address

# Restart frontend
Push-Location "frontend"; npm start; Pop-Location
```

---
## 5. Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| MetaMask asks to switch network repeatedly | Wrong `REACT_APP_ETH_CHAIN_ID` | Set correct chain ID & restart frontend |
| "Contract address not configured" toast | Missing `REACT_APP_ETH_CONTRACT` | Add deployed address to `.env` |
| Hardhat compile ok, deploy fails with signer error | Malformed or missing `PRIVATE_KEY` | Ensure it begins with `0x` and is correct length (64 hex chars) |
| Anchor tx never appears | Wrong network in MetaMask | Switch to Sepolia or correct chain manually |
| `ECONNREFUSED` during deploy | Bad `SEPOLIA_RPC_URL` | Re-copy RPC URL from provider |

---
## 6. Rotation & Revocation

- If `PRIVATE_KEY` leaks: create new wallet, fund with test ETH, update `.env`, redeploy if necessary.
- Old contract can remain; users can interact via new key.
- You cannot "un-anchor" hashes; immutability is expected.

---
## 7. Future Enhancements

Potential additions:
- `PINATA_API_KEY` / `PINATA_SECRET` for IPFS pinning (if storing docs off-chain).
- `ALCHEMY_API_KEY` separated from full RPC URL for dynamic provider selection.
- `FRONTEND_BUILD_TIMESTAMP` for cache busting.
- `SENTRY_DSN` for error reporting.

---
## 8. Summary

| Folder | Sensitive? | Purpose |
|--------|------------|---------|
| `eth/.env` | Yes | Deployment & verification secrets |
| `frontend/.env` | No | Public config consumed at build time |

Follow least-privilege: keep only what you need; never mix production secrets into test environments.
