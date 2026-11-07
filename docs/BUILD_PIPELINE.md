# RSS Netrix — Trusted Build Pipeline Design

## 1. Status

Design only. No workflow, private build-control repository, secret, key, R2 bucket, Worker, Android build or Windows build has been provisioned by this document. The workflow must not be enabled until the source-protection design and its acceptance tests are approved.

## 2. Intended flow

1. A maintainer prepares a source bundle in a controlled environment.
2. The bundle is validated, encrypted locally and tested by decrypting it in a disposable verification environment.
3. Only the encrypted bundle and non-sensitive manifest/checksum are pushed to the public repository (or, if later selected, copied to R2).
4. A maintainer authorizes a protected release build from a reviewed commit.
5. A trusted isolated runner fetches the exact ciphertext and verifies its manifest and checksum.
6. The runner obtains narrowly scoped decryption authorization from protected secrets, decrypts into a fresh temporary workspace and verifies authenticated integrity before extracting.
7. The runner builds Android and Windows targets in separate jobs/environments where practical. Build dependencies are pinned and verified.
8. Only release binaries, signatures and checksums are retained as artifacts. No source archive, plaintext workspace, key or debug dump is uploaded.
9. The runner is destroyed and cleanup evidence is recorded without logging secrets or source.

## 3. Trust boundaries and GitHub events

- Public repository workflows may run documentation checks and other secret-free validation.
- Untrusted fork pull requests must never receive source-decryption, signing, publishing or deployment secrets.
- Do not use `pull_request_target` to check out and execute untrusted PR code with privileged credentials.
- A protected release workflow must bind authorization to a reviewed immutable commit SHA and protected environment approval.
- Changes to workflow files, build scripts, dependency locks, encryption/decryption code and release configuration require elevated review.
- The private build-control repository is a proposed separate control plane, not yet created. It must be private, access-limited and protected against unreviewed workflow changes.

## 4. Runner isolation

Prefer a fresh ephemeral runner per build. Do not reuse a persistent self-hosted runner for decryption jobs. Use separate Android and Windows build environments if this reduces cross-platform toolchain exposure. Limit job permissions, avoid privileged container modes and avoid mounting unrelated credentials or host paths.

Disable source workspace caching. Do not publish build scans, diagnostic archives or crash dumps that may contain source. Restrict network access during the plaintext phase where feasible, while allowing only required dependency retrieval before decryption or from verified caches that contain no source. Network restrictions are defense-in-depth, not a guarantee against exfiltration.

## 5. Secrets and signing

- Store decryption authorization only in the approved protected secret store; do not add it until the private build-control repository is approved.
- Keep Android signing material and Windows signing material separate from source-encryption keys.
- Do not place long-lived signing keys in the public repository, R2 or client applications.
- Prefer short-lived credentials and narrow scopes. Masking is not a substitute for avoiding secret output.
- Never pass secret values as command-line arguments or print environment variables.
- Require explicit approval for production signing and publishing.

## 6. Build outputs

Allowed retained outputs:
- signed or unsigned test APK/EXE packages as appropriate to the approved stage;
- release installer/package;
- checksums, provenance metadata and non-sensitive build/test summaries.

Disallowed outputs:
- plaintext source archives or source maps containing private source;
- decrypted source folders;
- decryption keys, signing keys or access tokens;
- caches, debug bundles or logs containing source or secrets.

Artifact retention must be minimal and access-controlled. Release artifacts should be independently checked for expected package identity, version, signature and absence of accidental source payloads.

## 7. Cost and failure behavior

The development target is $0/month. Use eligible free services only after checking current quotas and terms. No paid runner, storage, signing service or Cloudflare resource may be provisioned without explicit approval. Enforce file-size and usage limits; fail safely rather than silently creating billable usage. Free-tier quotas can change and are not a cost guarantee.

## 8. Required pipeline tests

- Secret-free public PR workflow test.
- Negative test proving untrusted PR/fork cannot access protected secrets.
- Authorization test binding build to the approved commit SHA.
- Ciphertext checksum and authenticated-decryption failure tests.
- Build from a clean ephemeral runner.
- Android and Windows build/test verification, one controlled run at a time.
- Artifact inspection for source, secrets and unexpected files.
- Cleanup test and documented runner-retention limitations.
- Key recovery and rotation rehearsal.
- Review of workflow/action pins, permissions, dependencies and egress policy.

A green build alone does not prove source confidentiality. The pipeline is not production-ready until the security controls and negative tests above are verified.
