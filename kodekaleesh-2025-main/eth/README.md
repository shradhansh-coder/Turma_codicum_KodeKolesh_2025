# ProofRegistry (Ethereum) - Hardhat Project

This folder contains a minimal Solidity contract and Hardhat setup to anchor document hashes on Ethereum (e.g., Sepolia).

## Contract
`contracts/ProofRegistry.sol`
  - `function anchor(bytes32 hash, string docId)`
  - `function isAnchored(bytes32 hash) view returns (bool)`
  - `event Anchored(bytes32 hash, string docId, address indexed sender, uint256 timestamp)`

Matches the frontend ABI used in `frontend/src/eth/eth.js`.

## Quick Start

1. Install dependencies
```powershell
Push-Location "c:\Users\RARCH\kodekaleesh-2025\eth"; npm install; Pop-Location
```

2. Compile
```powershell
Push-Location "c:\Users\RARCH\kodekaleesh-2025\eth"; npm run compile; Pop-Location
```

3. Configure Sepolia (optional)
Create `c:\Users\RARCH\kodekaleesh-2025\eth\.env`:
```
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/<YOUR_PROJECT_ID>
PRIVATE_KEY=<YOUR_WALLET_PRIVATE_KEY>
ETHERSCAN_API_KEY=<optional>
```
Notes:
- Use a separate dev wallet with test ETH only.
- Never commit secrets.

4. Deploy to Sepolia
```powershell
Push-Location "c:\Users\RARCH\kodekaleesh-2025\eth"; npm run deploy:sepolia; Pop-Location
```
Copy the printed address.

5. Configure Frontend
Create/update `c:\Users\RARCH\kodekaleesh-2025\frontend\.env`:
```
REACT_APP_API_BASE=http://localhost:5000/api
REACT_APP_ETH_CHAIN_ID=11155111
REACT_APP_ETH_CONTRACT=0xYourDeployedContractAddress
```
Then rebuild or restart the frontend.

## Local Testing (Hardhat Network)
You can deploy locally and test with Hardhat network.
```powershell
Push-Location "c:\Users\RARCH\kodekaleesh-2025\eth"; npx hardhat node; Pop-Location
```
In a new terminal:
```powershell
Push-Location "c:\Users\RARCH\kodekaleesh-2025\eth"; npm run deploy:localhost; Pop-Location
```
Add the Hardhat network to MetaMask (http://127.0.0.1:8545, chainId 31337) and import one of the printed private keys for testing.

## Verification
If `ETHERSCAN_API_KEY` is set:
```powershell
npx hardhat verify --network sepolia <DEPLOYED_ADDRESS>
```