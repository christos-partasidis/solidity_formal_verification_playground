// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SumBox {
    uint256 public a;
    uint256 public b;

    function setA(uint256 x) external {
        a = x;
    }

    function setB(uint256 y) external {
        b = y;
    }

    function checkInvariant() external view {
        // Invariant attempt: sum must always fit in uint256
        // This is false unless restricted!
        assert(a + b >= a);  
    }
}
