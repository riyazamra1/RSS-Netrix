# RSS Netrix — Delivery Roadmap

The order below is dependency-aware. Phases are not completion claims; each requires tests and acceptance evidence.

## Phase 0 — Foundation and requirements
- [x] Establish repository identity and Android package ID.
- [x] Publish initial product, architecture and security direction.
- [ ] Resolve remaining UX, credential recovery and release requirements.
- [ ] Select SSH/SFTP and terminal dependencies after licensing/security review.
- [ ] Approve encrypted-source build design before adding application source.

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

## Phase 3 — Free daily workflow and terminal customization
- Multiple sessions, tabs and basic split workspace.
- Searchable command history, basic snippets and copy actions.
- All 30+ built-in themes, custom theme editor, colour wheel, HEX/RGB/HSL, ANSI palette and true-colour rendering (Free).
- Native Android/Windows file picker and editable terminal path insertion (Free).
- Secure opt-in session logging and preferences.

## Phase 4 — Free SFTP and SSH tunnels
- SFTP browser, basic upload/download and safe file operations (Free).
- Local, remote and dynamic forwarding (Free).
- Permission, cancellation, reconnect and large-file tests.

## Phase 5 — Free local credential vault and advanced SSH security
- Platform-protected secret storage (Free).
- Key generation/import and fingerprint display (Free where supported).
- Backup, recovery and re-authentication controls.
- Review SSH certificates, FIDO2 and other advanced authentication before tier assignment.

## Phase 6 — Premium productivity and advanced file workflows
- Saved workspace presets and advanced session restoration.
- Multi-host snippet execution and advanced productivity controls.
- Advanced SFTP queue and host-to-host transfer, subject to design review.
- Implement only after feature-level acceptance tests and entitlement design.

## Phase 7 — Premium encrypted sync and team collaboration
- Threat model and key hierarchy approval.
- Optional encrypted sync service, quotas and deletion semantics.
- Device enrollment/revocation, conflict handling and recovery tests.
- Shared vaults, team roles, collaboration, session handoff and audit controls.
- Cloudflare Worker/R2 only after explicit resource and cost review.

## Phase 8 — Release readiness
- Android and Windows compatibility matrix.
- Security and dependency audit.
- Performance, accessibility and usability testing.
- Signed release builds, privacy policy and support documentation.
- Pilot release before commercial rollout.

## Delivery gates
- Free/Premium placement follows the approved matrix in [FEATURE_PARITY_SPEC.md](FEATURE_PARITY_SPEC.md); do not introduce new paywalls without owner approval.
- All terminal theme and colour customization remains Free.
- Premium service entitlements must be tested server-side before any commercial launch.
- Requirements and change list reviewed before each commit.
- One build/deployment at a time.
- Report commit SHA, exact build/test statuses and artifact verification.
- No claim of feature completion based only on UI or a successful compile.
