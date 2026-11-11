# RSS Netrix — Encrypted Source Protection Engineering Review

**Status:** Engineering review / design hardening only  
**Applies to:** `tools/source_bundle.py`, `tests/test_source_bundle.py`, and the proposed trusted build pipeline  
**Production approval:** Not approved  
**Application source admission:** Blocked

## 1. Executive decision

The current source-bundle utility is a useful experimental authenticated-encryption proof of concept. Its passing prototype tests do not establish production readiness. It must not be used to protect the production Android or Windows source tree, and no privileged decryption workflow may be enabled, until the acceptance gates in this document and `SOURCE_PROTECTION.md` pass review.

The current implementation is intentionally a one-shot file wrapper with a 512 MiB limit. It reads the full input, ciphertext and plaintext into memory. It does not create or extract archives, manage production keys, authorize releases, or prove that decrypted source is removed from a build environment.

## 2. Findings in the current prototype

| ID | Finding | Risk / required disposition |
|---|---|---|
| SRC-01 | Encryption and decryption use whole-file `read_bytes()` and hold large buffers in memory. | Not scalable; replace with a reviewed streaming format before production. |
| SRC-02 | A single environment-provided 32-byte KEK is used directly for all DEK wrapping. | No production custody, access policy, recovery, rotation or revocation. Do not deploy this model. |
| SRC-03 | DEK wrapping uses AES-GCM with a random 96-bit nonce under a potentially long-lived KEK. | No nonce registry or collision bound is enforced. Select a reviewed key-wrap construction or a rigorously managed per-key nonce strategy; do not assume random nonces provide deterministic uniqueness. |
| SRC-04 | Header JSON is parsed permissively and then reserialized for AAD. | Enforce one canonical encoding, reject duplicate JSON keys, reject unknown fields and validate exact types/ranges before cryptographic processing. |
| SRC-05 | The utility accepts an opaque archive and does not validate or extract it. | Archive extraction is a separate high-risk boundary. No extractor may be added without traversal, symlink, duplicate-entry, special-file and decompression-bomb defenses. |
| SRC-06 | The temporary output write is atomic in the ordinary case but does not provide a complete race-resistant filesystem policy. | Define destination handling, symlink policy, permissions, no-follow semantics, exclusive creation and cleanup behaviour for supported operating systems. |
| SRC-07 | The format has only basic version, algorithm and key ID fields. | Define authenticated product/platform identity, bundle ID, source revision, lengths, manifest digest and format negotiation. Avoid sensitive metadata. |
| SRC-08 | Dependency requirement is a version range, not a complete hash-locked dependency set. | Lock transitive dependencies and hashes; verify provenance and update policy. |
| SRC-09 | Prototype tests cover round-trip, wrong key, ciphertext/header tampering, destination overwrite and invalid key length. | Add malformed/canonical header, truncation, size boundary, nonce/key version, fuzz/property and filesystem failure tests. |
| SRC-10 | Public CI is secret-free, but there is no protected release workflow or authorization test. | Keep decryption disabled. Design and test protected approval, immutable SHA binding and fork/untrusted-event isolation before any secrets exist. |

These are engineering observations from the current code and design files, not claims that an exploit has been demonstrated.

## 3. Required bundle-format properties

The production format must be versioned and specified independently of its implementation.

### 3.1 Authenticated manifest

The authenticated manifest should contain only the minimum non-secret fields needed to validate and route a bundle, such as:

- fixed format identifier and integer version;
- product identifier and permitted target platform(s);
- unique bundle identifier;
- source revision / immutable commit identifier;
- encryption suite and key-wrapping suite identifiers;
- key version identifier;
- ciphertext and plaintext lengths, subject to strict maximums;
- manifest schema version and integrity digest.

All security-relevant manifest bytes must be authenticated as associated data. The parser must reject duplicate keys, unknown mandatory versions, wrong JSON/value types, non-canonical encodings, overflow, truncated input, trailing garbage and unsupported algorithm identifiers. Do not treat a checksum as a substitute for authenticated encryption.

### 3.2 Streaming authenticated encryption

The implementation must support large source trees without loading the entire archive into memory. Select a reviewed streaming AEAD construction or a carefully specified chunked-AEAD format. If chunked encryption is selected, the specification must define:

- unique per-chunk nonces or a reviewed nonce derivation/counter scheme;
- authenticated bundle ID, chunk index, chunk count and final-chunk marker;
- strict ordering and rejection of duplicate, missing, reordered or truncated chunks;
- authenticated total length and maximum chunk count;
- safe finalization so incomplete streams are never accepted as complete plaintext;
- bounded memory use and cleanup of partial plaintext on every failure path.

Do not invent a custom cryptographic construction. Record the library, version, supported platforms and independent review evidence before implementation.

### 3.3 DEK wrapping and key hierarchy

Use a fresh random DEK for each bundle. Keep source-encryption/wrapping keys separate from application sync keys, user vault keys, API credentials and Android/Windows signing keys.

The selected DEK-wrapping mechanism must be a standard, reviewed construction with a documented nonce/uniqueness model. Prefer a standard key-wrap construction that does not require ad hoc nonce tracking where it meets the requirements. If an AEAD wrapping construction is selected, specify how nonce uniqueness is guaranteed for every wrapping key across all writers, retries, regions and restores.

Key IDs are selectors, not secrets and not proof of authorization. A key ID must map to one immutable key version; never silently replace key material under an existing ID.

### 3.4 Key custody lifecycle

Before production, document and rehearse:

- generation using a cryptographically secure random source;
- storage in a separately controlled secret-management boundary;
- narrow authorization for the release build identity;
- offline recovery backup with access controls and tested restoration;
- rotation with old/new key overlap and bundle migration;
- emergency revocation and re-encryption after suspected compromise;
- audit trail for key access and administrative changes;
- destruction policy and explicit warning that destroying a key may make historical ciphertext unrecoverable.

Do not create or store production keys as part of this documentation work. Do not send source-encryption keys to Android or Windows clients.

## 4. Archive validation and extraction boundary

The encrypted payload is not safe merely because its AEAD tag is valid. It may still contain a malicious or malformed archive. Before extracting, validate the complete archive against a strict allowlist.

Required controls:

- Reject absolute paths, drive-qualified paths, UNC paths, NUL bytes, traversal components and paths that escape the extraction root after normalization.
- Reject symlinks, hard links, device nodes, FIFOs, sockets and other special files unless a separately reviewed requirement explicitly permits a safe subset.
- Reject duplicate paths, case-folding collisions on case-insensitive filesystems and file/directory prefix conflicts.
- Reject encrypted archive entries, unsupported compression methods and malformed central-directory/local-header inconsistencies.
- Enforce maximum entry count, per-file uncompressed size, total uncompressed size, compression ratio, path length, nesting depth and extraction time.
- Prevent writes through pre-existing symlinks and use directory-relative/no-follow filesystem operations where available.
- Extract into a new private temporary directory with restrictive permissions; never extract over an existing workspace.
- Verify the final extracted file inventory against an authenticated manifest before build.
- Delete partial extraction output on any error and verify cleanup.
- Include adversarial fixtures for traversal, symlinks, duplicate names, decompression bombs, truncated archives and malformed metadata.

No production extractor exists in the reviewed prototype. These controls are requirements, not implemented functionality.

## 5. Trusted build pipeline requirements

### 5.1 Public CI

Public documentation and test workflows remain secret-free and read-only. They may validate public documentation, source-bundle test code and ciphertext format fixtures. They must not receive source-decryption, signing, publishing or deployment credentials.

Never use `pull_request_target` to check out or execute untrusted pull-request code with privileged credentials. Fork PRs and untrusted branches must have no route to protected secrets.

### 5.2 Protected release authorization

A future privileged build must:

1. Be initiated only through an explicitly approved release process.
2. Bind the authorization to one immutable, reviewed commit SHA and the exact encrypted bundle digest.
3. Require protected-environment approval from an authorized maintainer.
4. Verify the branch, commit, bundle manifest, bundle digest and release metadata before requesting decryption authorization.
5. Use narrowly scoped, short-lived credentials and least-privilege workflow permissions.
6. Require elevated review for workflow files, encryption code, build scripts, dependency locks and release configuration.
7. Pin third-party actions to immutable commit SHAs and lock dependencies with integrity hashes.
8. Fail closed on any mismatch, missing approval, unexpected event, missing manifest field or cleanup failure.

GitHub secrets are not an HSM/KMS. Repository administrators and privileged workflow code are trusted actors. Malicious build scripts or dependencies can read and exfiltrate source while it is decrypted; workflow controls reduce but cannot eliminate this risk.

### 5.3 Ephemeral build and outputs

Use a fresh isolated runner per authorized build. Do not use a persistent self-hosted runner for source decryption. Separate Android and Windows jobs where that reduces toolchain exposure.

- Retrieve and verify ciphertext before requesting decryption.
- Decrypt only after authorization and immediately before the build.
- Keep plaintext in a private, short-lived workspace.
- Disable caches containing source or generated source intermediates.
- Do not upload source archives, decrypted workspaces, source maps, debug dumps or logs that reveal source.
- Restrict egress during the plaintext phase where feasible; document that egress restrictions are defense-in-depth.
- Retain only approved signed release packages, checksums and non-sensitive provenance/test summaries.
- Destroy the runner and workspace; verify cleanup through a controlled test and document limitations of the runner provider.

No decryption workflow, runner, secret or signing credential is authorized or provisioned by this review.

## 6. Test and verification matrix

| Area | Required evidence |
|---|---|
| Format/parser | Canonical encoding, duplicate-key rejection, strict schema, unsupported-version rejection, integer/length bounds |
| Cryptography | Round-trip, wrong key, modified ciphertext, modified AAD, truncation, chunk reorder/duplication/removal, finalization failure |
| Key lifecycle | Key-version selection, rotation rehearsal, recovery restore, emergency revocation drill |
| Archive | Traversal, absolute path, symlink/hardlink, duplicate/case collision, special file, decompression bomb, size/count/depth limits |
| Filesystem | Symlink destination, race/no-overwrite, restrictive permissions, disk-full, interrupted write, partial cleanup |
| Supply chain | Fully pinned actions, hash-locked dependencies, integrity verification and update review |
| Workflow authorization | Approved immutable SHA only, protected-environment gate, fork/untrusted event cannot access secrets |
| Build isolation | Fresh runner, no source cache/artifact/log, constrained egress, cleanup evidence |
| Release artifact | Correct package identity/version, signing identity, checksum, no source payload or secret material |

Tests must include both positive and negative cases. A passing round-trip test or green CI badge is not a source-confidentiality certification.

## 7. Explicit go/no-go gates

Application source remains outside the public repository until all of the following are complete:

- [ ] Streaming bundle format selected and independently reviewed.
- [ ] Strict authenticated manifest and parser implemented and tested.
- [ ] DEK wrapping and key custody lifecycle approved.
- [ ] Recovery, rotation and revocation rehearsals pass.
- [ ] Safe archive validator/extractor implemented and adversarial tests pass.
- [ ] Dependency lock and integrity policy are in place.
- [ ] Protected release authorization and immutable SHA binding are implemented.
- [ ] Fork/untrusted workflow negative tests pass.
- [ ] Ephemeral runner and cleanup tests pass.
- [ ] Artifact, log, cache and source-leakage inspections pass.
- [ ] Threat model and workflow receive independent security review.
- [ ] Owner explicitly approves production use.

Until then, the current utility remains a prototype only. Do not add plaintext app source, enable privileged decryption, publish customer binaries on GitHub, merge either existing draft PR, or provision paid infrastructure based on this document.
