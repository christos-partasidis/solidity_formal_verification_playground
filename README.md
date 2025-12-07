# Solidity Formal Verification Playground  
*A progressive repository for learning formal verification of Solidity smart contracts, from basic assertions to industry-grade invariants for upgradeable systems.*

## 1. Overview 🔎

This repository explores formal verification in Solidity using:

- **Solidity SMTChecker** (built into the compiler)  
- **Certora Prover** (an industry standard formal verification engine)  
- **solc-verify** (a Hoare logic based verifier for critical systems)  
- **Upgradeable smart contract patterns**

The goal is to develop a deep understanding of how to specify and prove correctness in Ethereum smart contracts. The smart contracts
range from small isolated functions to multi contract upgradeable architectures used in finance, DeFi, and Central bank digital currency(CBDC) systems.

## 2. Why Formal Verification Matters 🤔

Mission critical blockchain applications require **mathematical guarantees** of correctness, especially:

- Central Bank Digital Currencies (e.g., **EuroCoin** and other CBDCs)  
- Regulated financial infrastructure  
- Permissioned institutional ledgers  
- Public DeFi protocols securing billions  
- Upgradeable systems requiring invariants across implementations  

Formal verification provides these guarantees through:

- SMT solving  
- Hoare logic proofs  
- State transition invariants  
- Cross contract reasoning  

This repository is designed as a step-by-step laboratory for mastering these techniques.

Each exercise develops the mental framework needed for deeper verification techniques.

## 3. Tools Used in This Repository⚙️

### 3.1. Solidity SMTChecker ⚙️

- Integrated into the Solidity compiler  
- Explores execution paths symbolically  
- Detects counterexamples automatically  
- Perfect for learning local and state level invariants  
- Fast and beginner friendly  

The SMTChecker interprets assertions as logical formulas and attempts to prove:

∀ inputs: preconditions ⇒ assertion holds

### 3.2. Certora Prover ⚙️

Used by: Aave, Compound, Balancer, Lido, MakerDAO, Uniswap  

Provides:

- Rule based invariants  
- Multi contract reasoning  
- Upgrade safety proofs  
- Storage layout verification  
- Cross function and cross contract correctness  

Certora is considered the gold standard for high assurance verification in production systems.

### 3.3. solc-verify ⚙️

A standalone tool that applies **Hoare logic**, enabling:

- Pre-conditions and post-conditions  
- Loop invariants  
- Function level correctness proofs  
- Modular reasoning  

Why Hoare Logic Matters

Hoare logic is essential in:

- Certified financial systems  
- CBDCs and institutional tokens (e.g., **EuroCoin**)  
- Systems requiring regulatory grade correctness  
- High stakes smart contract standards  

This makes **solc-verify** an important intermediate tool, especially for future work related to CBDCs or standardized digital currency frameworks.

## 4. Completed Exercises 🏋️‍♀️

### 4.1. SMTChecker setup  
Confirmed solver compatibility and execution.

### 4.2. Failing assertion  
Demonstrated counterexample discovery with:  
`assert(x > x + 1);`

### 4.3 Unreachable states  
Showed how a `require` or overflow prevents assertion execution.

### 4.4 Invalid invariant detection  
SMTChecker identified that `balance <= 1000` was not enforced.

### 4.5 Fixed invariant with domain restriction  
Enforced via `require(x <= 1000);`, thus solver proves the invariant.

These provide the conceptual foundation for all upcoming work.

## 5. Roadmap 🎯

### Phase 1 - Foundation (SMTChecker) (in progress🎯)
- Assertion semantics  
- Preconditions  
- State invariants  
- Transition invariants  
- Reasoning over mappings/arrays  
- Arithmetic proofs  

### Phase 2 - Hoare Logic (solc-verify)
- Pre/post-conditions  
- Loop invariants  
- Modular verification  
- Formal proofs for financial primitives  
- CBDC style correctness properties  

### Phase 3 - Transparent Proxy Verification (Certora + SMTChecker)
- State preservation across upgrades  
- Admin only upgradeability  
- Storage collision invariants  
- Behavioral equivalence rules  

### Phase 4 - UUPS Upgradeability Verification
- ERC1967(or similar) layout invariants  
- Upgrade flow correctness  
- Implementation logic invariants  

### Phase 5 - Advanced Topics
- Multi contract Certora invariants  
- Symbolic execution with Halmos  
- Governance and permission invariants  
- Economic invariants (AMMs, lending protocols)  


## End Goal 🏆

By completing this repository, you will gain the ability to:

- Verify upgrade safety  
- Guarantee state invariants  
- Ensure storage correctness  
- Prove behavioral consistency across versions  
- Write Certora rules like professional auditors  
- Apply Hoare logic for critical financial systems  
- Build fully verified upgradeable architectures  

This represents the same level of rigor used in high-assurance DeFi, institutional finance, and CBDC engineering.

















