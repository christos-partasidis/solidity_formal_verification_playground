// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AlwaysFalseFixed {
    function badfixed(uint256 x) external pure {
        // Precondition restricts execution domain.
        require(x == type(uint256).max, "x must be max uint");

        // Under this condition, x + 1 overflows and reverts,
        // so the assert is never reached in an unsafe state.
        assert(x > x + 1);
    }
}
