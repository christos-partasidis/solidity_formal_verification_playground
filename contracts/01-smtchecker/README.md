# Phase 1: SMTChecker Fundamentals

This directory contains progressive exercises for learning formal verification using the **Solidity SMTChecker**.

## Directory Structure

```
01-smtchecker/
├── 01-assertions/       # Exercise 1: Basic assertion semantics
├── 02-unreachable/      # Exercise 2: Unreachable code paths
├── 03-invariants/       # Exercise 3: State invariants
├── 04-domain-restriction/ # Exercise 4: Using require() as preconditions
├── 05-transitions/      # Exercise 5: Multi-function state transitions
├── 06-collections/      # Exercise 6: Mappings and arrays
└── 07-arithmetic/       # Exercise 7: Arithmetic property proofs
```

## Learning Path

Each exercise builds on the previous one. Work through them in order.

---

## Exercise 1: Basic Assertions → `01-assertions/`

**Files:** `AlwaysFalse.sol`, `AlwaysFalseFixed.sol`

**Concept:** Understanding how SMTChecker discovers counterexamples.

**Key Learning:**
- `assert()` statements are logical formulas the SMTChecker tries to prove
- When unprovable, SMTChecker provides a concrete counterexample
- `assert(x > x + 1)` is always false → counterexample: any value of `x`

**Commands:**
```bash
solc --model-checker-engine chc 01-assertions/AlwaysFalse.sol
solc --model-checker-engine chc 01-assertions/AlwaysFalseFixed.sol
```

**Expected Output:**
- `AlwaysFalse.sol`: Assertion violation with counterexample
- `AlwaysFalseFixed.sol`: All assertions hold (unreachable due to revert)

---

## Exercise 2: Unreachable States → `02-unreachable/`

**File:** `TestSmack.sol`

**Concept:** Assertions in unreachable code are vacuously true.

**Key Learning:**
- If code can't execute (due to `require`, overflow, or revert), assertions are ignored
- Understanding execution path feasibility
- Difference between "proof" and "no counterexample due to unreachability"

**Commands:**
```bash
solc --model-checker-engine chc 02-unreachable/TestSmack.sol
```

---

## Exercise 3: State Invariants → `03-invariants/`

**Files:** `InvariantFail.sol`, `InvariantFixed.sol`

**Concept:** Proving properties that must hold for state variables.

**Key Learning:**
- State invariants are properties that should always be true
- SMTChecker explores all possible inputs to find violations
- `InvariantFail.sol`: `balance <= 1000` not enforced → counterexample found
- `InvariantFixed.sol`: Precondition `require(x <= 1000)` ensures invariant

**Verification Goal:**
```
∀ inputs: preconditions ⇒ invariant holds
```

**Commands:**
```bash
solc --model-checker-engine chc 03-invariants/InvariantFail.sol
solc --model-checker-engine chc 03-invariants/InvariantFixed.sol
```

---

## Exercise 4: Domain Restriction → `04-domain-restriction/`

**Files:** `RangeBox.sol`, `SimpleBox.sol`, `SumBox.sol`

**Concept:** Using `require()` to restrict input domains and prove invariants.

**Key Learning:**
- `require()` = precondition = domain restriction
- Narrows the space the SMTChecker must explore
- Makes proofs tractable and invariants provable
- Defensive programming ≡ formal preconditions

**Commands:**
```bash
solc --model-checker-engine chc 04-domain-restriction/RangeBox.sol
solc --model-checker-engine chc 04-domain-restriction/SimpleBox.sol
solc --model-checker-engine chc 04-domain-restriction/SumBox.sol
```

---

## Exercise 5: State-Transition Invariants → `05-transitions/`

**Files:** `BoundedCounter.sol`, `BoundedCounterFixed.sol`

**Concept:** Proving invariants hold across **all** state-changing functions.

**Key Learning:**
- **Contract invariant**: Property that holds after every transaction
- Multi-function reasoning: SMTChecker verifies all execution paths
- `BoundedCounter.sol`: Invariant `counter <= MAX` violated by `increment(101)`
- `BoundedCounterFixed.sol`: Preconditions in all functions preserve invariant

**Formal Statement:**
```
∀ functions f, ∀ valid inputs: 
  Invariant_before ∧ Precondition_f ⇒ Invariant_after
```

**Commands:**
```bash
solc --model-checker-engine chc 05-transitions/BoundedCounter.sol
solc --model-checker-engine chc 05-transitions/BoundedCounterFixed.sol
```

**Why This Matters:**
- Foundation for proxy upgrade verification (preserving invariants across implementations)
- Essential for DeFi protocols (e.g., total supply invariants)
- Core technique for CBDC correctness (balance constraints, authorization invariants)

---

## Exercise 6: Invariants Over Collections → `06-collections/`

**Files:** 
- `TokenBalance.sol`, `TokenBalanceFixed.sol` (mapping invariants)
- `ArraySum.sol`, `ArraySumFixed.sol` (array invariants)

**Concept:** Proving properties about collections and aggregate values.

**Key Learning:**

### Mapping Invariants
- SMTChecker **CAN** reason about individual mapping entries:
  - `balances[address] <= totalSupply` ✓
  - Local properties about specific keys ✓
  
- SMTChecker **CANNOT** verify quantified invariants:
  - `∀ address: balances[address] <= MAX` ✗
  - `Σ balances[i] == totalSupply` ✗

### Array Invariants
- SMTChecker tracks bounded array contents symbolically
- Can verify element-wise properties for small arrays
- Cannot verify loop invariants or sum properties automatically
- **Design pattern**: Maintain explicit aggregates (sum, count) as state variables

**Critical Design Pattern:**
```solidity
// ❌ Unverifiable with SMTChecker
assert(sum(balances) == totalSupply);

// ✅ Verifiable with SMTChecker
// Track totalSupply explicitly, update atomically
```

**Commands:**
```bash
solc --model-checker-engine chc 06-collections/TokenBalance.sol
solc --model-checker-engine chc 06-collections/TokenBalanceFixed.sol
solc --model-checker-engine chc 06-collections/ArraySum.sol
solc --model-checker-engine chc 06-collections/ArraySumFixed.sol
```

**Limitations Discovered:**
- For true sum invariants (`Σ balances == total`), need **Certora Prover**
- For quantified properties (`∀ x`), need **Certora's ghost variables**
- This motivates Phase 2!

---

## Exercise 7: Arithmetic Properties → `07-arithmetic/`

**Files:** `SafePercentage.sol`, `SafePercentageFixed.sol`

**Concept:** Proving arithmetic correctness for financial calculations.

**Key Learning:**
- SMTChecker excels at arithmetic property verification
- Percentage calculations need explicit bounds (`bps <= 10000`)
- Division rounding has verifiable invariants
- Overflow prevention enables proofs (not just runtime safety)

**Verification Patterns:**
1. **Percentage bounds**: `bps <= 10000` ensures `result <= value`
2. **Overflow prevention**: `value <= MAX / multiplier` before multiplication
3. **Rounding properties**: `roundDown * divisor <= dividend`
4. **Distribution invariants**: `share1 + share2 + remainder == total`

**Commands:**
```bash
solc --model-checker-engine chc 07-arithmetic/SafePercentage.sol
solc --model-checker-engine chc 07-arithmetic/SafePercentageFixed.sol
```

**Why This Matters for DeFi/CBDC:**
- Interest calculations must be provably correct
- Fee distributions must not lose or create value
- Rounding must be predictable and fair

---

## Summary: What SMTChecker Can and Cannot Prove

### ✅ SMTChecker CAN Prove:
- Assertion reachability and violation
- State invariants with proper preconditions
- Multi-function invariant preservation
- Individual mapping/array entry properties
- Arithmetic bounds and relationships
- Overflow/underflow absence (implicit in 0.8+)

### ❌ SMTChecker CANNOT Prove:
- Quantified invariants (`∀ x: P(x)`)
- Sum invariants over collections (`Σ values == total`)
- Loop invariants (automatically)
- Cross-contract properties
- Temporal properties

### 🎯 Next: Certora Prover
Phase 2 introduces Certora for:
- Ghost variables (track hidden state)
- Quantified invariants
- Multi-contract reasoning
- Storage layout verification

---

## Tips for Learning

1. **Always read the counterexample** - it shows exactly when/how a property fails
2. **Start with failing tests** - understanding failures teaches more than successes
3. **Think in logic** - `require()` = precondition, `assert()` = postcondition/invariant
4. **Build incrementally** - each exercise adds one concept
