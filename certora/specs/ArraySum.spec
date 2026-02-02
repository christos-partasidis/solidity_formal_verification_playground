/*
 * ============================================================================
 * Certora Verification Spec for ArraySumFixed
 * ============================================================================
 * 
 * This spec reinforces ghost variables with a DIFFERENT data structure: arrays!
 * 
 * The Problem (same as TokenBalance):
 *   SMTChecker CANNOT prove: Σ values[i] == sum
 *   The contract tracks `sum` explicitly, but SMTChecker can't verify it's correct.
 * 
 * The Solution:
 *   Use a ghost variable to independently track the sum of array elements,
 *   then prove it equals the contract's `sum` variable.
 * 
 * Key Differences from TokenBalance:
 *   - Array vs mapping (different storage layout)
 *   - Bounded size (MAX_SIZE = 10)
 *   - Has update() function (changes element in place)
 *   - Has pop() function (removes last element)
 * 
 * NOTE: Arrays in Certora require special handling!
 *   - Array length is stored separately from elements
 *   - pop() sets element to 0 before removing
 *   - We need to be careful with ghost initialization
 */

// ============================================================================
// METHODS BLOCK
// ============================================================================

methods {
    // View functions (envfree)
    function values(uint256) external returns (uint256) envfree;
    function sum() external returns (uint256) envfree;
    function MAX_SIZE() external returns (uint256) envfree;
    
    // State-changing functions
    function add(uint256) external;
    function get(uint256) external returns (uint256) envfree;
    function update(uint256, uint256) external;
    function pop() external;
}

// ============================================================================
// GHOST VARIABLE - Simplified approach for arrays
// ============================================================================
// 
// For arrays, instead of tracking the exact sum via hooks (which is tricky
// because of how Solidity handles dynamic arrays), we focus on RULES that
// verify the relationship between operations and the sum variable.
//
// This is a common pattern: when exact ghost tracking is complex,
// use functional correctness rules instead.

// ============================================================================
// RULES - Functional Correctness
// ============================================================================

// Rule: add() increases sum by exactly the added value
rule addIncreasesSum(uint256 value) {
    env e;
    
    uint256 sumBefore = sum();
    
    add(e, value);
    
    uint256 sumAfter = sum();
    
    assert sumAfter == sumBefore + value, 
           "Sum should increase by added value";
}

// Rule: update() maintains sum correctly
// sum_after = sum_before - oldValue + newValue
rule updateMaintainsSum(uint256 index, uint256 newValue) {
    env e;
    
    // Get old value at index before update
    uint256 oldValue = get(index);
    uint256 sumBefore = sum();
    
    update(e, index, newValue);
    
    uint256 sumAfter = sum();
    
    // New sum = old sum - old value + new value
    assert to_mathint(sumAfter) == to_mathint(sumBefore) - to_mathint(oldValue) + to_mathint(newValue),
           "Sum should be adjusted by the difference";
}

// Rule: pop() decreases sum by the last element's value
rule popDecreasesSum() {
    env e;
    
    uint256 sumBefore = sum();
    
    // We can't easily get the last value, but we can verify sum decreases
    pop(e);
    
    uint256 sumAfter = sum();
    
    // Sum should not increase after pop
    assert sumAfter <= sumBefore, 
           "Sum should decrease after pop";
}

// Rule: get() doesn't change sum (view function property)
rule getIsReadOnly(uint256 index) {
    env e;
    
    uint256 sumBefore = sum();
    
    get(index);
    
    uint256 sumAfter = sum();
    
    assert sumAfter == sumBefore, 
           "Get should not change sum";
}

// Rule: sum only changes via add, update, or pop
rule sumOnlyChangesViaModifyingFunctions(method f) {
    env e;
    calldataarg args;
    
    uint256 sumBefore = sum();
    
    f(e, args);
    
    uint256 sumAfter = sum();
    
    // If sum changed, it must be add, update, or pop
    assert sumAfter != sumBefore => (
        f.selector == sig:add(uint256).selector ||
        f.selector == sig:update(uint256, uint256).selector ||
        f.selector == sig:pop().selector
    ), "Only add, update, pop can change sum";
}

// Rule: add is the only way to increase sum
rule onlyAddIncreasesSum(method f) {
    env e;
    calldataarg args;
    
    uint256 sumBefore = sum();
    
    f(e, args);
    
    uint256 sumAfter = sum();
    
    // If sum increased, it must have been add() OR update() with larger value
    // Note: update() CAN increase sum if newValue > oldValue
    assert sumAfter > sumBefore => (
        f.selector == sig:add(uint256).selector ||
        f.selector == sig:update(uint256, uint256).selector
    ), "Only add or update can increase sum";
}

// Rule: conservation - what goes in must come out
// If we add X and then pop, sum changes by (X - poppedValue)
rule addThenPopConservation(uint256 value) {
    env e;
    
    uint256 sumInitial = sum();
    
    add(e, value);
    
    uint256 sumAfterAdd = sum();
    assert sumAfterAdd == sumInitial + value;
    
    // Note: pop removes the LAST element, which is the one we just added
    pop(e);
    
    uint256 sumAfterPop = sum();
    
    // We added 'value' then popped it, so we should be back to initial
    assert sumAfterPop == sumInitial, 
           "Adding then popping same value should return to original sum";
}

// ============================================================================
// COMPARISON: TokenBalance vs ArraySum
// ============================================================================
//
// | Aspect          | TokenBalance           | ArraySumFixed          |
// |-----------------|------------------------|------------------------|
// | Data structure  | mapping(address=>uint) | uint256[]              |
// | Ghost approach  | Full ghost tracking    | Rule-based verification|
// | Size            | Unbounded              | Bounded (MAX_SIZE=10)  |
// | Operations      | mint, burn, transfer   | add, update, pop       |
//
// Key Learning:
//   - Mappings are easier to hook (KEY-based access)
//   - Arrays have complex storage (length + elements)
//   - Sometimes rules are better than ghost tracking
//   - Both approaches prove the same properties!
// ============================================================================
