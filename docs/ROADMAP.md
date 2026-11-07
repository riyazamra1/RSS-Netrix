# RSS Netrix — Delivery Roadmap

The order below is dependency-aware. Phases are not completion claims; each requires tests and acceptance evidence.

## Phase 0 — Foundation and requirements
- [x] Establish repository identity and Android package ID.
- [x] Publish initial product, architecture and security direction.
- [ ] Resolve remaining UX, credential recovery and release requirements.
- [ ] Select SSH/SFTP and terminal dependencies after licensing/security review.
- [x] Document encrypted-source and trusted-build design.
- [x] Add experimental AES-256-GCM source-bundle utility and secret-free negative/round-trip tests (test execution pending).
- [ ] Complete independent cryptographic review, streaming implementation, key custody, recovery and rotation before production use.
- [ ] Verify negative tests, ephemeral cleanup and source-leakage controls.
- [ ] Verify protected-workflow negative tests, ephemeral cleanup and source-leakage controls.
- [ ] Do not enable source decryption in CI until protected-environment controls and repository branch protections are verified.
- [ ] Define Free/Premium feature matrix and licensing lifecycle.
- [ ] Define official RSS website and store distribution procedures.
- [ ] Do not add plaintext application source to the public repository.
- [ ] Do not publish customer binaries as public GitHub release assets.

## Phase 1 — Platform skeletons
- Android native app shell and navigation.
- Native Windows app shell.
- Shared product models and documented protocol contracts where appropriate.
- CI builds without production secrets; encrypted-source release path only after Phase 0 gates pass.

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

## Phase 7 — Release readiness and official distribution
- Android and Windows compatibility matrix.
- Security and dependency audit.
- Performance, accessibility and usability testing.
- Signed release builds, privacy policy and support documentation.
- Android distribution via official RSS website / Google Play Store.
- Windows distribution via official RSS website / Microsoft Store.
- Verify Free feature availability, Premium activation and update eligibility.
- No public GitHub binary releases.
- Pilot release before commercial rollout.

## Delivery gates
- Requirements and change list reviewed before each commit.
- One build/deployment at a time.
- Report commit SHA, exact build/test statuses and artifact verification.
- No claim of feature completion based only on UI or a successful compile.
