# RSS Netrix — Source Handling Policy

**Status:** Accepted
**Owner decision date:** 2026-11-10
**Applies to:** every contributor, build, and automation that touches this repository

## 1. Purpose

RSS Netrix is proprietary commercial software owned by Razeen Secure Solution.
The repository `riyazamra1/RSS-Netrix` is public. This policy defines how
proprietary application source is handled so that plaintext proprietary source
never enters the public repository, public artifacts, logs or releases, while
ordinary development continues unimpeded.

## 2. Non-negotiable rules

1. **No plaintext proprietary application source in any public commit, branch,
   pull request, tag or release.**
2. **No plaintext proprietary source in public CI/CD artifacts, caches, logs,
   job summaries, test reports or screenshots.**
3. **No plaintext proprietary source published as a release asset.**
4. **No production decryption, source admission, or source-bearing CI/CD until
   all production gates have passed:** independent security review; approved
   HSM/KMS-backed production key custody; and protected release authorization
   with negative tests proving unauthorized releases cannot decrypt or admit
   source.
5. No keys, secrets, signing credentials or recovery material in the
   repository, workflows, logs or artifacts.
6. The Android application ID remains `com.riyaz.rssnetrix`. The Windows
   display name remains `RSS Netrix`.

## 3. What is permitted in the public repository

- Product documentation, specifications, architecture and decision records.
- Non-sensitive build metadata and dependency manifests that contain no
  proprietary source and no secrets.
- Encrypted proprietary source bundles (ciphertext only), only after all
  production gates in rule 2.4 have passed and the owner has explicitly
  authorized source admission.
- Secret-free tests that exercise public, non-proprietary tooling.

## 4. What is prohibited in the public repository

- Plaintext proprietary Android or Windows application source.
- Plaintext proprietary assets, design files or private implementation details.
- Decryption keys, KEKs, signing keys, tokens or credentials.
- Customer binaries (APK, AAB, EXE, MSI, MSIX, installers) as public releases.

## 5. Development workflow

- Proprietary application source is developed in an isolated, access-controlled
  workspace, never in a public branch.
- Application source admission is prohibited until every production gate in
  rule 2.4 has passed and the owner has explicitly approved the specific
  admission.
- The encrypted-source workstream is a **parallel workstream**, not a blocker
  for ordinary development. The production security gate is absolute and is
  never bypassed for convenience.

## 6. Enforcement

- Public CI is secret-free and read-only; it must never be able to read
  plaintext source or decryption material.
- Never use `pull_request_target` to check out or execute untrusted pull-request
  code with privileged credentials.
- Changes to workflows, encryption logic, build scripts and dependency locks
  require elevated review.
- Any suspected plaintext source or secret exposure is treated as a security
  incident: stop, remove the exposure, and follow the incident procedure before
  continuing. Removing a leaked file in a later commit does not remove it from
  Git history.

## 7. Relationship to other documents

- `ENCRYPTED_SOURCE_REVIEW.md` — the go/no-go gates for encrypted source. **Planned design document** (drafted on an unmerged branch; not yet on `main`).
- `SOURCE_PROTECTION.md` and `BUILD_PIPELINE.md` — the detailed design. **Planned design documents** (drafted on an unmerged branch; not yet on `main`).
- `SECURITY.md` — the security design and threat model (present).
- `LICENSE` — the proprietary all-rights-reserved licence for RSS Netrix code (present).
- `THIRD_PARTY_NOTICES.md` — preserved third-party licences (present).
