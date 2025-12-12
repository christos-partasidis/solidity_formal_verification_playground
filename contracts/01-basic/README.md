# Phase 1: SMTChecker Fundamentals

This directory contains progressive exercises for learning formal verification using the **Solidity SMTChecker**.

## Learning Path

Each exercise builds on the previous one. Work through them in order.

---

## Exercise 1: Basic Assertions

**Files:** `01_AlwaysFalse.sol`, `01_AlwaysFalseFixed.sol`

**Concept:** Understanding how SMTChecker discovers counterexamples.

**Key Learning:**
- `assert()` statements are logical formulas the SMTChecker tries to prove
- When unprovable, SMTChecker provides a concrete counterexample
- `assert(x > x + 1)` is always false → counterexample: any value of `x`

**Commands:**
```bash
solc --model-checker-engine chc 01_AlwaysFalse.sol
solc --model-checker-engine chc 01_AlwaysFalseFixed.sol
```

**Expected Output:**
- `01_AlwaysFalse.sol`: Assertion violation with counterexample
- `01_AlwaysFalseFixed.sol`: All assertions hold

---

## Exercise 2: Unreachable States

**File:** `02_TestSmack.sol`

**Concept:** Assertions in unreachable code are vacuously true.

**Key Learning:**
- If code can't execute (due to `require`, overflow, or revert), assertions are ignored
- Understanding execution path feasibility
- Difference between "proof" and "no counterexample due to unreachability"

---

## Exercise 3: State Invariants (Violation Detection)

**Files:** `03_InvariantFail.sol`, `03_InvariantFixed.sol`

**Concept:** Proving properties that must hold for state variables.

**Key Learning:**
- State invariants are properties that should always be true
- SMTChecker explores all possible inputs to find violations
- `03_InvariantFail.sol`: `balance <= 1000` not enforced → counterexample found
- `03_InvariantFixed.sol`: Precondition `require(x <= 1000)` ensures invariant

**Verification Goal:**
```
∀ inputs: preconditions ⇒ invariant holds
```

---

## Exercise 4: Domain Restriction

**Files:** `04_RangeBox.sol`, `04_SimpleBox.sol`, `04_SumBox.sol`

**Concept:** Using `require()` to restrict input domains and prove invariants.

**Key Learning:**
- `require()` = precondition = domain restriction
- Narrows the space the SMTChecker must explore
- Makes proofs tractable and invariants provable
- Defensive programming ≡ formal preconditions

---

## Exercise 5: State-Transition Invariants (Latest)

**Files:** `05_BoundedCounter.sol`, `05_BoundedCounterFixed.sol`

**Concept:** Proving invariants hold across **all** state-changing functions.

**Key Learning:**
- **Contract invariant**: Property that holds after every transaction
- Multi-function reasoning: SMTChecker verifies all execution paths
- `05_BoundedCounter.sol`: Invariant `counter <= MAX` violated by `increment(101)`
- `05_BoundedCounterFixed.sol`: Preconditions in all functions preserve invariant

**Formal Statement:**
```
∀ functions f, ∀ valid inputs: 
  Invariant_before ∧ Precondition_f ⇒ Invariant_after
```

**Commands:**
```bash
# See counterexample
solc --model-checker-engine chc 05_BoundedCounter.sol

# Verify proof
solc --model-checker-engine chc 05_BoundedCounterFixed.sol
```

**What to Observe:**
1. In `05_BoundedCounter.sol`: Counterexample showing `increment(101)` breaks invariant
2. In `05_BoundedCounterFixed.sol`: All assertions hold because preconditions enforce bounds
3. How `require()` statements act as formal preconditions
4. Multi-function invariant reasoning

**Why This Matters:**
- Foundation for proxy upgrade verification (preserving invariants across implementations)
- Essential for DeFi protocols (e.g., total supply invariants)
- Core technique for CBDC correctness (balance constraints, authorization invariants)

---

## Exercise 6: Invariants Over Mappings and Arrays ⭐ (Latest)

**Files:** 
- `06_TokenBalance.sol`, `06_TokenBalanceFixed.sol` (mapping invariants)
- `06_ArraySum.sol`, `06_ArraySumFixed.sol` (array invariants)

**Concept:** Proving properties about collections and aggregate values.

**Key Learning:**

### Mapping Invariants
- SMTChecker **CAN** reason about individual mapping entries:
  - `balances[address] <= totalSupply` ✓
  - Local properties about specific keys ✓
  
- SMTChecker **CANNOT** verify quantified invariants:
  - `∀ address: balances[address] <= MAX` ✗
  - `Σ balances[i] == totalSupply` ✗
  - Cross-account relationships without explicit tracking ✗

### Array Invariants
- SMTChecker tracks bounded array contents symbolically
- Can verify element-wise properties for small arrays
- Cannot verify loop invariants or sum properties automatically
- **Design pattern**: Maintain explicit aggregates (sum, count) as state variables

### Critical Design Pattern
```solidity
// ❌ Unverifiable with SMTChecker
assert(sum(balances) == totalSupply);

// ✅ Verifiable with SMTChecker
// Track totalSupply explicitly
// Update atomically with balance changes
// SMTChecker verifies update consistency
```

**Commands:**
```bash
# Mapping invariants
solc --model-checker-engine chc 06_TokenBalance.sol        # See violation
solc --model-checker-engine chc 06_TokenBalanceFixed.sol   # Verify proof

# Array invariants
solc --model-checker-engine chc 06_ArraySum.sol            # See bug in update()
solc --model-checker-engine chc 06_ArraySumFixed.sol       # Verify correctness
```

**What to Observe:**
1. `06_TokenBalance.sol`: Counterexample where `mint(1000001)` exceeds `MAX_SUPPLY`
2. `06_TokenBalanceFixed.sol`: Preconditions prevent all violations
3. `06_ArraySum.sol`: Bug where `update()` doesn't adjust `sum`
4. `06_ArraySumFixed.sol`: Correct atomic updates maintain consistency

**Why This Matters:**
- **ERC20 tokens**: Total supply invariant is critical
- **DeFi protocols**: Reserve tracking must be accurate
- **CBDCs**: Circulation limits must be enforced
- **Upgradeable systems**: Storage invariants across versions

**Limitations Discovered:**
- For true sum invariants (`Σ balances == total`), need **Certora Prover**
- For quantified properties (`∀ x`), need **Certora's ghost variables**
- This motivates Phase 4 of the roadmap!

---

## Next Steps

✅ **Completed:** Basic assertions, state invariants, transition invariants, mappings/arrays  
🎯 **Next:** Arithmetic boundary proofs  
📍 **Then:** Move to Phase 2 (Hoare Logic with solc-verify)

---

## Tips for Learning

1. **Always read the counterexample** - it shows exactly when/how a property fails
2. **Start with failing tests** - understanding failures teaches more than successes
3. **Think in logic** - `require()` = precondition, `assert()` = postcondition/invariant
4. **Build incrementally** - each exercise adds one concept

## SMTChecker Quick Reference

```bash
# Basic verification
solc --model-checker-engine chc <file.sol>

# With specific contracts
solc --model-checker-engine chc --model-checker-contracts <ContractName> <file.sol>

# Verbose output
solc --model-checker-engine chc --model-checker-show-unproved <file.sol>
```

**Engines:**
- `chc` (default): Constrained Horn Clauses - best for most cases
- `bmc`: Bounded Model Checking - for specific depth exploration

---

**Remember:** Formal verification is a **dialogue** with the solver. The counterexamples guide you toward correct specifications.
