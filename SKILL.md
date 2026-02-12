# SKILL.md — Project Tracker

## Overview

A text-based project management system designed for autonomous AI agents.

## File Structure

```
.tracker/
├── prd.json          # Project definition + story index
├── stories/          # User stories (STORY-XXX.md)
├── tasks/            # Individual tasks (TASK-XXX.md)
├── progress.md       # Append-only work log
└── learnings.md      # Patterns discovered
```

## Workflow

### Starting Work

1. Read `.tracker/prd.json` to understand the project
2. Read `.tracker/progress.md` to see recent activity
3. Find the next story with `status: todo` and highest priority
4. Update story status to `in_progress`

### During Work

1. Break story into tasks if not already done
2. For each task:
   - Update task status to `in_progress`
   - Implement the required changes
   - Run tests if applicable
   - Update task status to `done`
   - Append entry to `progress.md`

### Completing Work

1. Verify all acceptance criteria are met
2. Update story status to `done`
3. Update `prd.json` metadata
4. Document any learnings in `learnings.md`
5. Commit changes with appropriate message

## Status Values

- `todo` — Not started
- `in_progress` — Currently being worked on
- `done` — Completed successfully
- `blocked` — Cannot proceed (explain why in Notes)
- `cancelled` — Will not be done
