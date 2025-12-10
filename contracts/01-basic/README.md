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

## Exercise 5: State-Transition Invariants ⭐ (Latest)

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

## Next Steps

✅ **Completed:** Basic assertions, state invariants, transition invariants  
🎯 **Next:** Invariants over mappings and arrays  
📍 **Then:** Arithmetic boundary proofs

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
