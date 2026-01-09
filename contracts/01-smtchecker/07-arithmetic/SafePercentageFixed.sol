// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title SafePercentageFixed - Arithmetic Proof (Correct Version)
/// @notice Demonstrates provable arithmetic properties with proper preconditions
/// @dev Shows how to write verifiably correct percentage calculations

contract SafePercentageFixed {
    uint256 public constant BASIS_POINTS = 10000; // 100% = 10000 basis points
    uint256 public constant MAX_BPS = 10000;      // Maximum 100%

    /// @notice Calculates a percentage of a value using basis points
    /// @dev Preconditions ensure result never exceeds input
    /// @param value The base value
    /// @param bps Basis points (e.g., 500 = 5%, max 10000 = 100%)
    /// @return result The calculated percentage
    function calculatePercentage(uint256 value, uint256 bps) public pure returns (uint256 result) {
        // Precondition: bps must be at most 100%
        require(bps <= MAX_BPS, "Percentage exceeds 100%");
        
        // Precondition: prevent multiplication overflow
        // value * bps <= type(uint256).max
        require(value <= type(uint256).max / BASIS_POINTS, "Value too large");
        
        result = (value * bps) / BASIS_POINTS;
        
        // Now this invariant HOLDS
        // Proof: bps <= 10000 ⇒ (value * bps) / 10000 <= value
        assert(result <= value);
    }

    /// @notice Distributes a total amount among recipients with percentages
    /// @dev All percentages must sum to at most 100%
    /// @param total The total amount to distribute
    /// @param percentage1 First recipient's percentage (in bps)
    /// @param percentage2 Second recipient's percentage (in bps)
    function distribute(
        uint256 total,
        uint256 percentage1,
        uint256 percentage2
    ) public pure returns (uint256 share1, uint256 share2, uint256 remainder) {
        // Preconditions: valid percentages
        require(percentage1 <= MAX_BPS, "Percentage1 exceeds 100%");
        require(percentage2 <= MAX_BPS, "Percentage2 exceeds 100%");
        require(percentage1 + percentage2 <= MAX_BPS, "Total exceeds 100%");
        
        // Precondition: prevent overflow
        require(total <= type(uint256).max / BASIS_POINTS, "Total too large");
        
        share1 = (total * percentage1) / BASIS_POINTS;
        share2 = (total * percentage2) / BASIS_POINTS;
        remainder = total - share1 - share2;
        
        // All invariants now HOLD
        assert(share1 + share2 + remainder == total);
        assert(share1 <= total);
        assert(share2 <= total);
        assert(remainder <= total);
    }

    /// @notice Safe division with rounding direction control
    /// @dev Demonstrates rounding invariants
    /// @param numerator The dividend
    /// @param denominator The divisor
    /// @param roundUp Whether to round up (true) or down (false)
    function safeDivide(
        uint256 numerator,
        uint256 denominator,
        bool roundUp
    ) public pure returns (uint256 result) {
        require(denominator > 0, "Division by zero");
        
        if (roundUp && numerator % denominator != 0) {
            result = (numerator / denominator) + 1;
            
            // Rounding up invariant: result * denominator >= numerator
            assert(result * denominator >= numerator);
        } else {
            result = numerator / denominator;
            
            // Rounding down invariant: result * denominator <= numerator
            assert(result * denominator <= numerator);
        }
    }

    /// @notice Calculates fee with minimum guarantee
    /// @dev Common DeFi pattern: max(calculated_fee, minimum_fee)
    /// @param amount The base amount
    /// @param feeBps Fee in basis points
    /// @param minFee Minimum fee to charge
    function calculateFee(
        uint256 amount,
        uint256 feeBps,
        uint256 minFee
    ) public pure returns (uint256 fee) {
        require(feeBps <= MAX_BPS, "Fee exceeds 100%");
        require(amount <= type(uint256).max / BASIS_POINTS, "Amount too large");
        
        uint256 calculatedFee = (amount * feeBps) / BASIS_POINTS;
        
        // Take the maximum of calculated fee and minimum fee
        fee = calculatedFee > minFee ? calculatedFee : minFee;
        
        // Invariants
        assert(fee >= minFee);              // Never below minimum
        assert(fee >= calculatedFee);       // Never below calculated (when minFee applies)
        
        // Note: fee might exceed amount if minFee > amount
        // This is intentional for small transactions
    }
}

/// Expected SMTChecker Output:
/// Info: CHC: All assertions hold!
///
/// Key Arithmetic Verification Patterns:
///
/// 1. **Percentage Bounds**:
///    - Always validate bps <= 10000 for "at most 100%" semantics
///    - This ensures (value * bps) / 10000 <= value
///
/// 2. **Overflow Prevention**:
///    - Check value <= MAX / multiplier before multiplication
///    - Solidity 0.8+ reverts on overflow, but explicit checks enable proofs
///
/// 3. **Division Properties**:
///    - Round down: result * divisor <= dividend
///    - Round up: result * divisor >= dividend
///    - These are verifiable with SMTChecker
///
/// 4. **Sum Invariants**:
///    - When distributing, shares + remainder == total (by construction)
///    - Each share <= total (when percentages <= 100%)
///
/// 5. **Why This Matters for DeFi/CBDC**:
///    - Interest calculations must be provably correct
///    - Fee distributions must not lose or create value
///    - Rounding must be predictable and fair
