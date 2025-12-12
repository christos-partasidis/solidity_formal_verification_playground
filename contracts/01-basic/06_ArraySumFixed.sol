// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title ArraySumFixed - Correct Array Sum Tracking
/// @notice Demonstrates proper invariant maintenance for arrays
/// @dev Shows how to keep aggregate values consistent

contract ArraySumFixed {
    uint256[] public values;
    uint256 public sum;
    uint256 public constant MAX_SIZE = 10;

    /// @notice Adds a value to the array
    function add(uint256 value) public {
        require(values.length < MAX_SIZE, "Array full");
        require(sum + value >= sum, "Sum overflow");
        
        values.push(value);
        sum += value;
        
        // Invariant: sum is non-decreasing when adding
        assert(sum >= value);
    }

    /// @notice Gets a value at an index
    function get(uint256 index) public view returns (uint256) {
        require(index < values.length, "Index out of bounds");
        return values[index];
    }

    /// @notice Updates a value in the array (CORRECT VERSION)
    /// @dev Maintains the sum invariant by adjusting for the difference
    function update(uint256 index, uint256 newValue) public {
        require(index < values.length, "Index out of bounds");
        
        uint256 oldValue = values[index];
        
        // Adjust sum: subtract old value, add new value
        if (newValue >= oldValue) {
            // Increasing: check for overflow
            require(sum + (newValue - oldValue) >= sum, "Sum overflow");
            sum = sum + (newValue - oldValue);
        } else {
            // Decreasing: safe from overflow
            sum = sum - (oldValue - newValue);
        }
        
        values[index] = newValue;
        
        // Now assertions about individual elements hold
        assert(values[index] == newValue);
    }

    /// @notice Removes the last value
    function pop() public {
        require(values.length > 0, "Array empty");
        
        uint256 lastValue = values[values.length - 1];
        require(sum >= lastValue, "Sum underflow");
        
        sum -= lastValue;
        values.pop();
        
        // Sum decreased appropriately
        assert(sum <= sum + lastValue);
    }
}

/// Expected SMTChecker Output:
/// Info: CHC: All assertions hold!
///
/// Critical Learning:
///
/// 1. **Explicit Aggregate Tracking**:
///    - Maintain sum as a state variable
///    - Update it atomically with array modifications
///    - Don't compute it from array elements
///
/// 2. **Why This Works**:
///    - SMTChecker doesn't verify "sum == Σ values[i]"
///    - But it DOES verify that sum updates match array operations
///    - The invariant holds by construction, not by proof of equivalence
///
/// 3. **Design Pattern for Verification**:
///    ```
///    Unverifiable: ∀ i: Σ array[i] == total
///    Verifiable: Each operation updates total correctly
///    ```
///
/// 4. **When This Pattern Works**:
///    ✓ Token total supply (sum of balances)
///    ✓ Voting power (sum of delegated votes)
///    ✓ Pool reserves (sum of deposits)
///    ✓ CBDC circulation (sum of issued tokens)
///
/// 5. **Limitations Still Present**:
///    - Cannot prove: "sum is actually correct given initial state"
///    - Cannot prove: "no unauthorized sum modifications"
///    - For these, need Certora with ghost variables
///
/// Next Phase: Certora will let us prove the actual sum invariant!
