// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ProofRegistry {
    mapping(bytes32 => bool) private _anchored;

    event Anchored(bytes32 hash, string docId, address indexed sender, uint256 timestamp);

    function anchor(bytes32 hash, string calldata docId) external {
        require(!_anchored[hash], "Already anchored");
        _anchored[hash] = true;
        emit Anchored(hash, docId, msg.sender, block.timestamp);
    }

    function isAnchored(bytes32 hash) external view returns (bool) {
        return _anchored[hash];
    }
}
