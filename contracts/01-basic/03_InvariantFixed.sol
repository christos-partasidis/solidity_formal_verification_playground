// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract InvariantFixed {
    uint256 public balance;

    function set(uint256 x) external {
        require(x <= 1000, "too large");
        balance = x;
    }

    function checkInvariant() external view {
        assert(balance <= 1000);
    }
}
