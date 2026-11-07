# RSS Netrix — Encrypted Source Protection Design

## 1. Objective and scope

The public repository must not contain readable application source payloads. Product specifications, architecture decisions, build metadata and non-sensitive documentation may remain public. When implementation begins, source payloads must be encrypted before they are added to the public repository.

This is source-at-rest protection. It does not prevent reverse engineering of released APK/EXE binaries, protect a compromised developer endpoint, or make malicious build code safe.

## 2. Repository and storage boundaries

| Location | Permitted contents | Prohibited contents |
|---|---|---|
| Public `riyazamra1/RSS-Netrix` | Documentation, build metadata, encrypted source bundles, public test vectors | Plaintext app source, decryption keys, signing keys, credentials |
| Private build-control repository (to be separately approved) | Reviewed workflow definitions, locked build tooling, protected Actions secrets | Production user data, long-lived plaintext source archives |
| Cloudflare R2 (not provisioned) | Encrypted source bundle objects only, if later approved | Keys, plaintext source, build logs |
| Trusted ephemeral runner | Decrypted source only during an authorized build | Persistent caches, uploaded source artifacts, retained workspaces |
| Release storage | Verified APK/EXE/installers and checksums | Source archives, private keys, build decryption keys |

The private build-control repository and any Cloudflare resources are proposed only. Creating them requires separate explicit approval. No repository, bucket, Worker, secret or key is created by this document.

## 3. Key hierarchy

Use separate cryptographic domains for:
- **Source-encryption key (SEK):** protects source bundles at rest.
- **Application sync key (ASK):** protects user data synchronized by RSS Netrix.
- **Code-signing keys:** sign release artifacts and are never used to encrypt source.
- **Cloud/API credentials:** authorize narrowly scoped service operations and are not encryption keys.

Never derive one of these keys from another or reuse a key across purposes. Use a versioned envelope: a fresh random data-encryption key per bundle, authenticated encryption for the bundle, and a separately protected wrapping key. The exact algorithm suite and file format remain unselected until a reviewed prototype passes interoperability, tamper, recovery and rotation tests. AES-256-GCM is a candidate, not yet an implementation decision. Nonces must never repeat under the same key.

## 4. Key custody

The proposed build design stores the minimum required decryption capability in protected secrets belonging to a private build-control repository. R2, if used, stores ciphertext only. Keep a separate offline recovery copy under owner-controlled access.

This is not an HSM or dedicated KMS. Repository administrators and authorized workflow maintainers may be able to invoke workflows that use the secret. GitHub Actions secrets do not by themselves prevent malicious workflow code from exfiltrating decrypted material.

Do not put the decryption key in:
- the public repository, source bundle, APK or EXE;
- a public workflow variable, command-line argument or log;
- R2 object metadata or a Worker response;
- a developer machine's shared configuration or a workflow artifact.

Never send the master key to a client application. Access should be limited to a reviewed protected build path and an explicit authorized release event.

## 5. Encryption bundle requirements

The bundle format must be versioned and include only non-secret metadata required to identify and validate it:
- format/version identifier;
- product and platform target;
- monotonically managed source-bundle version;
- encryption suite identifier;
- key-wrapping version/key identifier;
- nonce and authentication tag as required by the chosen suite;
- ciphertext length and cryptographic integrity information.

Authenticate metadata as associated data. Reject unknown versions, invalid lengths, duplicate/invalid nonce use, truncated payloads, authentication failures and unexpected archive paths. Prevent archive path traversal, symlinks escaping the workspace, duplicate paths and decompression bombs. The plaintext archive must not include local credentials, signing material, build secrets, caches or generated binaries.

## 6. Build trust and source-exfiltration controls

A trusted runner is not automatically safe. Build scripts and dependencies execute code and can read the decrypted workspace. Controls must include:
1. A protected release branch and mandatory review for source-encryption, workflow, build-script and dependency changes.
2. No secrets in fork pull-request or other untrusted workflow contexts; do not use unsafe `pull_request_target` patterns to check out and execute untrusted code.
3. A private build-control repository with tightly limited write/admin access and protected environments, if approved.
4. Immutable SHA pinning for third-party workflow actions; dependency lockfiles and integrity verification.
5. Least-privilege workflow permissions and short-lived job credentials.
6. Decrypt only after authorization, immediately before build, into a fresh ephemeral workspace.
7. Disable source-bearing caches and artifacts; do not upload workspace snapshots, crash dumps or diagnostic bundles.
8. Restrict network egress during the build where practical; do not assume this alone blocks exfiltration.
9. Keep logs free of source contents, environment dumps, tokens and secret values.
10. Destroy the runner/workspace after the job and verify cleanup behavior.

The build must fail closed if authorization, integrity checks, quota checks or cleanup prerequisites fail. A compromised workflow or malicious dependency can still exfiltrate source while it is readable; the controls reduce risk but do not mathematically eliminate it.

## 7. Rotation, revocation and recovery

Before production use, specify and test:
- routine key rotation with old-bundle migration or controlled retention;
- emergency key revocation after suspected compromise;
- re-encryption of active bundles under a new key version;
- recovery from the separately protected offline copy;
- owner/admin access removal and audit review;
- incident response, notification and repository history handling.

Deleting a key can render historical ciphertext unrecoverable. Do not rotate or revoke without a tested recovery/migration plan. Removing a leaked plaintext file in a later commit does not remove it from Git history; treat exposure as a security incident.

## 8. Acceptance tests before source is added

- Round-trip encryption/decryption on supported build environments.
- Wrong-key, modified-ciphertext, modified-metadata and truncated-file rejection.
- Archive traversal, symlink, duplicate-entry and decompression-bomb tests.
- Reproducible bundle manifest and checksum verification.
- No plaintext source in Git objects, logs, caches, workflow artifacts or release outputs.
- Workflow tests prove untrusted PRs cannot access decryption/signing secrets.
- A controlled test confirms ephemeral cleanup and documents its limitations.
- Key backup, rotation and revocation drills complete successfully.
- Security review approves the complete workflow and threat model.

Until every required gate is evidenced, keep application source out of the public repository and do not claim source encryption is implemented.
