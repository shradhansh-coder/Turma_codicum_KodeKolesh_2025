import { ethers } from 'ethers';

export const ETH_CHAIN_ID = (process.env.REACT_APP_ETH_CHAIN_ID || '11155111').trim(); // Sepolia by default
export const CONTRACT_ADDRESS = (process.env.REACT_APP_ETH_CONTRACT || '').trim();

export const CONTRACT_ABI = [
  {
    "inputs": [
      { "internalType": "bytes32", "name": "hash", "type": "bytes32" },
      { "internalType": "string", "name": "docId", "type": "string" }
    ],
    "name": "anchor",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [ { "internalType": "bytes32", "name": "hash", "type": "bytes32" } ],
    "name": "isAnchored",
    "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "anonymous": false,
    "inputs": [
      { "indexed": false, "internalType": "bytes32", "name": "hash", "type": "bytes32" },
      { "indexed": false, "internalType": "string", "name": "docId", "type": "string" },
      { "indexed": true, "internalType": "address", "name": "sender", "type": "address" },
      { "indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256" }
    ],
    "name": "Anchored",
    "type": "event"
  }
];

export async function getProviderAndSigner() {
  if (!window.ethereum) throw new Error('MetaMask not available');
  const provider = new ethers.BrowserProvider(window.ethereum);
  const accounts = await provider.send('eth_requestAccounts', []);
  const signer = await provider.getSigner();
  return { provider, signer, account: accounts[0] };
}

export async function ensureChain(provider) {
  const net = await provider.getNetwork();
  const current = ethers.toBeHex(net.chainId);
  const want = ethers.toBeHex(parseInt(ETH_CHAIN_ID, 10));
  if (current !== want) {
    try {
      await provider.send('wallet_switchEthereumChain', [{ chainId: ethers.toBeHex(parseInt(ETH_CHAIN_ID, 10)) }]);
    } catch (e) {
      // If the chain is not added in MetaMask, attempt to add for local Hardhat
      if (e && (e.code === 4902 || String(e.message || '').includes('Unrecognized chain ID'))) {
        try {
          await provider.send('wallet_addEthereumChain', [{
            chainId: want,
            chainName: parseInt(ETH_CHAIN_ID, 10) === 31337 ? 'Local Hardhat' : 'Custom Network',
            rpcUrls: parseInt(ETH_CHAIN_ID, 10) === 31337 ? ['http://127.0.0.1:8545'] : [],
            nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 }
          }]);
          await provider.send('wallet_switchEthereumChain', [{ chainId: want }]);
        } catch (addErr) {
          throw new Error('Please add/switch to the configured chain in MetaMask');
        }
      } else {
        throw new Error('Please switch wallet to the configured chain');
      }
    }
  }
}

export async function getContractWritable() {
  if (!CONTRACT_ADDRESS) throw new Error('Contract address not configured');
  const { provider, signer } = await getProviderAndSigner();
  await ensureChain(provider);
  // Sanity check: ensure the configured address has contract code
  const code = await provider.getCode(CONTRACT_ADDRESS);
  if (!code || code === '0x') {
    throw new Error('Configured ETH address is not a contract on this network');
  }
  return new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);
}

export async function getContractReadonly() {
  if (!CONTRACT_ADDRESS) throw new Error('Contract address not configured');
  if (!window.ethereum) throw new Error('MetaMask not available');
  const provider = new ethers.BrowserProvider(window.ethereum);
  await ensureChain(provider);
  const code = await provider.getCode(CONTRACT_ADDRESS);
  if (!code || code === '0x') {
    throw new Error('Configured ETH address is not a contract on this network');
  }
  return new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
}

export async function anchorOnChain(hashBytes32, docId) {
  if (!CONTRACT_ADDRESS) throw new Error('Contract address not configured');
  const { provider, signer } = await getProviderAndSigner();
  await ensureChain(provider);
  const code = await provider.getCode(CONTRACT_ADDRESS);
  if (!code || code === '0x') {
    throw new Error('Configured ETH address is not a contract on this network');
  }
  const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);
  const data = contract.interface.encodeFunctionData('anchor', [hashBytes32, docId]);
  return signer.sendTransaction({ to: CONTRACT_ADDRESS, data });
}

export function hexFromSha256(sha) {
  // sha is hex string without 0x from backend; normalize to 0x...
  let s = (sha || '').toLowerCase();
  if (!s.startsWith('0x')) s = '0x' + s;
  if (ethers.dataLength(s) !== 32) {
    // Accept arbitrary hex length by left-padding; on-chain we only need bytes32
    const stripped = s.slice(2);
    const padded = stripped.padStart(64, '0');
    s = '0x' + padded;
  }
  return s;
}

export async function diagnoseEth() {
  if (!window.ethereum) {
    return { ok: false, reason: 'No MetaMask', details: {} };
  }
  const provider = new ethers.BrowserProvider(window.ethereum);
  const net = await provider.getNetwork();
  const current = ethers.toBeHex(net.chainId);
  const want = ethers.toBeHex(parseInt(ETH_CHAIN_ID, 10));
  let code = '0x';
  try {
    if (CONTRACT_ADDRESS) {
      code = await provider.getCode(CONTRACT_ADDRESS);
    }
  } catch {}
  const isContract = !!code && code !== '0x';
  return {
    ok: isContract && current === want,
    reason: isContract ? (current === want ? 'ok' : 'wrong_chain') : 'no_code',
    details: {
      configuredChainId: want,
      walletChainId: current,
      contractAddress: CONTRACT_ADDRESS,
      codeLength: code ? code.length : 0,
      isContract
    }
  };
}
