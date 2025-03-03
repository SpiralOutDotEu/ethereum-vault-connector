import "../utils/IsMustRevertFunction.spec";

/**
 * Check that we don't leak write access to storage to other code.
 */
import "../utils/CallOpSanity.spec";

////////////////////////////////////////////////////////////////
//                                                            //
//           Account Controllers (Ghost and Hooks)            //
//                                                            //
////////////////////////////////////////////////////////////////

/* Any load from `firstElement` or `elements`, for either `accountControllers`
 * or `vaultStatusChecks`, MUST be dominated by a store on the same memory first.
 * Thus, requiring `value != currentContract` is safe as we assert it before.
 * We do this to keep the knowledge about `currentContract` not being in any of
 * these sets across HAVOC'd function calls.
 */
// when writing to accountControllers, check that value != currentContract
hook Sstore EthereumVaultConnectorHarness.accountControllers[KEY address user].firstElement address value STORAGE {
    assert(value != currentContract);
}
hook Sstore EthereumVaultConnectorHarness.accountControllers[KEY address user].elements[INDEX uint256 i].value address value STORAGE {
    assert(value != currentContract);
}
// when loading from accountControllers, we know that value != currentContract
hook Sload address value EthereumVaultConnectorHarness.accountControllers[KEY address user].firstElement STORAGE {
    require(value != currentContract);
}
hook Sload address value EthereumVaultConnectorHarness.accountControllers[KEY address user].elements[INDEX uint256 i].value STORAGE {
    require(value != currentContract);
}

////////////////////////////////////////////////////////////////
//                                                            //
//           Vault Status Checks (Ghost and Hooks)            //
//                                                            //
////////////////////////////////////////////////////////////////

// when writing to vaultStatusChecks, check that value != currentContract
hook Sstore EthereumVaultConnectorHarness.vaultStatusChecks.firstElement address value STORAGE {
    assert(value != currentContract);
}
hook Sstore EthereumVaultConnectorHarness.vaultStatusChecks.elements[INDEX uint256 i].value address value STORAGE {
    assert(value != currentContract);
}
// when loading from vaultStatusChecks, we know that value != currentContract
hook Sload address value EthereumVaultConnectorHarness.vaultStatusChecks.firstElement STORAGE {
    require(value != currentContract);
}
hook Sload address value EthereumVaultConnectorHarness.vaultStatusChecks.elements[INDEX uint256 i].value STORAGE {
    require(value != currentContract);
}

////////////////////////////////////////////////////////////////
//                                                            //
//                Ghost and Hook for Property                 //
//  EVC can only be msg.sender during the permit() function   //
//                                                            //
////////////////////////////////////////////////////////////////

/**
 * Core property: we never `call` into ourselves (except for `permit`, which we
 * exclude in the rule below). All other possibilities to be called either have
 * `msg.sender != currentContract` (reentrant `call` or `staticcall` or internal
 * `delegatecall`), or have no write access to our storage (reentrant
 * `delegatecall`).
 */
hook CALL(uint g, address addr, uint value, uint argsOffset, uint argsLength, uint retOffset, uint retLength) uint rc
{
    assert(executingContract != currentContract || addr != currentContract);
}

// This rule checks the property of interest "EVC can only be msg.sender during the self-call in the permit() function". Expected to fail on permit() function.
rule onlyEVCCanCallCriticalMethod(method f, env e, calldataarg args)
  filtered {f -> 
    !isMustRevertFunction(f) &&
    f.selector != sig:EthereumVaultConnectorHarness.permit(address,uint256,uint256,uint256,uint256,bytes,bytes).selector
  }{
    //Exclude EVC as being the initiator of the call.
    require(e.msg.sender != currentContract);

    f(e,args);

    assert(true);
}


