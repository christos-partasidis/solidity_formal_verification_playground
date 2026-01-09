// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title TokenBalance - Mapping Invariants (Simple Version)
/// @notice Demonstrates invariant reasoning over mappings with SMTChecker
/// @dev Shows what SMTChecker CAN verify about mappings

contract TokenBalance {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    uint256 public constant MAX_SUPPLY = 1000000;

    /// @notice Mints tokens to an address
    /// @dev This version has NO invariant enforcement - will fail verification
    function mint(address to, uint256 amount) public {
        balances[to] += amount;
        totalSupply += amount;
        
        // Invariant 1: Total supply never exceeds max
        // This will FAIL - no precondition prevents overflow
        assert(totalSupply <= MAX_SUPPLY);
        
        // Invariant 2: Individual balance doesn't exceed total supply
        // This HOLDS because we increment both together
        assert(balances[to] <= totalSupply);
    }

    /// @notice Burns tokens from an address
    function burn(address from, uint256 amount) public {
        require(balances[from] >= amount, "Insufficient balance");
        
        balances[from] -= amount;
        totalSupply -= amount;
        
        // Individual balance invariant still holds
        assert(balances[from] <= totalSupply);
    }

    /// @notice Transfers tokens between addresses
    function transfer(address from, address to, uint256 amount) public {
        require(balances[from] >= amount, "Insufficient balance");
        
        balances[from] -= amount;
        balances[to] += amount;
        
        // Total supply doesn't change during transfers
        // These assertions explore what SMTChecker can verify
        assert(balances[from] <= totalSupply);
        assert(balances[to] <= totalSupply);
    }
}

/// Expected SMTChecker Output:
/// Warning: CHC: Assertion violation happens here.
/// Function: mint
/// Counterexample:
/// totalSupply = 0
/// to = 0x0
/// amount = 1000001
///
/// The prover finds that minting 1000001 tokens violates MAX_SUPPLY
///
/// Key Observations:
/// 1. SMTChecker CAN reason about individual mapping entries
/// 2. SMTChecker CAN track relationships between mapping values and totals
/// 3. SMTChecker CANNOT verify sum invariants (∑ balances[i] == totalSupply)
/// 4. For complex quantified invariants, we need Certora Prover
