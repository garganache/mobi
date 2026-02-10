# Agent Workflow Guide

This document defines the standard workflow for agents working on tasks in the mobi project.

---

## Before Starting a Task

### 1. Understand the Current State
```bash
cat .tracker/status.md
```
Read the current project status to understand what's been done and what's in progress.

### 2. Read Your Task
```bash
cat .tracker/tasks/TASK-XXX.md
```
Carefully read:
- **Description**: What needs to be done
- **Definition of Done**: Acceptance criteria you must meet

### 3. Learn from the Past
```bash
cat .tracker/learnings.md
```
Review documented mistakes and patterns to avoid repeating previous errors.

### 4. Follow Coding Standards
```bash
cat CONTRIBUTING.md
```
Understand the project's coding rules, conventions, and best practices.

---

## During Task Execution

### Work in Small Steps
- Break the task into incremental steps
- Complete one step at a time
- **Never assume anything works**

### Verify Each Step
After each change, verify it works - these are examples:

```bash
# For code changes
npm run build          # Frontend
pytest                 # Backend tests
npm run lint           # Linting

# For infrastructure
terraform plan         # Terraform changes
kubectl get pods       # Kubernetes state
kubectl describe pod   # Check pod status

# For configuration
cat <file>             # Read the actual file content
ls -la <dir>           # Verify files exist
```

### If Blocked
1. **Stop immediately** - don't work around the blocker
2. **Document the blocker** in the task file:
   ```markdown
   **Status:** blocked

   ## Blocker
   [Detailed explanation of what's blocking progress]
   ```
3. **Update progress.md** with the blocker details
4. **Do not** continue or make assumptions

---

## After Completing the Task

### Required Verification Steps

Complete **ALL** of these steps before marking the task as done:

#### 1. Infrastructure Verification (if applicable)
```bash
# Terraform
terraform plan -out=plan.tfplan
# Should show "No changes" or expected changes only

# Kubernetes
kubectl get all -n <namespace>
kubectl logs <pod-name>
# Verify pods are running and logs show no errors
```

#### 2. Code Verification
```bash
# Frontend
cd frontend
npm run build          # Must succeed
npm run lint           # Must pass with no errors
npm run type-check     # Must pass (if using TypeScript)

# Backend
cd backend
pytest                 # All tests must pass
ruff check .           # Linting must pass (if configured)
mypy .                 # Type checking must pass (if configured)
```

#### 3. Test Verification ⚠️ **MANDATORY BEFORE GIT PUSH**
```bash
# Unit tests
pytest                 # Backend - MUST PASS
npm test               # Frontend - MUST PASS

# Integration tests (if applicable)
npm run test:integration

# E2E tests (REQUIRED)
cd frontend
npm run test:e2e       # MUST PASS before any git push

# If E2E tests fail, DO NOT PUSH
# Fix issues and re-run until all tests pass
```

**🚨 CRITICAL: NO CODE SHOULD BE PUSHED TO MAIN WITHOUT PASSING E2E TESTS**

#### 4. Update the Task File
```bash
# Edit the task file to mark it as done
# Update all checkboxes in Definition of Done
```

Example:
```markdown
**Status:** done

## Definition of Done
- [x] Feature implemented
- [x] Tests passing
- [x] Linting passing
- [x] Documentation updated
```

#### 5. Update Progress Log
```bash
# Append to progress.md
echo "## TASK-XXX: [Task Title] - $(date +%Y-%m-%d)

**Status:** Completed

### What Was Done
- [Bullet point summary of changes]
- [Key implementation details]

### Verification
- [x] Build passing
- [x] Tests passing
- [x] Linting passing

### Files Changed
- path/to/file1.ts
- path/to/file2.py
" >> .tracker/progress.md
```

---

## Golden Rules

1. **Read Before Acting** - Always read status, task, learnings, and contributing docs
2. **Small Steps** - Work incrementally, never big-bang changes
3. **Verify Everything** - Don't assume, verify with actual commands
4. **Document Blockers** - If stuck, document clearly and stop
5. **Complete Verification** - All verification steps required before marking done
6. **Update Logs** - Always update progress.md after completion

---

## Example Workflow

```bash
# 1. Before starting
cat .tracker/status.md
cat .tracker/tasks/TASK-015.md
cat .tracker/learnings.md
cat CONTRIBUTING.md

# 2. During work (repeat for each step)
# ... make a change ...
npm run build                    # Verify it builds
npm test                         # Verify tests pass
git diff                         # Review the change

# 3. After completion - Full verification
cd frontend && npm run build && npm run lint && npm test
cd ../backend && pytest && ruff check .
kubectl get pods -n mobi-dev     # If K8s related

# 4. Update task file
# Edit .tracker/tasks/TASK-015.md
# Mark status: done, check all boxes

# 5. Update progress log
echo "[completion summary]" >> .tracker/progress.md

# 6. Done!
```

---

## Status Values

- `todo` - Not started
- `in_progress` - Currently working on it
- `blocked` - Cannot proceed (must document why)
- `done` - Completed and verified
- `cancelled` - Will not be done
