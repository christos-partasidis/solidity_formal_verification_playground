// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title BoundedCounter - State Transition Invariant (Failing Version)
/// @notice Demonstrates multi-function invariant reasoning with SMTChecker
/// @dev The invariant `counter <= MAX` should hold after every transaction
///      This version FAILS because increment() doesn't enforce the bound

contract BoundedCounter {
    uint256 public counter;
    uint256 public constant MAX = 100;

    /// @notice Increments the counter by a given amount
    /// @dev SMTChecker will find a counterexample where counter exceeds MAX
    function increment(uint256 amount) public {
        counter += amount;
        
        // Invariant assertion - this will FAIL
        assert(counter <= MAX);
    }

    /// @notice Decrements the counter by a given amount
    function decrement(uint256 amount) public {
        require(amount <= counter, "Underflow");
        counter -= amount;
        
        // This assertion holds because we can't go below 0
        assert(counter <= MAX);
    }

    /// @notice Resets counter to zero
    function reset() public {
        counter = 0;
        
        // This always holds
        assert(counter <= MAX);
    }
}

/// Expected SMTChecker Output:
/// Warning: CHC: Assertion violation happens here.
/// Counterexample:
/// counter = 0
/// amount = 101
/// Transaction trace:
/// BoundedCounter.constructor()
/// State: counter = 0
/// BoundedCounter.increment(101)
///
/// The prover finds that calling increment(101) when counter = 0 
/// violates the invariant counter <= 100
