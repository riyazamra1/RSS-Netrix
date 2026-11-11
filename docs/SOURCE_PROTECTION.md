# RSS Netrix — Encrypted Source Protection Design

## 1. Objective and scope

The public repository must not contain readable application source payloads. Product specifications, architecture decisions, build metadata and non-sensitive documentation may remain public. When implementation begins, source payloads must be encrypted before they are added to the public repository.

This is source-at-rest protection. It does not prevent reverse engineering of released APK/EXE binaries, protect a compromised developer endpoint, or make malicious build code safe.

## 2. Repository and storage boundaries

| Location | Permitted contents | Prohibited contents |
|---|---|---|
| Public `riyazamra1/RSS-Netrix` | Documentation, build metadata, encrypted source bundles, public test vectors | Plaintext app source, decryption keys, signing keys, credentials |
| Cloudflare R2 (not provisioned) | Encrypted source bundle objects only, if later approved | Keys, plaintext source, build logs |
| Trusted ephemeral runner | Decrypted source only during an authorized build | Persistent caches, uploaded source artifacts, retained workspaces |
| Release storage | Verified APK/EXE/installers and checksums | Source archives, private keys, build decryption keys |

No separate private build-control repository is part of this design. No R2 bucket, Worker, key, secret or paid resource is provisioned by this document.

## 3. Key hierarchy

Use separate cryptographic domains for:
- **Source-encryption key (SEK):** protects source bundles at rest.
- **Application sync key (ASK):** protects user data synchronized by RSS Netrix.
- **Code-signing keys:** sign release artifacts and are never used to encrypt source.
- **Cloud/API credentials:** authorize narrowly scoped service operations and are not encryption keys.

Never derive one of these keys from another or reuse a key across purposes. Use a versioned envelope: a fresh random data-encryption key per bundle, authenticated encryption for the bundle, and a separately protected wrapping key. The exact algorithm suite and file format remain unselected until a reviewed prototype passes interoperability, tamper, recovery and rotation tests. AES-256-GCM is a candidate, not yet an implementation decision. Nonces must never repeat under the same key.

## 4. Key custody

Ordinary public CI must be secret-free. Any future decryption-capable workflow must be a protected release path in this same repository: protected branch, mandatory review, immutable approved commit SHA, protected-environment approval, least privilege and a fresh ephemeral runner. Fork PRs and untrusted workflows must never receive secrets. Never use `pull_request_target` to execute untrusted code with privileged credentials.

Public workflow code and repository administrators who can change privileged workflows remain part of the trust boundary. GitHub Actions secrets are not an HSM/KMS and cannot prevent malicious privileged workflow code from exfiltrating secrets or plaintext. Keep a separately controlled offline recovery copy.

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
3. Protected-environment approval and mandatory review of privileged workflow changes in the same public repository; repository administrators remain trusted actors.
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

## 8. Commercial access and distribution policy

RSS Netrix includes a Free feature tier and paid Premium features. Free features do not mean public GitHub binary downloads.

- Android customers install through the official RSS website or Google Play Store.
- Windows customers install through the official RSS website or Microsoft Store.
- GitHub is not a customer download channel. Do not publish APKs, EXEs, MSIX packages or installers as public GitHub release assets.
- Premium features require valid licence validation and device activation. Expiry and revocation must be enforced by the licensing service.
- Store availability and platform policies must be verified before claiming a store release is available.
- Signed binaries can still be inspected and reverse engineered; source encryption does not prevent binary analysis.

## 9. Acceptance tests before source is added

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
