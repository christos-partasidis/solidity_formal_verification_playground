// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title SafePercentage - Arithmetic Proof (Failing Version)
/// @notice Demonstrates SMTChecker's ability to verify arithmetic properties
/// @dev Shows common arithmetic pitfalls: division rounding, percentage bounds

contract SafePercentage {
    uint256 public constant BASIS_POINTS = 10000; // 100% = 10000 basis points

    /// @notice Calculates a percentage of a value using basis points
    /// @dev This version has potential issues SMTChecker will catch
    /// @param value The base value
    /// @param bps Basis points (e.g., 500 = 5%)
    /// @return result The calculated percentage
    function calculatePercentage(uint256 value, uint256 bps) public pure returns (uint256 result) {
        // Potential issue: multiplication overflow for large values
        result = (value * bps) / BASIS_POINTS;
        
        // Invariant: result should never exceed the original value
        // This will FAIL when bps > 10000 (>100%)
        assert(result <= value);
    }

    /// @notice Distributes a total amount among recipients with percentages
    /// @dev Demonstrates rounding invariants
    /// @param total The total amount to distribute
    /// @param percentage1 First recipient's percentage (in bps)
    /// @param percentage2 Second recipient's percentage (in bps)
    function distribute(
        uint256 total,
        uint256 percentage1,
        uint256 percentage2
    ) public pure returns (uint256 share1, uint256 share2, uint256 remainder) {
        share1 = (total * percentage1) / BASIS_POINTS;
        share2 = (total * percentage2) / BASIS_POINTS;
        remainder = total - share1 - share2;
        
        // Invariant: shares + remainder should equal total
        // This holds due to how we calculate remainder
        assert(share1 + share2 + remainder == total);
        
        // Invariant: no share exceeds total
        // This will FAIL if percentage > 10000
        assert(share1 <= total);
        assert(share2 <= total);
    }

    /// @notice Calculates compound interest approximation
    /// @dev Shows arithmetic property verification
    /// @param principal The starting amount
    /// @param ratePerPeriod Interest rate per period (in bps)
    /// @param periods Number of periods
    function compoundInterest(
        uint256 principal,
        uint256 ratePerPeriod,
        uint256 periods
    ) public pure returns (uint256 finalAmount) {
        finalAmount = principal;
        
        for (uint256 i = 0; i < periods; i++) {
            uint256 interest = (finalAmount * ratePerPeriod) / BASIS_POINTS;
            finalAmount = finalAmount + interest;
            
            // Invariant: amount should always grow (for positive rate)
            // SMTChecker will verify this for bounded loops
            assert(finalAmount >= principal);
        }
        
        return finalAmount;
    }
}

/// Expected SMTChecker Output:
/// Warning: CHC: Assertion violation happens here.
/// Function: calculatePercentage
/// Counterexample:
/// value = 100
/// bps = 20000 (200%)
/// result = 200 > 100 → assertion fails
///
/// Key Insights:
/// 1. SMTChecker finds arithmetic edge cases automatically
/// 2. Overflow protection in 0.8+ doesn't prevent logic errors
/// 3. Percentage calculations need explicit bounds checking
/// 4. Division rounding requires careful invariant design
