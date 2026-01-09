/*
 * ============================================================================
 * Certora Verification Spec for BoundedCounterFixed
 * ============================================================================
 * 
 * This is our first CVL (Certora Verification Language) specification.
 * CVL is a declarative language for expressing properties about smart contracts.
 * 
 * Key concepts demonstrated:
 *   1. methods block - declaring the contract interface
 *   2. envfree annotation - for pure/view functions
 *   3. env type - for state-changing functions
 *   4. invariants - properties that always hold
 *   5. rules - properties about function behavior
 */

// ============================================================================
// METHODS BLOCK
// ============================================================================
// The methods block declares which contract functions CVL can interact with.
// Think of it as an "interface" declaration for the prover.
//
// Syntax: function name(params) visibility returns (type) [annotations];

methods {
    // --------------------------------------------------------------------
    // VIEW FUNCTIONS (marked envfree)
    // --------------------------------------------------------------------
    // `envfree` means these functions don't depend on the transaction
    // environment (msg.sender, msg.value, block.timestamp, etc.)
    // 
    // Why? Because counter() is a simple getter that just reads storage.
    // It doesn't care WHO is calling or WHEN - it returns the same value.
    //
    // With envfree, we can call these directly: counter() instead of counter(e)
    
    function counter() external returns (uint256) envfree;
    function MAX() external returns (uint256) envfree;
    
    // --------------------------------------------------------------------
    // STATE-CHANGING FUNCTIONS (no envfree)
    // --------------------------------------------------------------------
    // These functions CAN depend on the environment:
    //   - msg.sender might matter for access control
    //   - msg.value might be required for payable functions
    //   - block.timestamp for time-based logic
    //
    // When calling these, we must pass an `env` variable: increment(e, amount)
    // This lets us reason about different callers, timestamps, etc.
    
    function increment(uint256) external;
    function decrement(uint256) external;
    function reset() external;
    function setValue(uint256) external;
}

// ============================================================================
// INVARIANT
// ============================================================================
// An invariant is a property that must ALWAYS hold:
//   - After the constructor
//   - After every public/external function call
//   - For ALL possible inputs and states
//
// This is stronger than a rule - it's checked across ALL functions automatically.

invariant counterBounded()
    counter() <= MAX()      // The property: counter never exceeds MAX (100)
    {
        preserved {
            // The 'preserved' block is an inductive proof helper.
            // It says: "Assume the invariant holds BEFORE the function call,
            //           then prove it still holds AFTER."
            // 
            // This is how we prove invariants inductively:
            //   Base case: invariant holds after constructor (counter = 0 <= 100) ✓
            //   Inductive step: if counter <= MAX before, then counter <= MAX after ✓
            require counter() <= MAX();
        }
    }

// ============================================================================
// RULES
// ============================================================================
// Rules verify properties about SPECIFIC function behavior.
// Unlike invariants, rules are about what happens when you call a function.
//
// Structure:
//   1. Setup: establish preconditions, save "before" state
//   2. Action: call the function
//   3. Assert: check postconditions

// Rule 1: increment increases counter by the specified amount
rule incrementIncreasesCounter(uint256 amount) {
    // `env e` declares an environment variable.
    // It represents: msg.sender, msg.value, block.timestamp, etc.
    // Certora will try ALL possible environments symbolically.
    env e;
    
    // Save state BEFORE the function call
    // Since counter() is envfree, we call it directly (no env needed)
    uint256 counterBefore = counter();
    
    // Call the function
    // Since increment is NOT envfree, we pass the environment `e`
    // This lets Certora reason about all possible callers
    increment(e, amount);
    
    // Save state AFTER the function call
    uint256 counterAfter = counter();
    
    // Assert the postcondition
    // If increment didn't revert, counter should have increased by amount
    assert counterAfter == counterBefore + amount, 
           "Counter should increase by amount";
}

// Rule 2: reset sets counter to zero
rule resetSetsToZero() {
    env e;
    
    // No need to save "before" state - we only care about "after"
    reset(e);
    
    // After reset, counter must be 0
    assert counter() == 0, "Counter should be zero after reset";
}

// Rule 3: decrement decreases counter by the specified amount
rule decrementDecreasesCounter(uint256 amount) {
    env e;
    
    uint256 counterBefore = counter();
    
    decrement(e, amount);
    
    uint256 counterAfter = counter();
    
    // If decrement didn't revert (amount <= counter), this should hold
    assert counterAfter == counterBefore - amount, 
           "Counter should decrease by amount";
}

// ============================================================================
// WHAT CERTORA PROVES
// ============================================================================
// For each rule, Certora proves:
//   "For ALL possible inputs and states, IF the function doesn't revert,
//    THEN the assertion holds."
//
// This is different from testing:
//   - Testing: checks specific inputs (maybe 1000 cases)
//   - Certora: proves for ALL inputs (infinite cases, mathematically)
//
// If Certora finds a counterexample, it shows you:
//   - The exact input values that break the property
//   - The state before and after
//   - The full execution trace
// ============================================================================
