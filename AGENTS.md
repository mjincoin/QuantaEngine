<!-- BEGIN DESTI PROJECT SKILLS -->
## Project skill reuse

- Keep this project's own rules authoritative; read its AGENTS.md first.
- Locate the workspace from the enclosing multi-project checkout. The control repository (<control> below) is the ONE canonical control checkout named by control_repo in the private host settings (00-dystem on current hosts, 00-desti on older ones); a second checkout of it is a stale duplicate. The skill library is 05-ai/01-skills/. Resolve those paths at runtime; never commit a Windows/macOS home directory or mount path.
- Search the shared library's INDEX.md and read a relevant SKILL.md before reuse; use project-skill-lifecycle only for evidence-backed reusable procedures.
- For context recording, multi-host ownership, Git guards and multi-remote publication, follow <control>/docs/MULTI_HOST_ONBOARDING.md and <control>/docs/operations/AGENT_ENTRY_POLICY.md. Run desti-sync begin on <control> itself first, then only <control>/scripts/repo_sync.py for this project; it refuses duplicate or stale control checkouts, co-author/AI attribution trailers and publishing without today's host context log. Never bypass guards.
- Keep raw sessions, private journals, credentials, keys and machine receipts local. New repositories must be registered in <control>/data/project_sync_registry.csv.
<!-- END DESTI PROJECT SKILLS -->
