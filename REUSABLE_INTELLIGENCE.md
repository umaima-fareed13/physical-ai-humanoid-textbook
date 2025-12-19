# Reusable Intelligence: Automated Deployment Agent

This document describes the **Automated Deployment Agent Skill** implemented for the Physical AI Humanoid Textbook project, satisfying the hackathon's "Reusable Intelligence" requirement.

---

## Overview

The Automated Deployment Agent (`scripts/auto_deploy.py`) is a Python-based intelligent script that autonomously validates, commits, and deploys documentation changes. It acts as a reusable skill that can be invoked by AI agents or run manually to ensure safe, error-free deployments.

---

## How It Works

### Agent Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                 AUTOMATED DEPLOYMENT AGENT                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. BUILD VALIDATION                                       │
│      └─> npm run build                                      │
│          ├─> Success: Continue to next step                 │
│          └─> Failure: STOP + Report detailed errors         │
│                                                             │
│   2. CHANGE DETECTION                                       │
│      └─> git status --porcelain                             │
│          ├─> Changes found: Continue                        │
│          └─> No changes: Exit gracefully                    │
│                                                             │
│   3. STAGE CHANGES                                          │
│      └─> git add .                                          │
│                                                             │
│   4. COMMIT                                                 │
│      └─> git commit -m "Auto-deploy via Agent Skill"        │
│                                                             │
│   5. PUSH TO REMOTE                                         │
│      └─> git push                                           │
│                                                             │
│   ✅ DEPLOYMENT COMPLETE                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Build Validation** | Runs `npm run build` to catch broken links, missing assets, and syntax errors before deployment |
| **Intelligent Error Reporting** | On failure, provides detailed error output with common issues checklist |
| **Change Detection** | Automatically detects if there are changes to deploy |
| **Safe Deployment** | Only commits and pushes if build succeeds |
| **Custom Messages** | Supports custom commit messages via `--message` flag |
| **Cross-Platform** | Works on Windows, macOS, and Linux |

---

## Usage

### Basic Usage

```bash
python scripts/auto_deploy.py
```

### With Custom Commit Message

```bash
python scripts/auto_deploy.py --message "Add Chapter 5: Reinforcement Learning"
```

### As a Claude Code Skill

This script can be invoked by Claude Code or other AI agents:

```
"Please run the auto-deploy skill to push my latest changes"
```

The agent will:
1. Validate the build
2. Report any errors (if build fails)
3. Auto-commit and push (if build succeeds)

---

## Error Handling

When the build fails, the agent provides:

1. **STDERR Output** - Direct error messages from the build process
2. **STDOUT Output** - Last 50 lines of build output for context
3. **Common Issues Checklist**:
   - Broken internal links
   - Missing images or assets
   - Invalid markdown syntax
   - Missing frontmatter in docs
   - JavaScript/TypeScript errors

---

## Integration Points

### CI/CD Pipeline

```yaml
# Example GitHub Actions integration
- name: Run Deployment Agent
  run: python scripts/auto_deploy.py --message "${{ github.event.head_commit.message }}"
```

### Pre-commit Hook

```bash
#!/bin/sh
python scripts/auto_deploy.py
```

### Scheduled Deployment

```bash
# Cron job for daily deployment
0 9 * * * cd /path/to/project && python scripts/auto_deploy.py
```

---

## Why This is "Reusable Intelligence"

1. **Autonomous Decision Making**: The agent decides whether to proceed or abort based on build results
2. **Self-Documenting Errors**: Provides actionable feedback when things go wrong
3. **Portable**: Can be used across any Docusaurus project
4. **Agent-Compatible**: Designed to be invoked by AI agents (Claude Code, etc.)
5. **Idempotent**: Safe to run multiple times; handles "no changes" gracefully

---

## Architecture

```python
class DeploymentAgent:
    """Core agent class with modular methods"""

    def run_build() -> bool       # Validates npm build
    def check_for_changes() -> bool   # Detects git changes
    def stage_changes() -> bool   # git add .
    def commit_changes() -> bool  # git commit
    def push_changes() -> bool    # git push
    def deploy() -> bool          # Orchestrates full pipeline
```

---

## Example Output

### Successful Deployment

```
============================================================
AUTOMATED DEPLOYMENT AGENT
============================================================

ℹ️  [INFO] Starting build validation...
⏳ [WORKING] Running npm build...
✅ [SUCCESS] Build completed successfully!
⏳ [WORKING] Checking for changes...
⏳ [WORKING] Staging changes...
✅ [SUCCESS] Changes staged successfully
⏳ [WORKING] Creating commit...
✅ [SUCCESS] Committed: Auto-deploy via Agent Skill - 2024-12-19 15:30
⏳ [WORKING] Pushing to remote...
✅ [SUCCESS] Successfully pushed to remote!

============================================================
✅ [SUCCESS] DEPLOYMENT COMPLETE!
============================================================
```

### Failed Build

```
============================================================
AUTOMATED DEPLOYMENT AGENT
============================================================

ℹ️  [INFO] Starting build validation...
⏳ [WORKING] Running npm build...
❌ [ERROR] Build failed!

============================================================
BUILD ERROR REPORT
============================================================

[STDERR Output]
----------------------------------------
Error: Links in docs/chapter-5.md are broken

============================================================
COMMON ISSUES TO CHECK:
============================================================
1. Broken internal links (check file paths)
2. Missing images or assets
3. Invalid markdown syntax
4. Missing frontmatter in docs
5. JavaScript/TypeScript errors in components
============================================================

❌ [ERROR] Deployment aborted due to build failure
```

---

## License

This Reusable Intelligence component is part of the Physical AI Humanoid Textbook project, created for the hackathon.
