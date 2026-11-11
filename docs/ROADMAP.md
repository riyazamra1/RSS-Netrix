# RSS Netrix — Delivery Roadmap

The order below is dependency-aware. Phases are not completion claims; each requires tests and acceptance evidence.

## Phase 0 — Foundation and requirements
- [x] Establish repository identity and Android package ID.
- [x] Publish initial product, architecture and security direction.
- [x] Complete the initial repository and requirements audit (`AUDIT_REPORT.md`).
- [x] Record owner decisions: proprietary licence, single public repo, encrypted source as a parallel workstream, dependency selection (`DECISIONS.md` ADR-009…015).
- [x] Add licence, third-party notices and source-handling policy.
- [x] Draft platform-neutral core contracts, vault threat model, design system and recovery model (`specs/`).
- [ ] Owner review and approval of the foundation specifications.
- [ ] Resolve remaining release requirements and packaging approach.
- [ ] Validate the selected SSH/SFTP/terminal dependencies (dependency, licensing, API compatibility, security, build) before locking versions.
- [ ] Implement and approve the encrypted-source design before adding application source to the public repository.

## Phase 1 — Platform skeletons
- Android native app shell and navigation.
- Native Windows app shell.
- Shared product models and documented protocol contracts where appropriate.
- CI builds without production secrets.

## Phase 2 — SSH foundation
- Host profiles and host-key trust store.
- SSH password and key authentication.
- Interactive terminal and robust connection lifecycle.
- Tests using local disposable SSH fixtures.

## Phase 3 — Daily workflow
- Multiple sessions, tabs and split workspace.
- Command history (minimum 10 recent commands), snippets and copy actions.
- Secure session logging and preferences.

## Phase 4 — SFTP and tunnels
- SFTP browser and reliable transfer lifecycle.
- Local, remote and dynamic forwarding.
- Permission, cancellation and reconnect tests.

## Phase 5 — Credential and key vault
- Platform-protected secret storage.
- Key generation/import and fingerprint display.
- Backup, recovery and re-authentication controls.

## Phase 6 — Encrypted sync
- Threat model and key hierarchy approval.
- Optional encrypted sync service, quota limits and deletion semantics.
- Device enrollment/revocation, conflict handling and recovery tests.
- Cloudflare Worker/R2 only after explicit resource and cost review.

## Phase 7 — Release readiness
- Android and Windows compatibility matrix.
- Security and dependency audit.
- Performance, accessibility and usability testing.
- Signed release builds, privacy policy and support documentation.
- Pilot release before commercial rollout.

## Delivery gates
- Requirements and change list reviewed before each commit.
- One build/deployment at a time.
- Report commit SHA, exact build/test statuses and artifact verification.
- No claim of feature completion based only on UI or a successful compile.
