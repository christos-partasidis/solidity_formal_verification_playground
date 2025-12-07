// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract InvariantFail {
    uint256 public balance;

    function set(uint256 x) external {
        balance = x;
    }

    // Attempted invariant:
    // "balance must always be <= 1000"
    function checkInvariant() external view {
        assert(balance <= 1000);
    }
}
