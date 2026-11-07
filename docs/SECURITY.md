# RSS Netrix — Security Design and Threat Model

## 1. Assets
- SSH passwords, private keys and key passphrases
- Host identities and connection metadata
- Terminal input/output and command history
- SFTP file contents and transfer metadata
- Cloud sync encryption keys and authorization credentials
- Source-encryption and code-signing keys
- Build workspaces and release artifacts

## 2. Threats
- Device loss, malware or a compromised user account
- Malicious or substituted SSH host
- Man-in-the-middle attacks and changed host keys
- Malicious dependency, build script or compromised workflow
- Public repository disclosure and Git-history leakage
- Cloud account/token compromise and unauthorized object access
- Source exfiltration during decryption/build
- Accidental logging, crash-report, cache or artifact leakage
- Backup key loss, failed rotation or device revocation failure

## 3. Required controls

### SSH transport
- Verify server host keys; support known-host fingerprints and explicit trust-on-first-use confirmation.
- Warn prominently on key changes; never auto-accept changed keys.
- Prefer modern algorithms; disable legacy algorithms by default.
- Validate certificate/key formats and authentication failure paths.

### Local secret storage
- Android: encrypt secret material with keys protected by Android Keystore; consider biometric/device-credential gating as an optional policy.
- Windows: use DPAPI/Credential Locker-backed protection; avoid plaintext config files.
- Never store private keys or passwords in preferences, logs, clipboard history, analytics or source code.
- Clear transient secret buffers as far as platform/runtime constraints allow.

### Encrypted sync
- Use authenticated encryption with a unique nonce per encryption operation, authenticated metadata, key versioning and strict envelope validation. AES-256-GCM remains a candidate pending prototype and review.
- Define a recovery phrase/key export or another user-controlled recovery mechanism before sync can be enabled.
- Provide device revocation, key rotation, conflict handling and permanent deletion.
- The server must enforce per-account object authorization, size/type limits, quotas and rate limits.
- Server-side secrets must be restricted, rotated and absent from source and client binaries.
- A Worker Secret is not an HSM or a separate KMS; compromise of the Worker or its secret may expose protected data depending on the design.

### Encrypted source and build pipeline
- Public repository application source payloads must be encrypted before commit; do not commit plaintext source.
- Keep source-encryption keys separate from sync keys and code-signing keys.
- Store ciphertext in the public repository; never store decryption keys alongside it.
- Keep ordinary public CI secret-free. Restrict any future decryption workflow to a protected, reviewed release path and immutable approved commit.
- Public workflow code and repository administrators remain part of the trust boundary; GitHub secrets are not an HSM/KMS.
- Never expose decryption/signing secrets to untrusted PRs or forks.
- Pin third-party actions by immutable commit SHA and grant least-privilege workflow permissions.
- Do not print secrets or source; do not cache or publish decrypted workspaces.
- Treat build scripts and dependencies as executable, potentially malicious code. Restrict egress where practical and inspect retained artifacts.
- A trusted runner does not eliminate source-exfiltration risk while plaintext is available to build code.

## 4. Key management decisions and controls
- Source-encryption keys, user cloud-sync keys and signing keys are separate cryptographic domains.
- Exact source bundle suite and envelope format remain unselected until a tested prototype and review.
- Define key wrapping, backup, recovery, rotation, revocation and incident response before enabling source builds.
- GitHub protected secrets are not an HSM/KMS; repository administrators and privileged workflow code remain part of the trust boundary.
- Do not provision a Worker, R2 bucket, key or paid service without separate explicit approval.

## 5. Security limitations
- A public Android APK or Windows executable can be inspected and reverse engineered.
- Encryption of source files at rest protects repository contents but cannot make released binaries opaque.
- Client-side encryption does not protect data on an already compromised endpoint.
- Malicious build code can potentially exfiltrate source while it is decrypted.
- Free-tier infrastructure is not a security boundary by itself.

### Licensing and distribution
- Provide the defined Free feature tier without treating GitHub as a public binary download channel.
- Android customers install through the official RSS website or Google Play Store; Windows customers through the official RSS website or Microsoft Store, subject to channel readiness and platform policies.
- Enforce Premium entitlement, device activation, expiry and revocation server-side. Do not rely solely on client-side flags or obfuscation.
- Sign release packages and verify package identity and update authenticity.
- Released APK/EXE/MSIX packages can still be inspected and reverse engineered.

## 6. Release gate
No production credential vault, encrypted sync or source-decryption workflow may be marked complete until threat modelling, implementation review, automated negative tests, recovery testing and independent verification are performed.
