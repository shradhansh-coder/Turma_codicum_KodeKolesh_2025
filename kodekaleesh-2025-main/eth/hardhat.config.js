require('dotenv').config();
require('@nomicfoundation/hardhat-toolbox');

const { SEPOLIA_RPC_URL, PRIVATE_KEY } = process.env;

const networks = { hardhat: {} };
if (SEPOLIA_RPC_URL && PRIVATE_KEY) {
  networks.sepolia = {
    url: SEPOLIA_RPC_URL,
    accounts: [PRIVATE_KEY]
  };
}

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: '0.8.24',
    settings: {
      optimizer: { enabled: true, runs: 200 }
    }
  },
  networks,
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY || undefined
  }
};
