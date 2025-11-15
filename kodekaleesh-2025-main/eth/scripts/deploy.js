const { ethers } = require("hardhat");

async function main() {
  const factory = await ethers.getContractFactory("ProofRegistry");
  const contract = await factory.deploy();
  const deployed = await contract.waitForDeployment();
  const address = await deployed.getAddress();
  console.log("ProofRegistry deployed to:", address);

  // Optional: verify guidance
  console.log("\nTo verify (if Etherscan API key set):");
  console.log(`npx hardhat verify --network sepolia ${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
