// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SimpleBox {
    uint256 private value;

    function set(uint256 x) external {
        // This should always hold:
        assert(x <= 1e18);
        value = x;
    }

    function get() external view returns (uint256) {
        return value;
    }
}