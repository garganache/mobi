Rules for All code ( Humans & Sub-agents) 
General 
- Read this file before writing ANY cod
- All commands assume you're in the repo root
- When in doubt , check existing code patterns first - don't invent a new one

Git
- Commit messages: concise , imperative( Add x, Fix y )
- Don't commit secrets , .env files, or credentials
- User feature branches for non-trivial changes

Sub-Agent Rules 
- ALWAYS read this file first ( cat CONTRIBUTING.md)
- ALWAYS read .tracker/WORKFLOW.md - the task lifecycle steps are mandatory
- ALWAYS check existing code patterns before writing new code
- NEVER assume a library/component exists - verify with `ls` or `grep`
- NEVER Use placeholder implementation unless explicitly told to
- After writing files , verify they exist : `ls -la <path>`
- After writing code, verify it compiles: run the relevant buil/int command
- After completing a task , update the task file with implementation notest and check DoD boxes

Infrastructure 
- All infra changes go through Terraform or K8S manifests - no manual cloud console changes
- Docker images are built via CI, not locally pushed
- Secrets go in k8s secrets, never in code.
