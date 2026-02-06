// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./TransparentProxyFixed.sol";

/**
 * ============================================================================
 * TransparentProxyFixedHarness - Testing Harness for Certora
 * ============================================================================
 * 
 * This harness exposes internal state for formal verification.
 * It adds public getters that Certora can call without reverting.
 * 
 * NOTE: This is ONLY for verification. In production, use TransparentProxyFixed.
 * ============================================================================
 */
contract TransparentProxyFixedHarness is TransparentProxyFixed {
    
    constructor(address _impl) TransparentProxyFixed(_impl) {}
    
    /**
     * @notice Get admin without access control (for verification only)
     */
    function getAdmin() external view returns (address) {
        return _getAdmin();
    }
    
    /**
     * @notice Get implementation without access control (for verification only)
     */
    function getImplementation() external view returns (address) {
        return _getImplementation();
    }
    
    /**
     * @notice Get pending admin without access control (for verification only)
     */
    function getPendingAdmin() external view returns (address) {
        return _getPendingAdmin();
    }
}
