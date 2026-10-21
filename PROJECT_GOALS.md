# AI Crypto Trading Bot — Final Goals

**Version:** 1.0  
**Status:** Goals finalized; implementation in progress  
**Initial mode:** Simulation / paper trading only

## 1. Project Vision

Build an autonomous multi-agent AI crypto trading research and simulation system. Multiple agents will analyze market data, technical indicators, available news and sentiment, then propose BUY, SELL or HOLD decisions based on evidence.

The system will automate research, decision coordination, risk validation, simulation and performance reporting. It will not be a fixed-rule-only bot.

## 2. Final Preferences

- Budget: ₹0 additional monthly cost.
- Editor: Visual Studio Code.
- Mentor: ChatGPT in browser.
- Language: Python 3.12.
- AI runtime: Suitable free-tier cloud API.
- Learning style: Understand each code step.
- Workflow: One step at a time; verify output before proceeding.
- Initial market: BTC/USDT.
- Initial timeframe: 1 hour.
- Trading mode: Simulation / paper trading only.
- Legacy project: `C:\ai_trading_bot` must remain untouched.

Free-tier availability, quotas and rate limits may change. Never activate a paid service automatically.

## 3. Proposed Agents and Components

### Market Data Agent
Collect public market data, validate OHLCV records, and analyze price, volume, volatility and indicators.

### News & Sentiment Agent
Analyze available news and sentiment. Record sources and timestamps. Do not invent missing information.

### Market Research Agent
Evaluate trends, returns, volatility and other available evidence.

### AI Decision Agent
Produce a structured BUY, SELL or HOLD proposal with reasoning, supporting evidence, confidence and limitations.

### Agent Coordinator
Coordinate agent workflows, validate their outputs and detect incomplete or conflicting evidence.

### Independent Risk Engine
Use deterministic Python rules independent of the AI model. Validate position size, exposure, drawdown and loss limits. Reject invalid proposals and fail safely when critical data or services are unavailable.

### Simulation Engine
Maintain a simulated portfolio, track positions and account for estimated fees and slippage. Record decisions, simulated actions, profit/loss and drawdown.

### Monitoring and Reporting
Record errors, API failures, decisions and performance. Stop the workflow when critical safety checks fail.

## 4. Core Workflow

1. Collect public market data.
2. Validate data and calculate features.
3. Run market research and available news/sentiment analysis.
4. Coordinate agent outputs.
5. Generate a structured AI decision proposal.
6. Validate the proposal through the independent Risk Engine.
7. Apply permitted actions only to the simulated portfolio.
8. Update portfolio metrics.
9. Save logs and reports.
10. Check system health before the next cycle.

If critical data is missing, an API fails, a response is invalid, or risk validation fails, the system must not perform a simulated trade.

## 5. Technology Stack

- Python 3.12
- VS Code and Git
- Existing virtual environment, after verification
- CCXT for public exchange market data
- Pandas and NumPy for data analysis
- SQLite for records and logs
- One suitable free-tier cloud LLM API
- Testing and visualization libraries as needed

Avoid unnecessary installations, paid coding agents, paid APIs, GPUs and cloud servers.

## 6. Development Roadmap

1. **Project organization:** Verify project structure, preserve existing changes and create documentation.
2. **Market data:** Validate the existing pipeline and analyze returns, volatility and drawdown.
3. **AI integration:** Connect a suitable free-tier API with secure credentials and error handling.
4. **Multi-agent architecture:** Test research, news/sentiment, decision and coordination separately.
5. **Independent Risk Engine:** Implement deterministic risk checks and failure handling.
6. **Backtesting:** Evaluate historical results with fees, slippage and drawdown.
7. **Paper trading:** Test simulated decisions using public market data.
8. **Autonomous simulation:** Automate the workflow with logging and recovery handling.
9. **Monitoring:** Evaluate reliability, risk controls and performance.

SMA crossover is an educational baseline only, not the predetermined final strategy.

## 7. Non-Negotiable Safety Rules

1. No real-money trading or live order execution.
2. Never modify, run or reuse the configuration of `C:\ai_trading_bot`.
3. Never expose API keys, secrets, passwords or `.env` contents in chat.
4. Obtain approval before code modifications, installations, destructive commands or risky script execution.
5. Never reset, stash, overwrite or delete existing uncommitted work without explicit approval.
6. Never automatically activate paid services.
7. Treat all AI outputs as untrusted proposals.
8. Fail closed when the Risk Engine or a critical validation step fails.
9. Do not guarantee profitability.

## 8. Learning Rules

- Explain why each step is needed.
- Explain the purpose and expected output of every command.
- Provide one main task at a time.
- Verify results before proceeding.
- Preserve existing files and inspect before editing.
- Diagnose errors before attempting fixes.
- Avoid unnecessary repeated tasks.

## 9. Definition of Success

The initial system will be successful when its data pipeline is validated, agents can be tested independently, AI responses follow a defined structure, risk checks block unsafe actions, historical tests can be reproduced, and an automated simulation workflow produces logs and reports without sending real orders.

Profitability must be evaluated using evidence; it is never assumed.

## 10. Current Status

The goals and roadmap are finalized. The existing codebase contains prior work and uncommitted changes that must be preserved.

Next: complete project documentation and verify the Python environment before making implementation changes.
## 11. Implementation Progress

**Last updated:** 2026-10-16

This section records implementation progress separately from the finalized project goals. Existing goals, architecture, roadmap, and safety rules remain unchanged.

### 11.1 Verified Progress

**Portfolio Ledger — `src/portfolio_ledger.py`**

The latest reported test run verified the following:

- Initial simulated USDT and BTC balances.
- BUY fill updates simulated balances correctly.
- Identical duplicate fills are ignored.
- Conflicting data for an existing fill ID is rejected.
- SELL fill updates simulated balances correctly.
- Balances persist across a new ledger instance using the same database.
- SELL is rejected when the simulated BTC balance is insufficient.
- Invalid fill inputs are rejected, including NaN quantity, infinite price, zero quantity, and an unsupported trading symbol.

**Test result:** All seven main portfolio-ledger tests and four invalid-input tests passed in the reported test run.

**Order State Store — `src/order_state_store.py`**

Previously reported tests covered order persistence, status transitions, partial-fill tracking, restart recovery, duplicate client order IDs, and invalid order quantities. The reported order-state test suite passed.

**Safety verification:** The reported portfolio-ledger tests used a temporary database. No exchange API request or real trade was executed during those tests.

### 11.2 Current Limitations

The following must not be considered complete without further inspection and verification:

- Integration between the order-state database and portfolio-ledger database.
- Atomic or otherwise reliably recoverable processing of order updates and fill events across both components.
- Exchange-level order reconciliation and recovery from uncertain execution outcomes.
- Transaction fees, slippage, and other trading costs in portfolio accounting.
- End-to-end integration of the complete multi-agent simulation workflow.
- Full-project test and compilation status following the latest changes.

### 11.3 Next Development Task

Review the existing order-state store, portfolio ledger, and their tests. Design an exchange-independent fill-processing workflow that safely updates order state and portfolio accounting, with tests for duplicate events, conflicting data, failures, and restart recovery.

Use isolated test fixtures and temporary databases where practical. Preserve existing project files, databases, uncommitted Git changes, and the separate legacy project.

Do not introduce live exchange order execution or real-money trading.

### 11.4 Verification Policy

Only record implementation results supported by inspected code and actual test output. Distinguish verified functionality from planned work. Update this section when meaningful progress has been completed and verified.