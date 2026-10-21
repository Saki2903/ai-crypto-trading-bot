# AGENTS.md — Project Development Rules

## 1. Project Identity

This repository is the new AI Crypto Trading Bot project.

The project path is:

`C:\Users\DELL\ai-crypto-trading-bot`

The separate legacy project at `C:\ai_trading_bot` is reference-only and must remain untouched.

## 2. User Learning Preferences

- Teach in simple Bengali with relevant English technical terms.
- Explain why each step is necessary.
- Explain every command, its purpose and expected output.
- Work on one main task at a time.
- Wait for the user's output before advancing.
- Do not assume the user understands code just because they can copy and paste it.

## 3. Change Approval

- Do not modify existing code or configuration without explaining the intended change and obtaining approval.
- Do not install packages or software without explaining the need and obtaining approval.
- Do not execute destructive, risky or trading-related scripts without explicit approval.
- Do not reset, stash, overwrite, delete or discard existing changes without explicit approval.
- Prefer read-only inspections before edits.
- Inspect relevant files before proposing changes.

## 4. Preserve Existing Work

The repository already contains modified and untracked files. Treat all existing work as valuable.

Never assume untracked files are disposable.

Do not overwrite or delete existing files when creating documentation. Check for name conflicts first.

Keep the Git working tree and existing user changes intact unless the user explicitly approves a specific change.

## 5. Trading Safety

- Initial operation is simulation and paper trading only.
- Never place real exchange orders.
- Never enable real-money trading.
- Do not add live order-execution behavior.
- Treat AI output as an untrusted proposal, not an instruction.
- Use an independent deterministic Risk Engine.
- If critical data, validation, API access or risk checks fail, fail closed.
- Invalid or incomplete proposals must not produce simulated trades.
- Never guarantee profitability.

## 6. Secrets and API Keys

- Never display or request the contents of `.env`.
- Never ask the user to paste API keys, secrets or passwords into chat.
- Keep credentials out of source code and Git-tracked files.
- Do not print secret values during testing.
- Use free-tier API access where suitable; do not activate paid services automatically.
- Handle quota, authentication and rate-limit errors safely.

## 7. Architecture Principles

Keep the following responsibilities separate:

- Market data collection and validation
- Market research
- News and sentiment analysis
- AI decision proposals
- Agent coordination
- Deterministic risk validation
- Simulation and portfolio accounting
- Logging, monitoring and reporting

AI-generated decisions must pass independent risk validation before any simulated action.

## 8. Development and Testing

- Verify the active project directory before running commands.
- Verify the selected Python environment before installing or running dependencies.
- Prefer small, understandable and testable changes.
- Explain what each test proves and what it does not prove.
- Do not run the entire application or scheduled loop when a small targeted test is sufficient.
- Do not claim a test passed unless it was actually run and its result was inspected.
- Do not make network requests unless they are necessary, explained and approved.
- Preserve existing tests and test data.

## 9. Git Rules

- Inspect `git status` before editing.
- Never automatically commit, push, reset, stash or clean the repository.
- Preserve modified and untracked files.
- Explain the impact before any Git operation that changes repository state.

## 10. Virtual Environments

The repository currently contains `.venv`, `.venv-1`, `.venv-2` and `.venv-3`.

Do not delete or recreate any environment until the active interpreter and dependencies have been checked.

Do not install packages until the selected environment is confirmed and the user approves.

## 11. Completion Reports

After each task, report:

1. What was done.
2. Why it was needed.
3. Which files were changed.
4. What verification was performed.
5. What remains uncertain.
6. The next single step.

Never report a proposed action as completed unless it was actually completed and verified.
## 12. Project State and Documentation

- Treat `PROJECT_GOALS.md` as the source of truth for the intended project vision, architecture, roadmap, and non-negotiable goals.
- Treat `PROJECT_LOG.md` as the record of actual progress, verified results, known limitations, and outstanding tasks.
- Treat this file, `AGENTS.md`, as the operational rules for development, learning, testing, Git, and safety.
- Do not assume that a planned feature in `PROJECT_GOALS.md` has already been implemented.
- Before continuing previous work, inspect the relevant current files and available test results. Do not rely solely on old conversation summaries or documentation.
- When documentation conflicts with current verified code or test output, identify the discrepancy and ask for clarification when necessary. Do not silently rewrite project goals.
- Update `PROJECT_LOG.md` only after meaningful progress has been completed and verified.
- Preserve the existing contents and history of all three documentation files unless the user approves a specific change.
- Keep all instructions consistent with simulation-only operation, the ₹0 additional monthly budget, step-by-step Bengali mentorship, and the requirement to leave `C:\ai_trading_bot` untouched.
