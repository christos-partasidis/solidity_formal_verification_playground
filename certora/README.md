# Certora Prover Guide

This directory contains Certora Verification Language (CVL) specifications for formally verifying our Solidity contracts.

## Table of Contents

1. [CVL Syntax for Beginners](#1-cvl-syntax-for-beginners)
2. [Understanding the Verification Process](#2-understanding-the-verification-process)
3. [Completed Specifications](#3-completed-specifications)
4. [Directory Structure](#4-directory-structure)
5. [Running Verifications](#5-running-verifications)

---

## 1. CVL Syntax for Beginners

### 1.1 The `methods` Block

The `methods` block declares which contract functions the spec can interact with:

```cvl
methods {
    function counter() external returns (uint256) envfree;
    function MAX() external returns (uint256) envfree;
    function increment(uint256) external;
    function decrement(uint256) external;
}
```

#### Why `function` keyword?

The `function` keyword explicitly tells CVL "this is a Solidity function I want to reference." It mirrors Solidity's syntax and makes it clear we're declaring an external interface.

```cvl
function counter() external returns (uint256) envfree;
│        │         │        │               │
│        │         │        │               └── Special annotation (see below)
│        │         │        └── Return type (matches Solidity)
│        │         └── Visibility (external/public)
│        └── Function name from the contract
└── Keyword indicating this is a function declaration
```

#### What is `envfree`?

`envfree` means the function **does not depend on the blockchain environment** (msg.sender, msg.value, block.timestamp, etc.).

| Annotation | Meaning | When to Use |
|------------|---------|-------------|
| `envfree` | Function is pure/view and doesn't read `msg.*` or `block.*` | Getters, pure functions |
| *(none)* | Function may depend on environment | State-changing functions, functions using `msg.sender` |

**Why it matters:**
```cvl
// With envfree - can call directly
uint256 value = counter();

// Without envfree - must pass environment
env e;
increment(e, 10);  // e contains msg.sender, msg.value, etc.
```

#### Why `counter()` and `MAX()` to retrieve values?

In CVL, we call functions using **parentheses** just like in Solidity:

```cvl
// In Solidity:
uint256 x = counter();

// In CVL (identical syntax):
uint256 x = counter();
```

Even though `counter` is a state variable in Solidity, Solidity auto-generates a getter function `counter()`. CVL interacts with this getter.

### 1.2 The `env` Type

The `env` type represents the **blockchain environment** for a transaction:

```cvl
rule incrementIncreasesCounter(uint256 amount) {
    env e;  // Declares an environment variable
    
    increment(e, amount);  // Pass env to state-changing function
}
```

**What `env` contains:**
- `e.msg.sender` — The caller's address
- `e.msg.value` — ETH sent with the call
- `e.block.timestamp` — Current block time
- `e.block.number` — Current block number

**Example: Restricting to non-zero sender**
```cvl
rule onlyValidCaller() {
    env e;
    require e.msg.sender != 0;  // Exclude zero address
    
    increment(e, 10);
    // ...
}
```

### 1.3 Rules vs Invariants

#### Rules
Rules verify properties about **single function executions**:

```cvl
rule resetSetsToZero() {
    env e;
    
    reset(e);                    // Execute the function
    
    assert counter() == 0;       // Check the postcondition
}
```

**Structure:**
```
rule ruleName(parameters) {
    // 1. Setup (optional preconditions)
    // 2. Execute function(s)
    // 3. Assert postconditions
}
```

#### Invariants
Invariants verify properties that must **always hold** across all functions:

```cvl
invariant counterBounded()
    counter() <= MAX()
```

This checks that `counter() <= MAX()` holds:
- After constructor
- After every public/external function call
- For all possible inputs

**With preserved block:**
```cvl
invariant counterBounded()
    counter() <= MAX()
    {
        preserved {
            require counter() <= MAX();  // Assume invariant holds before
        }
    }
```

The `preserved` block tells Certora: "Assume the invariant holds before the function call, then prove it still holds after."

### 1.4 Assertions

```cvl
assert counterAfter == counterBefore + amount, "Error message";
│      │                                       │
│      │                                       └── Optional error message
│      └── Boolean expression to verify
└── Keyword (must be true for verification to pass)
```

### 1.5 Quick Reference

| CVL Element | Purpose | Example |
|-------------|---------|---------|
| `methods { }` | Declare contract interface | `function foo() external envfree;` |
| `envfree` | Function doesn't use msg.* or block.* | `function balance() external returns (uint) envfree;` |
| `env` | Blockchain environment for a call | `env e; transfer(e, to, amount);` |
| `rule` | Verify property of single execution | `rule transferWorks() { ... }` |
| `invariant` | Property that always holds | `invariant positive() balance() >= 0` |
| `assert` | Condition that must be true | `assert x > 0, "x must be positive";` |
| `require` | Assume a condition (filter inputs) | `require amount > 0;` |

---

## 2. Understanding the Verification Process

### 2.1 What Happens When You Run `certoraRun`

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Your Machine   │────▶│  Certora Cloud   │────▶│  Results Page   │
│                 │     │                  │     │                 │
│ • Solidity src  │     │ • Compile        │     │ • Pass/Fail     │
│ • CVL spec      │     │ • SMT solving    │     │ • Counterexamples│
│ • Config file   │     │ • Prove/Disprove │     │ • Call traces   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

**Step by step:**

1. **Local compilation**: `certoraRun` compiles your Solidity using `solc` locally
2. **Package & upload**: The CLI packages:
   - Compiled bytecode
   - Source code (for display in reports)
   - CVL specification
   - Configuration options
3. **Cloud processing**: Certora's servers:
   - Parse the CVL spec
   - Convert everything to SMT formulas
   - Run powerful SMT solvers (Z3, CVC5)
   - Search for counterexamples
4. **Results**: You get a URL with interactive results

### 2.2 What Gets Sent to Certora?

| Item | Sent? | Purpose |
|------|-------|---------|
| Solidity source code | ✅ Yes | Display in reports, source mapping |
| Compiled bytecode | ✅ Yes | The actual verification target |
| CVL specification | ✅ Yes | Properties to verify |
| Configuration | ✅ Yes | Options, paths, settings |
| Your API key | ✅ Yes | Authentication |

**Important:** Your source code is sent to Certora's cloud servers. For sensitive projects, consider:
- Certora's enterprise offerings with on-premise options
- Their security and confidentiality policies

### 2.3 Can You Send Only Bytecode?

**Short answer:** No, not easily.

**Why source is needed:**
1. **Debugging**: Counterexamples reference source lines
2. **Internal functions**: CVL can verify internal function behavior
3. **Storage layout**: Certora needs to understand storage variables
4. **Symbolic execution**: Works better with source-level information

**Alternative approaches:**
- Certora primarily works with source code
- For verified bytecode, you'd need tools like the EVM symbolic executor

### 2.4 Pricing and Usage

| Tier | Cost | Details |
|------|------|---------|
| **Academic/Research** | Free | Apply via Certora website |
| **Free tier** | Limited | Basic usage for learning |
| **Commercial** | Paid | Contact Certora for pricing |

**Your current status:** You have an API key, which suggests academic/free access.

**Rate limits:**
- There may be limits on concurrent jobs
- Complex verifications may have time limits
- Check the Certora dashboard for your quota

### 2.5 Verification Time

Verification time depends on:

| Factor | Impact |
|--------|--------|
| Contract complexity | More functions = longer |
| Number of rules | Each rule verified separately |
| Loop bounds | Unbounded loops are hard |
| Storage operations | Mappings add complexity |

**Typical times:**
- Simple contract (like BoundedCounter): 30 seconds - 2 minutes
- Medium DeFi contract: 5-30 minutes
- Complex protocol: Hours

---

## 3. Completed Specifications

We have three verified specifications demonstrating progressively advanced CVL concepts:

### 3.1 BoundedCounter.spec

**Purpose:** Introduction to CVL basics — rules and invariants.

**Key concepts demonstrated:**
- `methods` block with `envfree` annotation
- `env` type for state-changing functions
- Basic `rule` and `invariant` syntax
- `preserved` block for inductive proofs

**Run:** `certoraRun certora/confs/BoundedCounter.conf`

---

### 3.2 TokenBalance.spec (Ghost Variables)

**Purpose:** Demonstrate **ghost variables** — proving properties SMTChecker cannot!

**The Problem:**
SMTChecker **cannot** prove: `Σ balances[addr] == totalSupply`

Why? SMTChecker can't reason about quantified properties over unbounded mappings.

**The Solution:**
Use a **ghost variable** to independently track the sum of all balances:

```cvl
ghost mathint sumOfBalances {
    init_state axiom sumOfBalances == 0;
}

hook Sstore balances[KEY address addr] uint256 newValue (uint256 oldValue) {
    sumOfBalances = sumOfBalances - oldValue + newValue;
}

invariant sumOfBalancesEqualsTotalSupply()
    sumOfBalances == to_mathint(totalSupply())
```

**Key concepts demonstrated:**
- `ghost` variables for tracking aggregate state
- `hook Sstore` to intercept storage writes
- `mathint` type for arbitrary precision
- `to_mathint()` conversion
- Parametric rules with `method f`

**Run:** `certoraRun certora/confs/TokenBalance.conf`

---

### 3.3 ArraySum.spec

**Purpose:** Rule-based verification for arrays (alternative to ghost approach).

**Why different from TokenBalance?**
- Arrays have complex storage (length + elements stored separately)
- Ghost hooks for arrays are trickier than mappings
- Sometimes **rules are simpler** than ghost tracking

**Key concepts demonstrated:**
- Rule-based verification (no ghosts)
- Parametric rules with `method f` and `calldataarg`
- `sig:functionName(params).selector` syntax
- When to use rules vs ghosts

**Run:** `certoraRun certora/confs/ArraySum.conf`

---

### Comparison: Ghost Variables vs Rules

| Aspect | TokenBalance (Ghost) | ArraySum (Rules) |
|--------|---------------------|------------------|
| Data structure | `mapping(address => uint)` | `uint256[]` |
| Verification approach | Ghost + hooks + invariant | Rules only |
| Proves exact sum | ✅ Yes (`Σ balances == total`) | ❌ No (proves operations correct) |
| Complexity | Higher | Lower |
| Best for | Global invariants over mappings | Functional correctness |

**When to use ghosts:**
- Need to prove aggregate properties (`Σ`, `∀`, `∃`)
- Working with mappings (clean KEY-based hooks)
- Property must hold across ALL functions

**When to use rules:**
- Verifying specific function behavior
- Arrays (complex storage layout)
- Simpler specs that don't need global tracking

---

### 3.4 TransparentProxy.spec ✅ 🔥 (Proxy Pattern)

**Contract:** `contracts/03-transparent-proxy/TransparentProxy.sol`

**Purpose:** Verify access control and upgrade safety in proxy contracts.

**What it proves:**
| Property | Type | Description |
|----------|------|-------------|
| `onlyAdminCanUpgrade` | Rule | Non-admins cannot call upgradeTo() |
| `adminCanUpgrade` | Rule | Admin can successfully upgrade |
| `upgradeChangesImplementation` | Rule | upgradeTo(x) sets implementation to x |
| `upgradePreservesAdmin` | Rule | upgradeTo() doesn't change admin |
| `adminNeverChangesExceptFallback` | Parametric | No non-fallback function changes admin |
| `onlyUpgradeChangesImplementation` | Parametric | Only upgradeTo can change implementation |
| `viewFunctionsAreReadOnly` | Rule | View functions don't modify state |

**Key concepts demonstrated:**
- `@withrevert` and `lastReverted` for revert checking
- `f.isFallback` to filter out fallback functions
- Parametric rules with `filtered { f -> condition }`
- Understanding proxy security limitations

**Important Discovery: The Fallback Vulnerability 🔥**

During verification, we discovered that the `fallback()` function's `delegatecall` could allow a malicious implementation to overwrite the proxy's `admin` and `implementation` storage slots!

This is why production proxies use **EIP-1967 storage slots**:
```solidity
bytes32 constant ADMIN_SLOT = keccak256("eip1967.proxy.admin") - 1;
bytes32 constant IMPL_SLOT = keccak256("eip1967.proxy.implementation") - 1;
```

**Run:** `certoraRun certora/confs/TransparentProxy.conf`

---

## 4. Directory Structure

```
certora/
├── specs/                       # CVL specification files
│   ├── BoundedCounter.spec      # Basic rules and invariants
│   ├── TokenBalance.spec        # Ghost variables for sum invariant
│   ├── ArraySum.spec            # Rule-based array verification
│   └── TransparentProxy.spec    # Proxy access control and upgrade safety
├── confs/                       # Configuration files
│   ├── BoundedCounter.conf
│   ├── TokenBalance.conf
│   ├── ArraySum.conf
│   └── TransparentProxy.conf
├── rules/                       # (Legacy) Additional rule files
│   ├── admin.cvl
│   ├── invariants.cvl
│   └── upgrade.cvl
└── README.md                    # This file
```

### Configuration File Format

```json
{
    "files": [
        "contracts/01-smtchecker/05-transitions/BoundedCounterFixed.sol"
    ],
    "verify": "BoundedCounterFixed:certora/specs/BoundedCounter.spec",
    "wait_for_results": "all",
    "rule_sanity": "basic",
    "msg": "Description shown in dashboard"
}
```

| Field | Purpose |
|-------|---------|
| `files` | Solidity files to compile |
| `verify` | `ContractName:path/to/spec.spec` |
| `wait_for_results` | Wait for completion (`all`, `none`) |
| `rule_sanity` | Check rules are meaningful (`basic`, `advanced`) |
| `msg` | Label for this run in dashboard |

---

## 5. Running Verifications

### Basic Command

```bash
cd /path/to/project
certoraRun certora/confs/BoundedCounter.conf
```

### Environment Setup

Ensure these are set (add to `~/.zshrc`):
```bash
export PATH="$PATH:/Users/christospartasidis/Library/Python/3.9/bin"
export CERTORAKEY="your-api-key-here"
```

### Viewing Results

After running, you'll get a URL like:
```
https://prover.certora.com/output/6302848/xxxxx
```

The dashboard shows:
- ✅ Green: Rule/invariant verified
- ❌ Red: Counterexample found
- ⚠️ Yellow: Timeout or inconclusive

---

## Next Steps

1. ~~**Phase 3: Transparent Proxy Verification**~~ ✅ Done
2. **Phase 4: Create a Fixed TransparentProxy** — Fix vulnerabilities discovered and verify
3. **Phase 5: Diamond Pattern** — Analyse and verify the diamond proxy pattern
4. **Learn more CVL**: See [Certora Documentation](https://docs.certora.com/)
