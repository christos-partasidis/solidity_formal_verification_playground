// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract RangeBox {
    uint256 public value;

    function set(uint256 x) external {
        require(x <= 1000, "too large");
        value = x;

        assert(value <= 1000);
    }
}