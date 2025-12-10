// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AlwaysFalse {
    function bad(uint256 x) external pure {
        // This is mathematically false for some x.
        assert(x > x + 1);
    }
}
