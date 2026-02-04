/**
 * ============================================================================
 * CERTORA SPECIFICATION: TransparentProxy
 * ============================================================================
 * 
 * Phase 3: Transparent Proxy Verification
 * 
 * The Transparent Proxy pattern is foundational in upgradeable smart contracts.
 * It allows contracts to be upgraded while preserving state and address.
 * 
 * WHAT WE'RE VERIFYING:
 * ---------------------
 * 1. Access Control: Only admin can call upgradeTo()
 * 2. Upgrade Correctness: upgradeTo() actually changes implementation
 * 3. Admin Integrity: Admin is preserved during upgrades
 * 
 * ============================================================================
 * IMPORTANT DISCOVERY: THE FALLBACK VULNERABILITY
 * ============================================================================
 * 
 * The fallback() function does a delegatecall to the implementation.
 * This means the implementation could theoretically modify ANY storage slot,
 * including admin and implementation addresses!
 * 
 * This is a REAL vulnerability in simplified proxy contracts!
 * 
 * Production proxies (like OpenZeppelin's TransparentUpgradeableProxy) solve this by:
 * 1. Storing admin/impl in special EIP-1967 storage slots
 * 2. Using pseudo-random slot positions that implementations won't collide with
 * 
 * In this spec, we EXCLUDE the fallback from verification because:
 * - Its behavior depends entirely on the implementation contract
 * - We're verifying the proxy logic itself, not arbitrary implementations
 * - This is a teaching moment about proxy security!
 * 
 * KEY CONCEPTS DEMONSTRATED:
 * --------------------------
 * - Access control verification with @withrevert and lastReverted
 * - Parametric rules with method filtering
 * - f.isFallback for excluding fallback functions
 * - Understanding proxy security limitations
 * 
 * ============================================================================
 */

// =============================================================================
// METHODS BLOCK
// =============================================================================

methods {
    // View functions - don't need msg.sender, marked envfree
    function admin() external returns (address) envfree;
    function implementation() external returns (address) envfree;
    
    // State-changing function - needs env (for msg.sender check)
    function upgradeTo(address) external;
}

// =============================================================================
// ACCESS CONTROL RULES
// =============================================================================

/**
 * RULE: onlyAdminCanUpgrade
 * -------------------------
 * If msg.sender is not the admin, upgradeTo() must revert.
 * 
 * This is the core security property of the proxy pattern.
 * 
 * CVL Concept: @withrevert and lastReverted
 * - upgradeTo@withrevert means "call but don't fail if it reverts"
 * - lastReverted is true if the previous call reverted
 */
rule onlyAdminCanUpgrade(address newImpl) {
    env e;
    
    // Get current admin
    address currentAdmin = admin();
    
    // Call upgradeTo, allowing it to revert
    upgradeTo@withrevert(e, newImpl);
    
    // If caller is NOT admin, it MUST have reverted
    assert e.msg.sender != currentAdmin => lastReverted,
        "upgradeTo should revert when called by non-admin";
}

/**
 * RULE: adminCanUpgrade
 * ---------------------
 * If msg.sender IS the admin and provides valid input, upgradeTo() succeeds.
 * 
 * This is the "positive" counterpart to onlyAdminCanUpgrade.
 * We verify that admin access actually works.
 * 
 * Note: We require msg.value == 0 because upgradeTo is not payable.
 */
rule adminCanUpgrade(address newImpl) {
    env e;
    
    // Preconditions for success
    require e.msg.sender == admin();  // Caller is admin
    require e.msg.value == 0;          // upgradeTo is not payable
    
    // Call upgradeTo
    upgradeTo@withrevert(e, newImpl);
    
    // Should succeed (not revert)
    assert !lastReverted,
        "upgradeTo should succeed when called by admin";
}

// =============================================================================
// STATE TRANSITION RULES
// =============================================================================

/**
 * RULE: upgradeChangesImplementation
 * ----------------------------------
 * After a successful upgradeTo(newImpl), implementation() returns newImpl.
 * 
 * This verifies the upgrade actually does what it's supposed to do.
 */
rule upgradeChangesImplementation(address newImpl) {
    env e;
    
    // Successful upgrade
    upgradeTo(e, newImpl);
    
    // Implementation should now be newImpl
    assert implementation() == newImpl,
        "After upgradeTo, implementation should be the new address";
}

/**
 * RULE: upgradePreservesAdmin
 * ---------------------------
 * The upgradeTo function should never change the admin.
 * 
 * This prevents a malicious upgrade that could steal admin rights.
 */
rule upgradePreservesAdmin(address newImpl) {
    env e;
    
    // Capture admin before
    address adminBefore = admin();
    
    // Perform upgrade
    upgradeTo(e, newImpl);
    
    // Admin should be unchanged
    assert admin() == adminBefore,
        "upgradeTo should not change the admin";
}

// =============================================================================
// PARAMETRIC RULES (excluding fallback)
// =============================================================================

/**
 * RULE: adminNeverChangesExceptFallback
 * -------------------------------------
 * No function in this contract (except fallback) can change the admin.
 * 
 * CVL Concept: f.isFallback
 * - Filters out the fallback function from parametric rules
 * - Essential for proxy contracts where fallback has unpredictable behavior
 * 
 * Why exclude fallback?
 * - Fallback does delegatecall to implementation
 * - Implementation could write to ANY storage slot
 * - This is a known limitation of this simple proxy design
 */
rule adminNeverChangesExceptFallback(method f) filtered {
    f -> !f.isFallback
} {
    env e;
    calldataarg args;
    
    // Capture admin before
    address adminBefore = admin();
    
    // Call any non-fallback function
    f(e, args);
    
    // Admin should be unchanged
    assert admin() == adminBefore,
        "No non-fallback function should change the admin";
}

/**
 * RULE: onlyUpgradeChangesImplementation
 * --------------------------------------
 * Only upgradeTo() can change the implementation address (excluding fallback).
 * 
 * This ensures there's no hidden way to change implementation
 * through the proxy's own functions.
 */
rule onlyUpgradeChangesImplementation(method f) filtered {
    // Exclude upgradeTo (it's supposed to change implementation)
    // Exclude fallback (delegatecall can do anything)
    f -> f.selector != sig:upgradeTo(address).selector && !f.isFallback
} {
    env e;
    calldataarg args;
    
    // Capture implementation before
    address implBefore = implementation();
    
    // Call any function except upgradeTo and fallback
    f(e, args);
    
    // Implementation should be unchanged
    assert implementation() == implBefore,
        "Only upgradeTo should change implementation";
}

/**
 * RULE: viewFunctionsAreReadOnly
 * ------------------------------
 * The admin() and implementation() view functions don't change state.
 * 
 * This is mostly for demonstration - view functions shouldn't modify state,
 * but it's good to verify explicitly.
 */
rule viewFunctionsAreReadOnly() {
    // Capture state before
    address adminBefore = admin();
    address implBefore = implementation();
    
    // Call view functions
    address a = admin();
    address i = implementation();
    
    // State should be unchanged
    assert admin() == adminBefore,
        "admin() should not change admin";
    assert implementation() == implBefore,
        "implementation() should not change implementation";
}

// =============================================================================
// DOCUMENTATION: VULNERABILITIES DISCOVERED
// =============================================================================

/**
 * VULNERABILITIES IN THIS SIMPLIFIED PROXY:
 * =========================================
 * 
 * 1. FALLBACK CAN MODIFY PROXY STATE
 *    --------------------------------
 *    The fallback() does delegatecall to implementation.
 *    A malicious implementation could:
 *    - Overwrite `admin` storage slot (slot 0)
 *    - Overwrite `implementation` storage slot (slot 1)
 *    - Take over the proxy completely!
 *    
 *    FIX: Use EIP-1967 storage slots:
 *    - Admin slot: keccak256("eip1967.proxy.admin") - 1
 *    - Impl slot:  keccak256("eip1967.proxy.implementation") - 1
 * 
 * 2. NO ZERO-ADDRESS CHECK IN upgradeTo()
 *    ------------------------------------
 *    The contract allows setting implementation to address(0).
 *    This would brick the proxy (fallback would revert).
 *    
 *    FIX: Add `require(newImpl != address(0))` in upgradeTo()
 * 
 * 3. NO ADMIN TRANSFER MECHANISM
 *    ---------------------------
 *    Admin is set once in constructor and cannot be changed.
 *    If admin key is lost, the contract can never be upgraded again.
 *    
 *    FIX: Add two-step admin transfer (propose + accept)
 * 
 * 4. NO IMPLEMENTATION VALIDATION
 *    ----------------------------
 *    upgradeTo() doesn't check if newImpl is a valid contract.
 *    
 *    FIX: Add `require(newImpl.code.length > 0)`
 * 
 * 5. SELECTOR CLASHING (potential)
 *    -----------------------------
 *    If implementation has admin() or upgradeTo() functions,
 *    there could be selector conflicts.
 *    
 *    FIX: OpenZeppelin's TransparentProxy routes calls differently
 *    based on whether msg.sender is admin.
 */
