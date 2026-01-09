// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TransparentProxy {
    address public admin;
    address public implementation;

    constructor(address _impl) {
        admin = msg.sender;
        implementation = _impl;
    }

    function upgradeTo(address newImpl) external {
        require(msg.sender == admin, "not admin");
        implementation = newImpl;
    }

    fallback() external payable {
        address impl = implementation;
        require(impl != address(0));

        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())

            if eq(result, 0) { revert(0, returndatasize()) }
            return(0, returndatasize())
        }
    }
}