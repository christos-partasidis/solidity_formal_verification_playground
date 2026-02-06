/**
 * ============================================================================
 * CERTORA SPECIFICATION: TransparentProxyFixed (via Harness)
 * ============================================================================
 * 
 * Phase 4: Verifying the Fixed Transparent Proxy
 * 
 * We use a harness contract to expose internal state for verification.
 * This is a common pattern when verifying contracts with:
 * - Assembly storage access (EIP-1967 slots)
 * - Internal functions we want to verify
 * - Access-controlled view functions
 * 
 * WHAT WE'RE VERIFYING:
 * ---------------------
 * 1. Admin is never zero
 * 2. Implementation is never zero
 * 3. Only admin can upgrade
 * 4. Two-step admin transfer works correctly
 * 5. Zero-address checks work
 * 
 * NEW CVL CONCEPTS:
 * -----------------
 * - Using harness contracts for verification
 * - Verifying two-step processes
 * - requireInvariant composition
 * 
 * ============================================================================
 */

// =============================================================================
// METHODS BLOCK
// =============================================================================

methods {
    // Harness view functions (unrestricted access for verification)
    function getAdmin() external returns (address) envfree;
    function getImplementation() external returns (address) envfree;
    function getPendingAdmin() external returns (address) envfree;
    
    // Original admin-only view functions (will revert for non-admin)
    function admin() external returns (address);
    function implementation() external returns (address);
    function pendingAdmin() external returns (address);
    
    // Admin functions
    function upgradeTo(address) external;
    function transferAdmin(address) external;
    function acceptAdmin() external;
    function cancelAdminTransfer() external;
}

// =============================================================================
// STATE PROPERTIES (as rules, not invariants)
// =============================================================================

/**
 * Instead of invariants (which require constructor verification),
 * we verify that no function can SET admin or implementation to zero.
 * This proves the properties hold if they held initially.
 */

/**
 * RULE: noFunctionSetsAdminToZero
 * -------------------------------
 * No function can set the admin to zero address.
 * 
 * Combined with knowing the constructor sets admin to msg.sender (non-zero),
 * this proves admin is never zero throughout the contract's lifetime.
 */
rule noFunctionSetsAdminToZero(method f) filtered {
    f -> !f.isFallback
} {
    env e;
    calldataarg args;
    
    address adminBefore = getAdmin();
    require adminBefore != 0;  // Assume it wasn't zero before
    require e.msg.sender != 0;
    
    f@withrevert(e, args);
    
    // After any function, admin should still be non-zero
    assert getAdmin() != 0,
        "No function should set admin to zero";
}

/**
 * RULE: noFunctionSetsImplementationToZero
 * ----------------------------------------
 * No function can set the implementation to zero address.
 */
rule noFunctionSetsImplementationToZero(method f) filtered {
    f -> !f.isFallback
} {
    env e;
    calldataarg args;
    
    address implBefore = getImplementation();
    require implBefore != 0;  // Assume it wasn't zero before
    require e.msg.sender != 0;
    
    f@withrevert(e, args);
    
    // After any function, implementation should still be non-zero
    assert getImplementation() != 0,
        "No function should set implementation to zero";
}

// =============================================================================
// ACCESS CONTROL RULES
// =============================================================================

/**
 * RULE: onlyAdminCanUpgrade
 * -------------------------
 * If msg.sender is not the admin, upgradeTo() must revert.
 */
rule onlyAdminCanUpgrade(address newImpl) {
    env e;
    
    address currentAdmin = getAdmin();
    
    upgradeTo@withrevert(e, newImpl);
    
    assert e.msg.sender != currentAdmin => lastReverted,
        "upgradeTo should revert when called by non-admin";
}

/**
 * RULE: adminCanUpgrade
 * ---------------------
 * Admin can successfully upgrade to a valid implementation.
 */
rule adminCanUpgrade(address newImpl) {
    env e;
    
    require e.msg.sender == getAdmin();
    require e.msg.value == 0;
    require newImpl != 0;
    // Note: We can't easily check code.length in CVL, so we assume valid contract
    
    upgradeTo@withrevert(e, newImpl);
    
    // If it succeeded, implementation should be updated
    assert !lastReverted => getImplementation() == newImpl,
        "After successful upgrade, implementation should be newImpl";
}

/**
 * RULE: onlyAdminCanTransferAdmin
 * -------------------------------
 * Only admin can initiate admin transfer.
 */
rule onlyAdminCanTransferAdmin(address newAdmin) {
    env e;
    
    address currentAdmin = getAdmin();
    
    transferAdmin@withrevert(e, newAdmin);
    
    assert e.msg.sender != currentAdmin => lastReverted,
        "transferAdmin should revert when called by non-admin";
}

/**
 * RULE: acceptAdminRevertsIfNoPending
 * -----------------------------------
 * If there's no pending admin, acceptAdmin() must revert.
 * 
 * Note: We require msg.sender != 0 because in practice no caller has address 0.
 * The edge case where pending=0 and sender=0 wouldn't revert, but that's
 * not a realistic scenario.
 */
rule acceptAdminRevertsIfNoPending() {
    env e;
    
    require getPendingAdmin() == 0;
    require e.msg.sender != 0;  // Real callers are never address(0)
    
    acceptAdmin@withrevert(e);
    
    assert lastReverted,
        "acceptAdmin should revert when no pending admin";
}

/**
 * RULE: acceptAdminRevertsIfWrongCaller
 * -------------------------------------
 * If caller is not the pending admin, acceptAdmin() must revert.
 */
rule acceptAdminRevertsIfWrongCaller() {
    env e;
    
    address pending = getPendingAdmin();
    require pending != 0;
    require e.msg.sender != pending;
    
    acceptAdmin@withrevert(e);
    
    assert lastReverted,
        "acceptAdmin should revert when caller is not pending admin";
}

// =============================================================================
// UPGRADE INTEGRITY RULES
// =============================================================================

/**
 * RULE: upgradeChangesImplementation
 * ----------------------------------
 * After successful upgradeTo(newImpl), implementation equals newImpl.
 */
rule upgradeChangesImplementation(address newImpl) {
    env e;
    
    upgradeTo(e, newImpl);
    
    assert getImplementation() == newImpl,
        "After upgradeTo, implementation should be newImpl";
}

/**
 * RULE: upgradePreservesAdmin
 * ---------------------------
 * upgradeTo() should never change the admin.
 */
rule upgradePreservesAdmin(address newImpl) {
    env e;
    
    address adminBefore = getAdmin();
    
    upgradeTo(e, newImpl);
    
    assert getAdmin() == adminBefore,
        "upgradeTo should not change admin";
}

/**
 * RULE: upgradePreservesPendingAdmin
 * ----------------------------------
 * upgradeTo() should never change the pending admin.
 */
rule upgradePreservesPendingAdmin(address newImpl) {
    env e;
    
    address pendingBefore = getPendingAdmin();
    
    upgradeTo(e, newImpl);
    
    assert getPendingAdmin() == pendingBefore,
        "upgradeTo should not change pending admin";
}

/**
 * RULE: upgradeRejectsZeroAddress
 * -------------------------------
 * upgradeTo(address(0)) must always revert.
 */
rule upgradeRejectsZeroAddress() {
    env e;
    require e.msg.sender == getAdmin();
    require e.msg.value == 0;
    
    upgradeTo@withrevert(e, 0);
    
    assert lastReverted,
        "upgradeTo(0) should always revert";
}

// =============================================================================
// TWO-STEP ADMIN TRANSFER RULES
// =============================================================================

/**
 * RULE: transferAdminSetsPending
 * ------------------------------
 * transferAdmin(x) should set pendingAdmin to x.
 */
rule transferAdminSetsPending(address newAdmin) {
    env e;
    require e.msg.sender == getAdmin();
    require e.msg.value == 0;
    require newAdmin != 0;
    
    transferAdmin(e, newAdmin);
    
    assert getPendingAdmin() == newAdmin,
        "transferAdmin should set pending admin";
}

/**
 * RULE: transferAdminPreservesAdmin
 * ---------------------------------
 * transferAdmin() should NOT change the current admin (only pending).
 */
rule transferAdminPreservesAdmin(address newAdmin) {
    env e;
    
    address adminBefore = getAdmin();
    
    transferAdmin(e, newAdmin);
    
    assert getAdmin() == adminBefore,
        "transferAdmin should not change current admin";
}

/**
 * RULE: transferAdminPreservesImplementation
 * ------------------------------------------
 * transferAdmin() should never change implementation.
 */
rule transferAdminPreservesImplementation(address newAdmin) {
    env e;
    
    address implBefore = getImplementation();
    
    transferAdmin(e, newAdmin);
    
    assert getImplementation() == implBefore,
        "transferAdmin should not change implementation";
}

/**
 * RULE: acceptAdminCompletesTwoStep
 * ---------------------------------
 * After acceptAdmin(), the pending admin becomes the actual admin.
 */
rule acceptAdminCompletesTwoStep() {
    env e;
    
    address pending = getPendingAdmin();
    require pending != 0;
    require e.msg.sender == pending;
    require e.msg.value == 0;
    
    acceptAdmin(e);
    
    assert getAdmin() == pending,
        "After acceptAdmin, pending should become admin";
    assert getPendingAdmin() == 0,
        "After acceptAdmin, pending should be cleared";
}

/**
 * RULE: acceptAdminPreservesImplementation
 * ----------------------------------------
 * Accepting admin should never change implementation.
 */
rule acceptAdminPreservesImplementation() {
    env e;
    
    address implBefore = getImplementation();
    
    acceptAdmin(e);
    
    assert getImplementation() == implBefore,
        "acceptAdmin should not change implementation";
}

/**
 * RULE: cancelTransferClearsPending
 * ---------------------------------
 * cancelAdminTransfer() should clear the pending admin.
 */
rule cancelTransferClearsPending() {
    env e;
    require e.msg.sender == getAdmin();
    require e.msg.value == 0;
    
    cancelAdminTransfer(e);
    
    assert getPendingAdmin() == 0,
        "cancelAdminTransfer should clear pending admin";
}

// =============================================================================
// PARAMETRIC RULES
// =============================================================================

/**
 * RULE: onlyUpgradeChangesImplementation
 * --------------------------------------
 * Only upgradeTo() can change the implementation.
 */
rule onlyUpgradeChangesImplementation(method f) filtered {
    f -> f.selector != sig:upgradeTo(address).selector
      && !f.isFallback
} {
    env e;
    calldataarg args;
    
    address implBefore = getImplementation();
    
    f@withrevert(e, args);
    
    assert getImplementation() == implBefore,
        "Only upgradeTo should change implementation";
}

/**
 * RULE: onlyAcceptAdminChangesAdmin
 * ---------------------------------
 * Only acceptAdmin() can change the admin.
 */
rule onlyAcceptAdminChangesAdmin(method f) filtered {
    f -> f.selector != sig:acceptAdmin().selector
      && !f.isFallback
} {
    env e;
    calldataarg args;
    
    address adminBefore = getAdmin();
    
    f@withrevert(e, args);
    
    assert getAdmin() == adminBefore,
        "Only acceptAdmin should change admin";
}

/**
 * RULE: onlyTransferAndCancelChangePending
 * ----------------------------------------
 * Only transferAdmin() and cancelAdminTransfer() can change pending admin.
 * (acceptAdmin also clears it, but that's covered separately)
 */
rule onlyTransferChangePending(method f) filtered {
    f -> f.selector != sig:transferAdmin(address).selector
      && f.selector != sig:cancelAdminTransfer().selector
      && f.selector != sig:acceptAdmin().selector
      && !f.isFallback
} {
    env e;
    calldataarg args;
    
    address pendingBefore = getPendingAdmin();
    
    f@withrevert(e, args);
    
    assert getPendingAdmin() == pendingBefore,
        "Only transferAdmin/cancelAdminTransfer/acceptAdmin should change pending";
}

// =============================================================================
// FULL TWO-STEP TRANSFER SCENARIO
// =============================================================================

/**
 * RULE: fullTwoStepTransferWorks
 * ------------------------------
 * Verify the complete two-step admin transfer process.
 * 
 * This is an end-to-end test:
 * 1. Current admin calls transferAdmin(newAdmin)
 * 2. newAdmin calls acceptAdmin()
 * 3. newAdmin is now the admin
 */
rule fullTwoStepTransferWorks(address newAdmin) {
    env e1;  // For transferAdmin
    env e2;  // For acceptAdmin
    
    address originalAdmin = getAdmin();
    
    // Preconditions
    require e1.msg.sender == originalAdmin;
    require e1.msg.value == 0;
    require newAdmin != 0;
    require newAdmin != originalAdmin;  // Different admin
    require e2.msg.sender == newAdmin;
    require e2.msg.value == 0;
    
    // Step 1: Current admin proposes new admin
    transferAdmin(e1, newAdmin);
    
    // Verify pending is set
    assert getPendingAdmin() == newAdmin;
    assert getAdmin() == originalAdmin;  // Admin unchanged yet
    
    // Step 2: New admin accepts
    acceptAdmin(e2);
    
    // Verify transfer complete
    assert getAdmin() == newAdmin,
        "After two-step transfer, new admin should be active";
    assert getPendingAdmin() == 0,
        "After two-step transfer, pending should be cleared";
}
