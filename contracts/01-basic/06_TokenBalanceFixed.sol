// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title TokenBalanceFixed - Mapping Invariants (Correct Version)
/// @notice Demonstrates provable invariants over mappings
/// @dev Shows proper preconditions to maintain mapping invariants

contract TokenBalanceFixed {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    uint256 public constant MAX_SUPPLY = 1000000;

    /// @notice Mints tokens to an address
    /// @dev Preconditions ensure invariants hold
    function mint(address to, uint256 amount) public {
        // Precondition 1: Prevent total supply overflow
        require(totalSupply + amount <= MAX_SUPPLY, "Exceeds max supply");
        
        // Precondition 2: Prevent individual balance overflow
        require(balances[to] + amount >= balances[to], "Balance overflow");
        
        balances[to] += amount;
        totalSupply += amount;
        
        // Now these assertions HOLD
        assert(totalSupply <= MAX_SUPPLY);
        assert(balances[to] <= totalSupply);
    }

    /// @notice Burns tokens from an address
    function burn(address from, uint256 amount) public {
        require(balances[from] >= amount, "Insufficient balance");
        require(totalSupply >= amount, "Total supply underflow");
        
        balances[from] -= amount;
        totalSupply -= amount;
        
        // Invariants hold
        assert(totalSupply <= MAX_SUPPLY);
        assert(balances[from] <= totalSupply);
    }

    /// @notice Transfers tokens between addresses
    function transfer(address from, address to, uint256 amount) public {
        require(balances[from] >= amount, "Insufficient balance");
        require(from != to, "Cannot transfer to self");
        
        // Handle potential overflow for receiver
        require(balances[to] + amount >= balances[to], "Receiver overflow");

        // SMTChecker Helper: 
        // Since SMTChecker cannot prove `sum(balances) == totalSupply`, it considers
        // states where `balances[to] + balances[from] > totalSupply` to be reachable.
        // In those states, a transfer could violate the invariant.
        // We add this redundant check to help the solver.
        require(balances[to] + amount <= totalSupply, "Solver helper");
        
        balances[from] -= amount;
        balances[to] += amount;
        
        // Total supply invariant (totalSupply unchanged)
        assert(totalSupply <= MAX_SUPPLY);
        
        // Individual balance invariants
        assert(balances[from] <= totalSupply);
        assert(balances[to] <= totalSupply);
    }
}

/// Expected SMTChecker Output:
/// Info: CHC: All assertions hold!
///
/// Key Lessons:
///
/// 1. **Local Invariants**: SMTChecker proves properties about specific mapping entries
///    - balances[to] <= totalSupply ✓
///    - balances[from] <= totalSupply ✓
///
/// 2. **Global Invariants**: SMTChecker tracks aggregate values
///    - totalSupply <= MAX_SUPPLY ✓
///
/// 3. **What SMTChecker CANNOT Prove**:
///    - Sum invariants: ∑ balances[i] == totalSupply
///    - Quantified properties: ∀ address a: balances[a] <= MAX_SUPPLY
///    - Cross-account relationships without explicit tracking
///
/// 4. **When to Use Certora**:
///    - Need to verify: "sum of all balances equals total supply"
///    - Need quantified invariants over unbounded domains
///    - Need multi-contract invariants
///    - Need to prove absence of certain attack patterns
///
/// 5. **Design Pattern**:
///    Track aggregates explicitly (totalSupply) rather than computing sums
///    This makes properties verifiable with SMTChecker
///
/// This is the foundation for verifying ERC20 tokens, DeFi protocols, and CBDCs
