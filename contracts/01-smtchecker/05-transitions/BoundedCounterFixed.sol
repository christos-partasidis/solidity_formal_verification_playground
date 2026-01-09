// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title BoundedCounterFixed - State Transition Invariant (Correct Version)
/// @notice Demonstrates how to maintain invariants across all state transitions
/// @dev The invariant `counter <= MAX` is enforced via preconditions

contract BoundedCounterFixed {
    uint256 public counter;
    uint256 public constant MAX = 100;

    /// @notice Increments the counter by a given amount
    /// @dev Precondition ensures the invariant is preserved
    function increment(uint256 amount) public {
        // Precondition: enforce that the new value stays within bounds
        require(counter + amount <= MAX, "Exceeds maximum");
        
        counter += amount;
        
        // Now this assertion HOLDS
        assert(counter <= MAX);
    }

    /// @notice Decrements the counter by a given amount
    function decrement(uint256 amount) public {
        require(amount <= counter, "Underflow");
        counter -= amount;
        
        // Invariant holds
        assert(counter <= MAX);
    }

    /// @notice Resets counter to zero
    function reset() public {
        counter = 0;
        
        // Invariant holds
        assert(counter <= MAX);
    }

    /// @notice Sets counter to a specific value
    /// @dev Another state transition that must preserve the invariant
    function setValue(uint256 newValue) public {
        require(newValue <= MAX, "Value too large");
        counter = newValue;
        
        // Invariant holds
        assert(counter <= MAX);
    }
}

/// Expected SMTChecker Output:
/// Info: CHC: All assertions hold!
///
/// Key Insight:
/// The invariant counter <= MAX is now a CONTRACT INVARIANT that holds:
/// - At construction (counter = 0)
/// - After every public function execution
/// - Across all possible execution paths
///
/// This is the foundation for proving correctness in more complex systems.
