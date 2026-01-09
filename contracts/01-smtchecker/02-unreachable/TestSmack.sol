// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TestSmack {
    function f(uint x) public pure {
        assert(x + 1 > x);
    }
}
