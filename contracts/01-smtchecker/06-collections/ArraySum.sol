// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title ArraySum - Array Invariants with SMTChecker
/// @notice Demonstrates reasoning about bounded arrays
/// @dev Shows both capabilities and limitations with array invariants

contract ArraySum {
    uint256[] public values;
    uint256 public sum;
    uint256 public constant MAX_SIZE = 10;

    /// @notice Adds a value to the array
    /// @dev Fails to maintain sum invariant
    function add(uint256 value) public {
        require(values.length < MAX_SIZE, "Array full");
        
        values.push(value);
        sum += value;
        
        // This assertion checks if sum tracking is correct
        // For small arrays, SMTChecker might verify this
        // For larger arrays, it becomes intractable
        assert(sum >= value);
    }

    /// @notice Gets a value at an index
    function get(uint256 index) public view returns (uint256) {
        require(index < values.length, "Index out of bounds");
        return values[index];
    }

    /// @notice Updates a value in the array
    /// @dev This breaks the sum invariant!
    function update(uint256 index, uint256 newValue) public {
        require(index < values.length, "Index out of bounds");
        
        // BUG: We update the array but don't update the sum!
        values[index] = newValue;
        
        // This assertion will FAIL in many cases
        // SMTChecker will find counterexamples
        assert(sum >= newValue);
    }
}

/// Expected SMTChecker Output:
/// Warning: CHC: Assertion violation might happen here.
/// Function: update
///
/// Counterexample scenario:
/// 1. add(10) → values = [10], sum = 10
/// 2. update(0, 20) → values = [20], sum = 10 (stale!)
/// 3. assert(sum >= newValue) → assert(10 >= 20) → FAILS
///
/// Key Insights:
/// - SMTChecker can reason about bounded arrays
/// - It tracks array contents symbolically for small sizes
/// - It finds bugs in aggregate update logic
/// - But: cannot verify "sum == Σ values[i]" for arbitrary length arrays
///
/// Limitation: SMTChecker doesn't verify loop invariants automatically
/// Solution: Use explicit tracking + manual loop invariants (covered in solc-verify phase)
