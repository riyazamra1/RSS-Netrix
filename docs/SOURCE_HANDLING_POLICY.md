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
4. **No decryption of production source bundles and no source-bearing CI/CD
   until the security design in `ENCRYPTED_SOURCE_REVIEW.md` is reviewed and
   explicitly approved by the owner.**
5. No keys, secrets, signing credentials or recovery material in the
   repository, workflows, logs or artifacts.
6. The Android application ID remains `com.riyaz.rssnetrix`. The Windows
   display name remains `RSS Netrix`.

## 3. What is permitted in the public repository

- Product documentation, specifications, architecture and decision records.
- Non-sensitive build metadata and dependency manifests that contain no
  proprietary source and no secrets.
- Encrypted proprietary source bundles (ciphertext only), once the encrypted
  source format is implemented and approved.
- Secret-free tests that exercise public, non-proprietary tooling.

## 4. What is prohibited in the public repository

- Plaintext proprietary Android or Windows application source.
- Plaintext proprietary assets, design files or private implementation details.
- Decryption keys, KEKs, signing keys, tokens or credentials.
- Customer binaries (APK, AAB, EXE, MSI, MSIX, installers) as public releases.

## 5. Development workflow

- Proprietary application source is developed in an isolated, access-controlled
  workspace, never in a public branch.
- Application source is admitted to the public repository only as an approved
  encrypted bundle, and only after the encrypted-source gates pass.
- The encrypted-source workstream is a **parallel workstream**, not a blocker
  for ordinary development. However, the security gate in rule 2.4 is absolute:
  it is never bypassed for convenience.

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

- `ENCRYPTED_SOURCE_REVIEW.md` — the go/no-go gates for encrypted source.
- `SOURCE_PROTECTION.md` and `BUILD_PIPELINE.md` — the detailed design.
- `SECURITY.md` — the security design and threat model.
- `LICENSE` — the proprietary all-rights-reserved licence for RSS Netrix code.
- `THIRD_PARTY_NOTICES.md` — preserved third-party licences.
