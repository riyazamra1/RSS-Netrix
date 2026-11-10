# RSS Netrix — Autonomous Implementation Plan (Pending Owner Approval)

**Status:** Prepared for owner review. **Not started.**
**Companion:** [`docs/AUDIT_REPORT.md`](AUDIT_REPORT.md)
**Date:** 2026-11-10
**Rule:** No implementation begins until the owner reviews the audit and approves this plan. PR #1 and PR #2 must not be merged. No paid resources, production secrets, accounts, infrastructure or published binaries are created.

---

## 1. Execution principles

- Requirements and the change list are reviewed before each commit (ADR-008).
- One build/deployment at a time; report commit SHA and exact build/test statuses.
- Never infer success from a queued workflow — verify the actual artefact.
- Secret-free public CI only; SHA-pinned actions; least-privilege permissions.
- Application source admission stays blocked unless the owner selects the encrypted-source track (Track 9) and its gates pass.
- Free tier stays free: core SSH, secure local credentials, terminal tabs/basic splits, **all terminal themes/colour controls**, file attachment/path insertion, basic SFTP, basic tunnels, basic history/snippets, basic host import/export.
- Android application ID stays `com.riyaz.rssnetrix`; Windows display name stays `RSS Netrix`.

---

## 2. Phase gates (definition of done per phase)

Each phase is complete only when: the real operation works; automated tests cover normal/error/cancellation/security paths; both platforms pass their matrix tests; no secret leaks into logs/artefacts; accessibility and responsive behaviour are checked; documentation is accurate; and the artefact is verified (signed, correct package identity).

---

## 3. Work plan (dependency-ordered)

### Step 0 — Governance (unblocks everything; owner input required for 0.1–0.3)
- 0.1 Owner decides repository model (public + encrypted source vs private source).
- 0.2 Owner decides licence; add `LICENSE`; fix repo description.
- 0.3 Owner confirms dependency selection (Android sshlib/termlib; Windows SSH.NET + WinUI 3).
- 0.4 Reconcile overlapping docs from PR #1, PR #2 and the design branch into one coherent set; resolve the ADR-009 collision; add ADRs for dependencies, licence and repository model. **Do not merge PR #1/#2.**
- 0.5 Open a draft PR (tracking only) for `docs/encrypted-source-build-design` so the review is preserved.
- 0.6 Enable `main` branch protection; add secret-free CI + secret scanning + dependency review.

### Step 1 — Specifications
- 1.1 Freeze platform-neutral contracts (host model, lifecycle state machine, trust store, vault, transfer model, error taxonomy).
- 1.2 Specify the RSS design system (tokens, typography, components).
- 1.3 Specify vault envelope + platform protection; write the vault threat model.
- 1.4 Specify credential recovery (owner-visible).

### Step 2 — Platform skeletons
- 2.1 Android project (Kotlin/Compose/Material 3), app ID `com.riyaz.rssnetrix`, Play-compliant target API (API 36), module boundaries, secret-free CI.
- 2.2 Windows project (.NET 10 + WinUI 3), module boundaries, secret-free CI.

### Step 3 — SSH foundation
- 3.1 Android: SSH library + lifecycle + password/key auth + host-key verification before credentials + known-hosts/TOFU + key-change warnings + local sshd fixture tests.
- 3.2 Windows: SSH.NET ≥ 2026.0.0, same requirements + fixture tests.
- 3.3 Host manager (CRUD, groups/tags/search, import/export secrets-excluded) on both platforms.

### Step 4 — Terminal and daily workflow (Free)
- 4.1 Android terminal integration (PTY, resize, ANSI/VT, Unicode, scrollback, copy/paste, extra-key toolbar) + tabs/basic splits.
- 4.2 Windows VT renderer (libvterm/VtNetCore over WinUI/Skia) + shell channel + tabs/resizable splits + keyboard-first UX.
- 4.3 Themes/colour customization on both platforms (≥30 themes, editor, colour wheel, HEX/RGB/HSL, ANSI-16, 256/true colour, per-host, import/export, live preview).
- 4.4 File attachment / editable path insertion (native pickers, safe escaping, no auto-execute, local-vs-remote clarity, upload-to-remote).
- 4.5 Command history (≥10 recent) + snippets (copy-only).

### Step 5 — SFTP and tunnels (Free)
- 5.1 SFTP basic on both platforms (SFTP not SCP; progress, cancel, retry, confirmations, partial-transfer safety).
- 5.2 SSH tunnels (local/remote/dynamic SOCKS) with validation and session-tied lifecycle.

### Step 6 — Credential vault (Free) and advanced SSH security (Unassigned)
- 6.1 Local vault on both platforms (Keystore / DPAPI-Credential Locker), key gen/import, fingerprints, optional biometric/Hello, re-auth before export. **Requires 1.3.**
- 6.2 Feasibility review for SSH certificates, FIDO2/security keys, agent forwarding; then tier assignment.

### Step 7 — Premium productivity
- 7.1 Workspace presets/session restoration, multi-host execution, advanced autocomplete — after entitlement design; only if genuinely implemented and tested.

### Step 8 — Premium sync, team and collaboration
- 8.1 Sync key hierarchy/recovery/rotation/revocation design + threat model.
- 8.2 Optional encrypted multi-device sync (client-side AEAD; device lifecycle; conflict handling; quotas; deletion). Cloudflare R2/Workers only after explicit cost/resource review.
- 8.3 Team vaults/roles/permissions/collaboration/audit with a real server-side authorization model.
- 8.4 Advanced SFTP queue/host-to-host transfer.

### Step 9 — Encrypted-source hardening (optional parallel track; must not gate Steps 2–8)
- 9.1 Streaming AEAD bundle format + strict authenticated manifest/parser (independently reviewed).
- 9.2 DEK wrapping + key custody lifecycle (generation, storage, offline recovery, rotation, revocation, destruction) with rehearsals.
- 9.3 Safe archive validator/extractor with traversal/symlink/duplicate/bomb defences + adversarial fixtures.
- 9.4 Hash-locked dependencies; protected release authorization (immutable SHA binding, protected environment, fork isolation, ephemeral runner, cleanup) with negative tests.
- 9.5 Complete the go/no-go gates in `ENCRYPTED_SOURCE_REVIEW.md` §7; independent review; explicit owner approval before admitting source or enabling decryption.

### Step 10 — Release readiness
- 10.1 Compatibility matrix, dependency/security audit, accessibility/performance/usability testing.
- 10.2 Signed builds, privacy policy, support docs, Play/Store/website listing verification.
- 10.3 Pilot release before commercial rollout. **No public GitHub binary releases.**

---

## 4. Verification per step

| Step | Primary verification |
|---|---|
| 0 | Protection enabled; secret-free CI green; docs reconciled; no PR merged |
| 1 | Contracts reviewed; threat model approved |
| 2 | Both skeletons build in CI with no secrets |
| 3 | Host-key-before-credentials proven; key-change rejected; fixture tests pass on both platforms |
| 4 | ANSI/VT, Unicode, resize, themes render correctly; attachment never auto-executes; history copy-only |
| 5 | Transfer cancel/retry/partial-safety verified; tunnel lifecycle bound to session |
| 6 | Vault never stores plaintext; re-auth before export; fingerprints correct |
| 7–8 | Entitlement enforced server-side; sync crypto round-trip + recovery + revocation drills |
| 9 | All §7 gates evidenced; no plaintext source in Git/logs/artefacts |
| 10 | Signed artefact, correct package identity, verified distribution path |

---

## 5. First actions after owner approval (no code)

1. Record the owner's decisions from `AUDIT_REPORT.md` §9.3 in `docs/DECISIONS.md`.
2. Reconcile the three branches' documentation into one coherent set (without merging PR #1/#2).
3. Add the `LICENSE` file and fix the repository description.
4. Enable `main` branch protection and add secret-free CI + secret scanning.
5. Then, and only then, begin Step 2 (platform skeletons).

**No implementation step will start until the owner reviews the audit report and approves this plan.**
