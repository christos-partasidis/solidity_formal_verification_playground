// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BoxV2 {
    uint256 public value;

    function set(uint256 x) external {
        value = x * 2; // different behavior
    }
}
