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
            calldatacopy(0, 0, calldatasize()) // copy calldata to memory, start at offset 0, start copying from beginning, copy calldatasize bytes
            // memory [0 .. calldatasize())contains the exact bytes the caller sent

            // gas(): forward all remaining gas to the call
            // impl: address whose code is executed
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())

            if eq(result, 0) { revert(0, returndatasize()) }
            return(0, returndatasize())
        }
    }
}