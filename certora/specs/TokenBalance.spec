/*
 * ============================================================================
 * Certora Verification Spec for TokenBalanceFixed
 * ============================================================================
 * 
 * This spec demonstrates GHOST VARIABLES - Certora's killer feature!
 * 
 * The Problem:
 *   SMTChecker CANNOT prove: Σ balances[addr] == totalSupply
 *   Why? It can't reason about quantified properties over mappings.
 * 
 * The Solution:
 *   Certora's ghost variables let us track "shadow state" that mirrors
 *   the contract's state. We use a ghost to track the sum of all balances,
 *   then prove it equals totalSupply.
 * 
 * Key Concepts:
 *   1. ghost - invisible state that only exists in the spec
 *   2. hook - intercepts storage operations to update ghost state
 *   3. invariant - proves the ghost tracks the real state correctly
 */

// ============================================================================
// METHODS BLOCK
// ============================================================================

methods {
    // View functions (envfree - don't depend on msg.sender, etc.)
    function balances(address) external returns (uint256) envfree;
    function totalSupply() external returns (uint256) envfree;
    function MAX_SUPPLY() external returns (uint256) envfree;
    
    // State-changing functions (need env for msg.sender, etc.)
    function mint(address, uint256) external;
    function burn(address, uint256) external;
    function transfer(address, address, uint256) external;
}

// ============================================================================
// GHOST VARIABLE
// ============================================================================
// A ghost is "shadow state" that exists only in the specification.
// The contract doesn't know about it - it's purely for verification.
//
// Here we create a ghost that tracks: Σ balances[addr] for all addresses
//
// Think of it as: "If we could sum every balance in the mapping, what would it be?"

ghost mathint sumOfBalances {
    // Axiom: ghost starts at 0 (before any storage writes)
    init_state axiom sumOfBalances == 0;
}

// ============================================================================
// HOOK
// ============================================================================
// A hook intercepts every SSTORE (storage write) to the balances mapping.
// When balances[addr] changes from oldValue to newValue, we update our ghost.
//
// Syntax: hook Sstore <variable>[KEY <keyType> <keyName>] <valueType> <newValue> (valueType <oldValue>)
//
// This says: "Whenever balances[addr] is written..."

hook Sstore balances[KEY address addr] uint256 newValue (uint256 oldValue) {
    // Update ghost: remove old value, add new value
    // This keeps sumOfBalances == Σ balances[addr] at all times
    sumOfBalances = sumOfBalances - oldValue + newValue;
}

// We also need a hook for SLOAD to ensure the ghost is consistent when reading
hook Sload uint256 value balances[KEY address addr] {
    // This axiom says: the value we're reading contributes to the sum
    // It helps the prover understand the relationship
    require sumOfBalances >= to_mathint(value);
}

// ============================================================================
// INVARIANTS
// ============================================================================

// THE MAIN INVARIANT - what SMTChecker couldn't prove!
// This says: the sum of all balances equals totalSupply
invariant sumOfBalancesEqualsTotalSupply()
    sumOfBalances == to_mathint(totalSupply())
    {
        preserved {
            // Inductive hypothesis: assume it holds before, prove it holds after
            require sumOfBalances == to_mathint(totalSupply());
        }
    }

// Secondary invariant: totalSupply never exceeds MAX_SUPPLY
invariant totalSupplyBounded()
    totalSupply() <= MAX_SUPPLY()
    {
        preserved {
            require totalSupply() <= MAX_SUPPLY();
        }
    }

// Individual balance never exceeds totalSupply
// (This one SMTChecker could prove, but let's verify it with Certora too)
invariant individualBalanceBounded(address addr)
    balances(addr) <= totalSupply()
    {
        preserved {
            require balances(addr) <= totalSupply();
            require sumOfBalances == to_mathint(totalSupply());
        }
    }

// ============================================================================
// RULES
// ============================================================================

// Rule: mint increases both balance and totalSupply by the same amount
rule mintIntegrity(address to, uint256 amount) {
    env e;
    
    uint256 balanceBefore = balances(to);
    uint256 totalBefore = totalSupply();
    
    mint(e, to, amount);
    
    uint256 balanceAfter = balances(to);
    uint256 totalAfter = totalSupply();
    
    assert balanceAfter == balanceBefore + amount, 
           "Mint should increase balance by amount";
    assert totalAfter == totalBefore + amount, 
           "Mint should increase totalSupply by amount";
}

// Rule: burn decreases both balance and totalSupply by the same amount
rule burnIntegrity(address from, uint256 amount) {
    env e;
    
    uint256 balanceBefore = balances(from);
    uint256 totalBefore = totalSupply();
    
    burn(e, from, amount);
    
    uint256 balanceAfter = balances(from);
    uint256 totalAfter = totalSupply();
    
    assert balanceAfter == balanceBefore - amount, 
           "Burn should decrease balance by amount";
    assert totalAfter == totalBefore - amount, 
           "Burn should decrease totalSupply by amount";
}

// Rule: transfer doesn't change totalSupply (conservation of tokens)
rule transferPreservesTotalSupply(address from, address to, uint256 amount) {
    env e;
    
    uint256 totalBefore = totalSupply();
    
    transfer(e, from, to, amount);
    
    uint256 totalAfter = totalSupply();
    
    assert totalAfter == totalBefore, 
           "Transfer should not change totalSupply";
}

// Rule: transfer moves tokens correctly
rule transferIntegrity(address from, address to, uint256 amount) {
    env e;
    
    // Precondition: from != to (as required by the contract)
    require from != to;
    
    uint256 fromBefore = balances(from);
    uint256 toBefore = balances(to);
    
    transfer(e, from, to, amount);
    
    uint256 fromAfter = balances(from);
    uint256 toAfter = balances(to);
    
    assert fromAfter == fromBefore - amount, 
           "Sender balance should decrease by amount";
    assert toAfter == toBefore + amount, 
           "Receiver balance should increase by amount";
}

// Rule: no function can create tokens out of thin air
// (totalSupply only increases via mint)
rule noTokenCreation(method f) {
    env e;
    calldataarg args;
    
    uint256 totalBefore = totalSupply();
    
    f(e, args);
    
    uint256 totalAfter = totalSupply();
    
    // If totalSupply increased, it must have been mint
    assert totalAfter > totalBefore => f.selector == sig:mint(address, uint256).selector,
           "Only mint can increase totalSupply";
}

// Rule: no function can destroy tokens except burn
rule noTokenDestruction(method f) {
    env e;
    calldataarg args;
    
    uint256 totalBefore = totalSupply();
    
    f(e, args);
    
    uint256 totalAfter = totalSupply();
    
    // If totalSupply decreased, it must have been burn
    assert totalAfter < totalBefore => f.selector == sig:burn(address, uint256).selector,
           "Only burn can decrease totalSupply";
}

// ============================================================================
// WHAT WE JUST PROVED (that SMTChecker couldn't!)
// ============================================================================
//
// 1. Σ balances[addr] == totalSupply  (THE BIG ONE!)
//    - Uses ghost variable to track the sum
//    - Hooks keep the ghost in sync with storage
//    - Invariant proves they're always equal
//
// 2. Token conservation
//    - Mint: increases sum and totalSupply equally
//    - Burn: decreases sum and totalSupply equally  
//    - Transfer: moves tokens without changing sum or totalSupply
//
// 3. No magic tokens
//    - Can't create tokens except via mint
//    - Can't destroy tokens except via burn
//
// This is the foundation of token correctness used by Aave, Compound, etc.
// ============================================================================
