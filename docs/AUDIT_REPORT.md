# RSS Netrix — Initial Repository and Requirements Audit

**Report type:** Read-only engineering audit and implementation plan
**Auditor:** OpenHands agent (autonomous engineering handover)
**Date:** 2026-11-10
**Repository:** `riyazamra1/RSS-Netrix` (public)
**Audited commit:** `260d115` (`main`, "docs: add product foundation, architecture and security baseline", 2026-11-07)
**Scope note:** No application code was modified, no pull request was merged, no branch was pushed, no secret, account, paid resource or binary was created. All findings are evidence-based from the repository, its branches, and public dependency registries.

---

## 1. Verified current repository status

### 1.1 Repository facts (verified via GitHub API)

| Property | Value |
|---|---|
| Full name | `riyazamra1/RSS-Netrix` |
| Visibility | **Public** |
| Default branch | `main` |
| Licence | **None declared** (no `LICENSE` file, no SPDX licence) |
| Description | "RSS Netrix is a clone of Termius" |
| Created | 2026-11-06 |
| Last push | 2026-11-10 |
| Repository size | 101 KB |
| Releases | **0** |
| Open issues | 0 (the 2 entries returned are the two pull requests) |
| Branch protection | Not readable with the current token (403) — **status unverified** |
| Issues / Wiki enabled | Yes / Yes |

### 1.2 Branches (verified)

| Branch | Head | State |
|---|---|---|
| `main` | `260d115` | Foundation documentation only |
| `feat/source-bundle-prototype` | `f361b3a` | PR #1 head (draft, open) |
| `docs/termius-feature-parity` | `b3cbb1b` | PR #2 head (draft, open) |
| `docs/encrypted-source-build-design` | `018463b` | **Not in any pull request** |

### 1.3 Contents of `main` (verified, 8 files)

```
.gitignore
README.md
SECURITY.md
docs/ARCHITECTURE.md
docs/DECISIONS.md
docs/PRODUCT_SPEC.md
docs/ROADMAP.md
docs/SECURITY.md
```

There is **no application source, no Android project, no Windows project, no CI workflow and no build file on `main`**. The commit history is a single, grafted (shallow) commit. No tags, no release assets, no large or binary blobs in history, and no secret-like literals in tracked files.

### 1.4 GitHub Actions (verified)

| Workflow | Location | State | Runs |
|---|---|---|---|
| Source bundle prototype tests | `.github/workflows/source-prototype-tests.yml` (only on `feat/source-bundle-prototype`) | active | 2 runs, both `completed/success`, both on 2026-11-07 |

`main` has **no workflows**. The prototype workflow is secret-free, uses `permissions: contents: read`, and pins actions by full commit SHA (`actions/checkout@11bd7190…` v4.2.2, `actions/setup-python@a26af69b…` v5.6.0). It triggers on `push`/`pull_request` scoped to the tool, tests and requirements paths, plus `workflow_dispatch`.

### 1.5 Working tree

`git status` on `main` is clean. All three remote branches were fetched locally for inspection only; no local commits or pushes were made.

---

## 2. Existing work and outstanding requirements

### 2.1 What exists today

**On `main` — an approved documentation baseline:**
- `README.md` — product identity, platforms, 7 security principles, $0/month cost target, delivery principles.
- `docs/PRODUCT_SPEC.md` — identity, platform choices, functional requirements 3.1–3.8, UX/accessibility, security/privacy, commercial direction, acceptance baseline.
- `docs/ARCHITECTURE.md` — architectural goals, proposed stacks, 6 logical modules, data boundaries, connection lifecycle state machine, terminal design, build/source protection, deployment.
- `docs/SECURITY.md` — assets, threats, required controls (SSH transport, local secret storage, encrypted sync, repository/CI), open key-management decisions, limitations, release gate.
- `docs/ROADMAP.md` — Phases 0–7 with checkboxes and delivery gates.
- `docs/DECISIONS.md` — ADR-001 … ADR-008.

**On unmerged branches — proposed but not approved into `main`:**
- PR #1 (`feat/source-bundle-prototype`): the encrypted-source prototype (`tools/source_bundle.py`), tests (`tests/test_source_bundle.py`), `requirements-source-prototype.txt` (`cryptography>=44,<47`), the secret-free CI workflow, and docs (`SOURCE_BUNDLE_PROTOTYPE.md`, `SOURCE_PROTECTION.md`, `BUILD_PIPELINE.md`) plus edits to `ARCHITECTURE.md`, `SECURITY.md`, `ROADMAP.md`, `DECISIONS.md`.
- PR #2 (`docs/termius-feature-parity`): `docs/FEATURE_PARITY_SPEC.md` (the comprehensive feature scope and the **owner-approved Free/Premium placement**), plus edits to `README.md`, `ARCHITECTURE.md`, `DECISIONS.md` (ADR-009 Free/Premium), `PRODUCT_SPEC.md`, `ROADMAP.md`.
- `docs/encrypted-source-build-design` (**no PR**): `docs/ENCRYPTED_SOURCE_REVIEW.md` (the security review), plus `SOURCE_PROTECTION.md`, `BUILD_PIPELINE.md` and further edits to `ARCHITECTURE.md`, `SECURITY.md`, `ROADMAP.md`, `DECISIONS.md` (ADR-009 encrypted source bundle, ADR-010 single-public-repo trusted build, ADR-011 Free/Premium + distribution).

### 2.2 Approved decisions (as recorded)

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | Product name `RSS Netrix`; Android app ID `com.riyaz.rssnetrix`; original RSS branding/assets | Accepted |
| ADR-002 | Native Android (Kotlin/Compose) and native Windows (candidate .NET + WinUI 3) | Accepted direction; Windows framework gated on library/packaging review |
| ADR-003 | Independent SSH implementation from documented standards; no copying proprietary code/assets | Accepted |
| ADR-004 | Local-first credentials via platform-protected storage; no mandatory RSS Core/cloud dependency | Accepted |
| ADR-005 | Optional client-side-encrypted cloud sync; Cloudflare R2/Workers as $0 candidate | Proposed; deferred |
| ADR-006 | Public repo with encrypted-at-rest application source; no plaintext app source until trusted workflow reviewed | Accepted constraint; deferred |
| ADR-007 | $0/month target; no paid resources without approval | Accepted |
| ADR-008 | Delivery discipline (requirements first, review change list, one deployment at a time, verify real artifacts) | Accepted |
| ADR-009 (PR #2) | Free/Premium **feature placement** approved for planning | Accepted for planning |
| ADR-009/010/011 (design branch) | Encrypted source bundle + key separation; single-public-repo trusted build; Free/Premium + official distribution | Proposed / Accepted (branch only) |

**Free tier (approved placement, must remain free):** direct SSH + local host profiles; password/key auth with host-key verification; local encrypted credential vault; interactive terminal; tabs + basic split panes; **all terminal themes and custom colour controls**; file attachment/path insertion; basic SFTP; basic local/remote/dynamic tunnels; basic command history + snippets; basic host import/export.

**Premium (approved placement):** advanced workspace presets/session restoration; advanced productivity (multi-host snippet execution, advanced autocomplete); advanced SFTP (queue features, host-to-host); encrypted multi-device sync; team workspaces/shared vaults; live terminal collaboration/handoff; team audit/administration.

**Unassigned (pending feasibility review):** Telnet, Mosh, serial and other protocols; SSH certificates, FIDO2/security keys and advanced auth.

### 2.3 Outstanding requirements / unresolved questions

From `ROADMAP.md` Phase 0 and `SECURITY.md` §4, plus gaps found in this audit:

1. **Dependency selection** for SSH/SFTP/terminal on both platforms has not been made (this report proposes candidates).
2. **Encrypted-source build design** has been documented and prototyped but is **not approved**; application source admission is **blocked**.
3. **Key-management decisions still open:** source vs sync key separation (recommendation: yes); key derivation/wrapping/recovery/rotation/revocation formats; whether a Worker can authorize decryption without returning a long-lived master key; build identity and short-lived authorization; incident response.
4. **UX requirements** (original RSS design system, navigation, theme set) not yet specified.
5. **Credential recovery** model not yet specified.
6. **Release/packaging** approach (Play/Store/website, signing, update channel) not yet specified.
7. **No licence file** in a public repository (affects reuse and legal clarity).
8. **No branch protection or CI on `main`** (release/supply-chain risk).
9. **`docs/encrypted-source-build-design` has no pull request** — its content (including the security review) is not visible through the PR process and risks being lost.
10. **Prototype dependency is a loose version range** (`cryptography>=44,<47`), not hash-locked; the installed `cryptography` on this machine is 50.0.2, outside that range (range should be re-validated when the prototype is revived).
11. **Overlapping edits:** PR #1, PR #2 and the design branch all edit `ARCHITECTURE.md`, `SECURITY.md`, `ROADMAP.md` and `DECISIONS.md` differently; ADR-009 is used with different meanings on two branches. Merging more than one as-is will conflict.

---

## 3. Encrypted-source prototype and its security review

### 3.1 What the prototype does

`tools/source_bundle.py` (PR #1) is a one-shot file wrapper around an **already-created** archive:

- AES-256-GCM authenticated encryption with a fresh random 256-bit DEK per bundle.
- A 256-bit KEK supplied out-of-band via env var `RSS_SOURCE_KEK` (base64, exactly 32 bytes) wraps the DEK with AES-GCM using a separate 96-bit nonce.
- A canonical-JSON header (version, algorithm, key id, payload nonce, wrap nonce, wrapped DEK) is authenticated as associated data; a magic prefix and big-endian header length frame the bundle.
- Bounds: 512 MiB input, 16 KiB header, strict key-id pattern, strict field set/length validation, `--force`-gated atomic replace, and no extraction.

`tests/test_source_bundle.py` covers round-trip, wrong key, ciphertext tampering, header (AAD) tampering, no-overwrite, and invalid key length. CI is secret-free and SHA-pinned.

### 3.2 Security review verdict (`docs/ENCRYPTED_SOURCE_REVIEW.md`)

The review is **excellent and correctly conservative**. It concludes the prototype is "a useful experimental authenticated-encryption proof of concept" whose "passing prototype tests do not establish production readiness", and it **blocks** application source admission and any privileged decryption workflow until explicit go/no-go gates pass. Its ten findings (SRC-01…SRC-10) are accurate. My independent assessment agrees with the verdict and adds these notes:

- **SRC-02/SRC-03 (key custody / DEK wrap):** using raw AES-GCM to wrap a DEK under a long-lived KEK is acceptable only with a rigorously managed nonce strategy; the review's preference for a dedicated key-wrap construction (e.g. AES-KW / RFC 3394) or a reviewed per-key nonce registry is the right call.
- **SRC-04 (canonical header):** the prototype computes AAD from a *re-serialised* header. If a decoder ever re-serialised differently from the encoder, AAD would diverge. The review's "enforce one canonical encoding, reject duplicate keys/unknown fields" requirement closes this. Python's `json` accepts duplicate keys (last wins) — a real hardening item.
- **SRC-05/SRC-06 (archive + filesystem boundary):** the prototype deliberately does not extract, so the highest-risk surface (path traversal, symlink escape, zip bombs) is *not yet written* — and must be treated as a first-class, separately reviewed component.
- **SRC-08 (dependency pinning):** `cryptography>=44,<47` is not hash-locked; must become a fully pinned, hash-verified lockfile.
- **SRC-10 (release authorization):** the current CI is genuinely secret-free and read-only. The protected release path does not exist and must not exist until reviewed.
- **Overarching caveat (correctly stated):** encryption at rest protects the *repository*, not released binaries. Any public APK/EXE can be inspected. Source encryption must never be presented as copy-protection.

### 3.3 Honest limits of the approach

The design (ADR-006/ADR-010) is coherent, but the owner should understand its real cost/benefit before committing:

- It **does not** prevent a determined party from reverse-engineering a shipped binary.
- It **does** add permanent operational overhead: every build needs an authorized, approved, ephemeral decryption step; every developer needs the KEK out-of-band; incident handling for key loss is severe (lost KEK ⇒ unrecoverable source).
- It **cannot** stop malicious privileged build code or a compromised dependency from exfiltrating plaintext while it is decrypted.
- A **public release binary** plus a **public repository** still reveals a great deal. If the true goal is commercial protection, the more effective levers are server-side Premium enforcement (already planned) and licensing — not source encryption.

The audit therefore recommends: keep the prototype and review as-is (unmerged), and **treat encrypted-source as an optional hardening track that runs in parallel with platform skeletons**, not as a hard gate that stalls all implementation. A clearly marked private repository is a simpler alternative if the owner's priority is confidentiality over "single public repository". This is an owner decision (see §9).

---

## 4. Architecture and dependency recommendations

### 4.1 Cross-cutting architecture (consistent with existing docs)

Keep the module split already approved in `ARCHITECTURE.md`: **Presentation → Application services → Protocol adapters → Security → Persistence → (later) Sync/collaboration**. Define platform-neutral contracts (connection lifecycle state machine, host profile model, transfer model, trust-store interface, vault interface) as versioned specifications that both platforms implement, so behaviour and security invariants stay aligned without sharing UI code.

The connection lifecycle `Created → Resolving → Connecting → HostKeyVerification → Authenticating → Ready → Reconnecting/Closing → Closed/Failed` is sound; host-key verification must complete **before** any credential is transmitted, and reconnect must never silently accept a changed host key.

### 4.2 Android dependency recommendation

**Recommended primary SSH/SFTP library: `org.connectbot.sshlib:sshlib` (ConnectBot "cbssh").**

| Attribute | Evidence |
|---|---|
| Licence | Apache-2.0 (POM `<licenses>`; repo `connectbot/cbssh` Apache-2.0) |
| Maintenance | Active — repo pushed 2026-11-08; Maven Central releases through `0.6.7` (lastUpdated 2026-11-02) |
| Android-native | Kotlin, coroutines, Kaitai-Struct protocol parsing, KStateMachine; built by the ConnectBot maintainers specifically for Android |
| Features | SSH client, interactive shells with PTY, command exec, **SFTP v3**, **local/remote/dynamic (SOCKS5) forwarding**, **agent forwarding**, host-key algorithms (RFCs 4250–4256, 4419, 5656, 8308, 8709, 8731, 9142) |
| Supply chain | CI with SLSA v1 Build Level 3 badge, SonarCloud quality gate |

**Alternative: `com.hierynomus:sshj` (Apache-2.0).** Mature and widely used (≈2.7k stars, pushed 2026-10-12, latest `0.40.0`). It is a strong JVM library with SFTP and forwarding, but it is not Android-first; it relies on BouncyCastle and needs Android-specific testing/trimming. Use only if sshlib proves insufficient.

**Alternative: Apache MINA SSHD (`org.apache.sshd`, Apache-2.0).** Very actively developed (`2.18.0` stable, `3.0.0-M4`; pushed 2026-11-10) and comprehensive, but heavier, has a history of advisories (including a 2022 **critical** deserialization issue and 2021/2023 issues), and is not Android-oriented. Not recommended as the Android default.

**Fallback: `com.github.mwiede:jsch` (BSD-style).** The maintained fork of JSch; small, embeddable, active (`2.28.8`, 2026-10-10). It has **no GitHub security advisories recorded**, is small enough to run on Android, and is the lowest-risk choice if the higher-level libraries cause trouble. Trade-off: lower-level API and less Android ergonomics.

**Terminal emulator (Android) — recommended: `org.connectbot:termlib` (Apache-2.0) or Termux `terminal-emulator`/`terminal-view` (Apache-2.0).**

- `connectbot/termlib` is a **Jetpack Compose** terminal component (Kotlin + C++ via JNI over **libvterm**, MIT), with 256-colour/true-colour, double-width and combining characters, selection, scrolling, resize, multiple fonts, and iTerm2/Kitty inline images. It is actively maintained (pushed 2026-11-10) and matches the Compose stack. It is the best fit.
- Termux `terminal-emulator` + `terminal-view` are Apache-2.0 (the *app* is GPLv3, but the two library modules are Apache-2.0 per `LICENSE.md`). They are battle-tested but View-based (not Compose) and are **not published to Maven Central** (they are built from source / JitPack); pulling them in means vendoring or a JitPack dependency. Prefer termlib; keep Termux modules as a fallback.

**Crypto/support:** prefer Android platform crypto (Keystore, `javax.crypto`) for local secrets. If a JCE provider is required, use BouncyCastle (`bcprov-jdk18on`, MIT) — note its advisories are all `medium` and current (1.80); pin and monitor. Do **not** use `androidx.security:security-crypto` as the vault backbone without review — 1.1.0 is the current release (2025-07-30) but the API has a history of alpha/beta churn; Keystore + a reviewed envelope design is more durable.

### 4.3 Windows dependency recommendation

**Recommended SSH/SFTP library: `SSH.NET` (`Renci.SshNet`, MIT).**

| Attribute | Evidence |
|---|---|
| Licence | MIT |
| Maintenance | Active — repo pushed 2026-11-03; NuGet `2026.0.0` |
| Features | SSH-2, **interactive shell/terminal**, **SFTP (sync + async)**, **remote, dynamic and local port forwarding**, configurable host-key/MAC/compression algorithm lists |
| Targets | .NET Standard 2.0 and **.NET 8+** (compatible with .NET 10) |

**Security note (important):** two **high**-severity advisories affect `ScpClient` path handling (arbitrary file write / server-side RCE via server-controlled SCP filenames) — patched in **`2026.0.0`**. **Pin ≥ `2026.0.0`.** These affect SCP specifically; RSS Netrix should prefer SFTP over SCP regardless. The library exposes host-key callbacks (`HostKeyReceived`/`CanTrust`) which satisfy the "verify before credentials" requirement.

**UI framework: WinUI 3 via `Microsoft.WindowsAppSDK` (MIT), targeting .NET 10 (LTS).** .NET 10 is current LTS (`10.0.14`, 2026-11-10). `Microsoft.WindowsAppSDK` latest stable is `2.6.5`. This matches ADR-002's candidate. Confirm minimum supported Windows version (Windows App SDK requires Windows 10 1809+) during Phase 1.

**Terminal emulator (Windows):** there is **no first-party, redistributable, supported NuGet control** for the Windows Terminal renderer (`Microsoft.Terminal.Control` / `Microsoft.Terminal.Wpf` are not on NuGet). Options:
- **Recommended: implement a VT renderer** over a proven emulation core. Use **libvterm** (MIT) or **VtNetCore** (MIT) for emulation and render with WinUI/Skia; this gives full control and matches the "renderer, not a shell" architecture.
- Third-party packages exist (`CI.Microsoft.Terminal.Wpf`, `WindowsTerminal.WinUI3.Control`) but are unofficial re-packagings with small download counts and no vendor support — not suitable for a security-sensitive client without review.
- **Terminal.Gui** (TUI framework) and **XtermSharp** (MIT, last pushed 2022) are not appropriate as the primary renderer.

### 4.4 Dependency summary table

| Layer | Android (recommended) | Windows (recommended) | Licence | Notes |
|---|---|---|---|---|
| SSH/SFTP/tunnels | `org.connectbot.sshlib:sshlib` | `SSH.NET` ≥ `2026.0.0` | Apache-2.0 / MIT | Android alt: sshj / mwiede-jsch |
| Terminal emulator | `org.connectbot:termlib` (Compose, libvterm) | Custom VT renderer over libvterm/VtNetCore | Apache-2.0 / MIT | Termux modules Apache-2.0 fallback |
| UI | Jetpack Compose + Material 3 | WinUI 3 (`Microsoft.WindowsAppSDK`) on .NET 10 | Apache-2.0 / MIT | No WebView shell |
| Local secret protection | Android Keystore + reviewed envelope | DPAPI / Credential Locker | Platform | No plaintext config |
| Crypto provider | Platform JCE; BouncyCastle if needed | .NET `System.Security.Cryptography` | MIT | Pin and monitor BC advisories |
| Source-bundle tooling | Python `cryptography` (pinned, hash-locked) | n/a | Apache-2.0/BSD | Prototype only; not approved |

**Licence/maintenance/security summary:** all primary recommendations are permissively licensed (Apache-2.0/MIT/BSD), actively maintained (pushes within days of this audit), and free of unpatched advisories at the recommended versions. The only material advisory risk is SSH.NET's SCP handling, mitigated by pinning ≥ `2026.0.0` and using SFTP.

---

## 5. Security gaps

| ID | Gap | Severity | Recommendation |
|---|---|---|---|
| G-01 | No `LICENSE` file in a public repository | Medium | Owner adds an explicit licence (or "all rights reserved") before any code is added |
| G-02 | No branch protection / required review on `main` (unverified; API returned 403) | High | Enable protected branch, required reviews, required status checks, disallow force-push; verify from an admin account |
| G-03 | No CI on `main` | Medium | Add a secret-free documentation/test workflow with `permissions: contents: read` and SHA-pinned actions |
| G-04 | Encrypted-source review sits on a branch **with no PR** | Medium | Open a draft PR (or otherwise track) so the review is discoverable and not lost; do **not** merge per instructions |
| G-05 | Prototype dependency not hash-locked; range excludes the installed `cryptography` | Medium | Pin exact version(s) with hashes; re-validate range when the prototype is revived |
| G-06 | No threat-model artefact beyond `docs/SECURITY.md` prose | Medium | Produce a structured threat model before Phase 5 (vault) and Phase 7 (sync) |
| G-07 | No secret-scanning / dependency-scanning in CI | Medium | Add secret scanning (e.g. GitHub secret scanning + push protection) and a dependency review workflow |
| G-08 | Open key-management questions (§2.3 item 3) | High (for sync/source) | Resolve before enabling sync or source decryption; document key hierarchy, rotation, recovery, revocation |
| G-09 | Overlapping doc edits across three branches; ADR-009 collision | Low | Reconcile in a single documentation PR before merging anything |
| G-10 | Repo description says "clone of Termius" | Low (brand/legal) | Change to an original-product description; ADR-003 forbids copying, and the wording invites trademark concern |
| G-11 | No dependency/licence audit policy yet | Medium | Adopt "permissive-only + maintained + no known unpatched advisories" gate; record in `DECISIONS.md` |
| G-12 | Prototype test workflow only runs on the prototype branch | Low | Acceptable now; formalise CI expectations in Phase 1 |

---

## 6. Android implementation phases

**Phase A0 — Project skeleton (Free).** Create the Gradle project with application ID **`com.riyaz.rssnetrix`** (unchanged), Kotlin + Compose + Material 3, `minSdk`/`targetSdk` chosen to satisfy the Google Play requirement (**target API 36 / Android 16 for submissions from 2026-08-31**), module boundaries mirroring the approved architecture, and a secret-free CI build. No secrets.

**Phase A1 — Host manager (Free).** Host profile CRUD, groups/tags, search, import/export with secrets excluded by default. Persistence for non-secret metadata (Room or DataStore).

**Phase A2 — SSH foundation (Free).** Integrate the selected SSH library; implement the connection lifecycle; password and key authentication; **host-key verification before credentials**; known-hosts trust store with explicit trust-on-first-use and prominent key-change warnings. Tests against local disposable SSH fixtures.

**Phase A3 — Interactive terminal (Free).** Integrate the terminal emulator component; PTY allocation, resize, ANSI/VT, Unicode, scrollback, selection, copy/paste, Android extra-key toolbar; multi-session tabs and basic split panes.

**Phase A4 — Terminal themes and customization (Free).** ≥30 built-in themes, custom editor, colour wheel, HEX/RGB/HSL, ANSI-16 palette, bold/bright, 256-colour and true-colour; per-host theme; import/export; live preview against the real renderer. **Must remain Free.**

**Phase A5 — File attachment / path insertion (Free).** Storage Access Framework picker beside the terminal toolbar; insert the local path (quoted/escaped), editable and never auto-executed; clearly distinguish local vs remote paths; handle content-URI providers safely; offer explicit upload-to-remote.

**Phase A6 — Command history and snippets (Free).** Searchable per-host/session history, minimum 10 recent commands, snippets with names/descriptions/categories; tap to **copy**, never auto-execute.

**Phase A7 — SFTP (Free basic).** Browse, metadata, upload/download, create/rename/move/delete, progress, cancellation, retry, destructive-action confirmation, partial-transfer safety.

**Phase A8 — SSH tunnels (Free basic).** Local, remote and dynamic SOCKS forwarding; state display; port/bind validation; lifecycle tied to the owning session.

**Phase A9 — Local credential vault (Free).** Keystore-backed storage, key generation/import, passphrases, fingerprints, optional biometric/device-credential gating, re-auth before export. **Threat model required first.**

**Phase A10 — Advanced SSH security (Unassigned → review).** SSH certificates, FIDO2/security keys, agent forwarding — feasibility review before any tier assignment.

**Phase A11 — Premium productivity.** Workspace presets/session restoration, multi-host snippet execution, advanced autocomplete — **only after server-side entitlement design**.

**Phase A12 — Premium SFTP / sync / team.** Advanced transfer queue and host-to-host transfer; encrypted multi-device sync; team vaults/collaboration/audit. Requires the sync key hierarchy, recovery, rotation, revocation and server-side authorization designs.

**Phase A13 — Release readiness.** Compatibility matrix, dependency/security audit, accessibility, signed release (Play / official website only), privacy policy. **No public GitHub binary releases.**

---

## 7. Windows implementation phases

**Phase W0 — Project skeleton.** .NET 10 (LTS) + WinUI 3 solution, display name **`RSS Netrix`**, module boundaries mirroring Android, secret-free CI build (Windows runner).

**Phase W1 — Host manager (Free).** Same model/contracts as Android; persistence for non-secret metadata; import/export with secrets excluded.

**Phase W2 — SSH foundation (Free).** Integrate `SSH.NET ≥ 2026.0.0`; connection lifecycle; password/key auth; host-key verification before credentials; known-hosts store with TOFU and key-change warnings. Tests against local disposable SSH fixtures.

**Phase W3 — Interactive terminal (Free).** Implement the VT renderer over the chosen emulation core; PTY/shell channel, resize, ANSI/VT, Unicode, scrollback, selection, clipboard; multi-tab and resizable split panes; keyboard-first shortcuts; avoid spurious resize on tab switch.

**Phase W4 — Terminal themes and customization (Free).** Same ≥30 themes and colour controls as Android; per-host themes; import/export; live preview. **Must remain Free.**

**Phase W5 — File attachment / path insertion (Free).** Native file picker, drag-and-drop, clipboard; insert local path (quoted/escaped) editable and never auto-executed; distinguish local vs remote; explicit upload-to-remote.

**Phase W6 — Command history and snippets (Free).** As Android, with keyboard navigation.

**Phase W7 — SFTP (Free basic).** SFTP browser and transfer lifecycle (**prefer SFTP over SCP** to avoid the patched SCP advisories), confirmations, cancellation, retry, partial-transfer safety.

**Phase W8 — SSH tunnels (Free basic).** Local/remote/dynamic forwarding with state and validation, tied to the owning session.

**Phase W9 — Local credential vault (Free).** DPAPI/Credential Locker-backed storage; optional Windows Hello where supported; re-auth before export. **Threat model required first.**

**Phase W10 — Advanced SSH security (Unassigned → review).** SSH certificates, FIDO2/security keys, agent forwarding.

**Phase W11 — Premium productivity.** Workspace presets/session restoration, multi-host execution, advanced autocomplete.

**Phase W12 — Premium SFTP / sync / team.** Advanced transfer features and encrypted sync/team services (shared design with Android).

**Phase W13 — Release readiness.** Compatibility matrix, dependency/security audit, accessibility, MSIX/installer signing, distribution via Microsoft Store / official website only.

---

## 8. Testing and release strategy

### 8.1 Testing

- **Unit tests** per module: models, lifecycle state machine, trust-store decisions, vault envelope crypto, path escaping, transfer state machine.
- **Integration tests** against **local disposable SSH/SFTP fixtures** (e.g. an ephemeral `sshd`/SFTP container started per test run) — real protocol paths, not mocks.
- **Security tests (negative-first):** host-key mismatch/change rejection; credential never sent before verification; wrong-key/AAD/truncation rejection for any envelope; archive traversal/symlink/bomb tests when an extractor exists; secret redaction in logs; untrusted-PR workflow cannot reach secrets.
- **Failure-path tests:** cancellation, disconnect mid-transfer, disk-full, permission denied, reconnect after key change.
- **Platform tests:** Android instrumentation on phone + tablet; Windows UI/keyboard/DPI on supported Windows versions.
- **Acceptance gate (from `FEATURE_PARITY_SPEC.md` §14):** real operation works; tests cover normal/error/cancel/security paths; both platforms pass; no secret leakage; accessibility/responsive checks; documentation accurate; signed artefact verified.
- **CI:** secret-free public workflows only; SHA-pinned actions; `permissions: contents: read`; secret scanning + dependency review. The privileged release path is designed but **not enabled** until reviewed.

### 8.2 Release

- **Distribution:** Android via official RSS website and/or Google Play; Windows via official RSS website and/or Microsoft Store. **GitHub is not a customer download channel** — no public APK/EXE/MSIX/installer release assets.
- **Signing:** separate Android and Windows signing identities; never reuse source-encryption or sync keys; verify signing identity and package ID (`com.riyaz.rssnetrix`) at release.
- **Premium enforcement:** server-side licence validation + device activation/revocation; never trust a client-side flag.
- **Cadence:** one build/deployment at a time; report commit SHA, exact build/test statuses and artefact verification; never infer success from a queued workflow.
- **Pilot:** internal/pilot release before commercial rollout.
- **Cost:** stay at $0/month; no paid runner/storage/signing/cloud resource without explicit owner approval.

---

## 9. Risks, blockers and owner-only decisions

### 9.1 Risks

| Risk | Impact | Mitigation |
|---|---|---|
| SSH.NET SCP advisories (high) if misused | Arbitrary file write / RCE | Pin ≥ `2026.0.0`; prefer SFTP; avoid SCP paths |
| Terminal emulator integration cost on Windows (no first-party control) | Schedule risk | Budget a renderer task; use libvterm/VtNetCore |
| Encrypted-source operational burden and key-loss risk | Build friction; irreversible loss | Treat as optional parallel track; keep offline recovery copy; rehearse recovery |
| Public repo + reverse-engineerable binaries | IP exposure | Server-side Premium enforcement; accept binary-analysis reality |
| No branch protection / no CI on `main` | Supply-chain compromise | Enable protection + secret-free CI + secret scanning |
| Overlapping branch edits / ADR-009 collision | Merge conflicts, lost work | Reconcile docs in one PR before merging anything |
| "clone of Termius" repo description | Brand/legal risk | Reword to original-product description |
| Loose prototype dependency pin | Reproducibility | Hash-locked lockfile |

### 9.2 Blockers (per the repo's own gates)

- **Application source admission is blocked** until the encrypted-source go/no-go gates in `ENCRYPTED_SOURCE_REVIEW.md` §7 pass **or** the owner approves the alternative repository model.
- **Premium sync/collaboration** is blocked on the key hierarchy, recovery, rotation, revocation and server-side authorization design.
- **Premium charging** is blocked on a reviewed licensing/authorization design (client flags are insufficient).

### 9.3 Owner-only decisions

1. **Repository model:** single public repo with encrypted-at-rest source (as designed) **vs** a private repository for source. (Trade-off in §3.3.)
2. **Licence:** choose a licence (or explicit "all rights reserved") for a public repo.
3. **Encrypted-source priority:** hard gate that blocks implementation, or optional parallel hardening track? (Audit recommends parallel.)
4. **Dependency selection:** confirm the recommended SSH/SFTP/terminal libraries (§4.2–4.3) before coding.
5. **Windows UI framework confirmation:** .NET 10 + WinUI 3, and minimum supported Windows version.
6. **Key management:** approve key hierarchy, wrapping, recovery, rotation, revocation formats; confirm source/sync/signing key separation.
7. **Commercial parameters:** prices, trial, renewals, device limits, payment provider, licence enforcement — **explicitly out of scope** of the approved feature placement.
8. **Distribution channels:** Play/Store/website readiness and timing.
9. **Android `minSdk`:** device-support floor vs library constraints.
10. **Whether to open a PR for `docs/encrypted-source-build-design`** so the review is tracked (without merging).

---

## 10. Dependency-ordered development backlog

Items are ordered by dependency. **[Free]/[Premium]/[Unassigned]** show tier. Every item is subject to the delivery gates in `ROADMAP.md`.

**Track 0 — Governance and repository hygiene (do first; unblocks everything)**
1. Resolve owner-only decisions in §9.3 (repository model, licence, dependency confirmation, key management).
2. Reconcile the overlapping doc edits from PR #1, PR #2 and the design branch into one coherent documentation set; resolve the ADR-009 collision; add ADRs for dependency selection and licence. **(Do not merge PR #1 or PR #2.)**
3. Open a draft PR (or equivalent tracking) for `docs/encrypted-source-build-design` so the security review is preserved. **(No merge.)**
4. Enable `main` branch protection: required reviews, required status checks, no force-push.
5. Add a secret-free documentation/test CI workflow with SHA-pinned actions and `permissions: contents: read`; enable secret scanning + push protection and dependency review.
6. Add a `LICENSE` file (owner decision) and fix the repo description.
7. Adopt and document a dependency/licence/security policy (permissive-only, maintained, no unpatched advisories) in `DECISIONS.md`.

**Track 1 — Foundation specifications (before code)**
8. Freeze platform-neutral contracts: host profile model, connection lifecycle state machine, trust-store interface, vault interface, transfer model, error taxonomy.
9. Specify the original RSS design system (tokens, typography, component inventory) for both platforms.
10. Specify the credential vault envelope and platform-protection design; write the vault threat model.
11. Specify the credential recovery model (owner-visible).

**Track 2 — Platform skeletons**
12. [Free] Android project skeleton (Kotlin/Compose/Material 3), app ID `com.riyaz.rssnetrix`, Play-compliant target API, module boundaries, secret-free CI. *(Phase A0)*
13. [Free] Windows project skeleton (.NET 10 + WinUI 3), module boundaries, secret-free CI. *(Phase W0)*

**Track 3 — SSH foundation**
14. [Free] Android: SSH library integration + lifecycle + password/key auth + host-key verification + known-hosts/TOFU + key-change warnings + fixture tests. *(A2)*
15. [Free] Windows: `SSH.NET ≥ 2026.0.0` integration, same requirements + fixture tests. *(W2)*
16. [Free] Host manager on both platforms (CRUD, groups/tags/search, import/export secrets-excluded). *(A1, W1)*

**Track 4 — Terminal and daily workflow**
17. [Free] Android terminal integration (PTY, resize, ANSI/VT, Unicode, scrollback, copy/paste, extra-key toolbar) + tabs/basic splits. *(A3)*
18. [Free] Windows VT renderer (libvterm/VtNetCore over WinUI/Skia) + shell channel + tabs/resizable splits + keyboard-first UX. *(W3)*
19. [Free] Terminal themes and colour customization on both platforms (≥30 themes, editor, colour wheel, HEX/RGB/HSL, ANSI-16, 256/true colour, per-host, import/export, live preview). *(A4, W4)*
20. [Free] File attachment / editable path insertion on both platforms (native pickers, safe escaping, no auto-execute, local-vs-remote clarity, upload-to-remote). *(A5, W5)*
21. [Free] Command history (≥10 recent) + snippets (copy-only, no auto-execute) on both platforms. *(A6, W6)*

**Track 5 — File transfer and tunnels**
22. [Free] SFTP basic on both platforms (browse/upload/download/create/rename/move/delete, progress, cancel, retry, confirmations, partial-transfer safety; SFTP not SCP). *(A7, W7)*
23. [Free] SSH tunnels (local/remote/dynamic SOCKS) on both platforms with validation and session-tied lifecycle. *(A8, W8)*

**Track 6 — Credential vault and advanced SSH security**
24. [Free] Local credential vault on both platforms (Keystore / DPAPI-Credential Locker), key gen/import, fingerprints, optional biometric/Hello, re-auth before export. **Requires item 10.** *(A9, W9)*
25. [Unassigned → review] SSH certificates, FIDO2/security keys, agent forwarding feasibility review; then tier assignment. *(A10, W10)*

**Track 7 — Premium productivity**
26. [Premium] Advanced workspace presets/session restoration, multi-host snippet execution, advanced autocomplete — **after entitlement design** and only if genuinely implemented and tested. *(A11, W11)*

**Track 8 — Premium sync, team and collaboration (requires items 8, 10, 11 and a server-side design)**
27. [Premium] Sync key hierarchy, recovery, rotation, revocation design + threat model.
28. [Premium] Optional encrypted multi-device sync (client-side AEAD; device enrollment/revocation; conflict handling; quotas; deletion). Cloudflare R2/Workers only after explicit resource/cost review. *(A12, W12)*
29. [Premium] Team workspaces/shared vaults, roles/permissions, collaboration/handoff, audit — requires a real server-side authorization model.
30. [Premium] Advanced SFTP queue/host-to-host transfer. *(A12, W12)*

**Track 9 — Encrypted-source hardening (optional parallel track; do not gate Tracks 2–8)**
31. Select and independently review a streaming AEAD bundle format; implement a strict authenticated manifest/parser.
32. Define and rehearse DEK wrapping + key custody (generation, storage, offline recovery, rotation, revocation, destruction).
33. Implement a safe archive validator/extractor with traversal/symlink/duplicate/bomb defences and adversarial fixtures.
34. Hash-lock dependencies; design and negative-test the protected release authorization (immutable SHA binding, protected environment, fork isolation, ephemeral runner, cleanup).
35. Complete the go/no-go gates in `ENCRYPTED_SOURCE_REVIEW.md` §7 and obtain independent review + explicit owner approval before admitting application source or enabling decryption.

**Track 10 — Release readiness**
36. Compatibility matrix (Android + Windows), dependency/security audit, accessibility/performance/usability testing.
37. Signed release builds; privacy policy; support documentation; Play/Store/website listing verification.
38. Pilot release before commercial rollout. **No public GitHub binary releases.**

---

## Appendix A — Evidence index

- Repository metadata, branches, PRs, workflows, runs, releases: GitHub REST API (2026-11-10).
- `main` content: `git ls-files` at `260d115`.
- Prototype code/tests: `origin/feat/source-bundle-prototype` (`tools/source_bundle.py`, `tests/test_source_bundle.py`, `.github/workflows/source-prototype-tests.yml`, `requirements-source-prototype.txt`).
- Security review: `origin/docs/encrypted-source-build-design:docs/ENCRYPTED_SOURCE_REVIEW.md`.
- Feature/tier spec: `origin/docs/termius-feature-parity:docs/FEATURE_PARITY_SPEC.md`.
- Dependency facts: GitHub REST API (repo licences/stars/activity), Maven Central search, NuGet flat-container + search APIs, PyPI JSON, GitHub Security Advisories API.
- Platform requirement: Google Play target API level guidance (Android 16 / API 36 for submissions from 2026-08-31).

## Appendix B — Recommended pinned versions (candidates, to confirm at implementation)

| Dependency | Ecosystem | Recommended |
|---|---|---|
| ConnectBot sshlib | Maven | `org.connectbot.sshlib:sshlib:0.6.7` (or later) |
| ConnectBot termlib | Maven/JitPack | latest `org.connectbot:termlib` |
| sshj (Android alternative) | Maven | `com.hierynomus:sshj:0.40.0` |
| mwiede jsch (Android fallback) | Maven | `com.github.mwiede:jsch:2.28.8` |
| SSH.NET | NuGet | `SSH.NET:2026.0.0` (**minimum**) |
| Windows App SDK | NuGet | `Microsoft.WindowsAppSDK:2.6.5` |
| .NET | SDK | .NET 10 LTS (`10.0.14`) |
| BouncyCastle (if needed) | Maven | `org.bouncycastle:bcprov-jdk18on:1.80` |
| Source-bundle tooling | PyPI | `cryptography` pinned + hash-locked (prototype only) |

*End of audit report.*
