# RSS Netrix — Security Design and Threat Model

## 1. Assets
- SSH passwords, private keys and key passphrases
- Host identities and connection metadata
- Terminal input/output and command history
- SFTP file contents and transfer metadata
- Cloud sync encryption keys and authorization credentials
- Build signing keys and release artifacts

## 2. Threats
- Device loss, malware or a compromised user account
- Malicious or substituted SSH host
- Man-in-the-middle attacks and changed host keys
- Malicious dependency or compromised build workflow
- Public repository disclosure
- Cloud account/token compromise and unauthorized object access
- Accidental logging, crash-report or artifact leakage
- Backup key loss or device revocation failure

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
- Use authenticated encryption (AES-256-GCM is the current candidate) with a unique nonce per encryption operation, authenticated metadata, key versioning and strict envelope validation.
- Define a recovery phrase/key export or another user-controlled recovery mechanism before sync can be enabled.
- Provide device revocation, key rotation, conflict handling and permanent deletion.
- The server must enforce per-account object authorization, size/type limits, quotas and rate limits.
- Server-side secrets must be restricted, rotated and absent from source and client binaries.
- A Worker Secret is not an HSM or a separate KMS; compromise of the Worker or its secret may expose protected data depending on the design.

### Repository and CI
- Keep plaintext source out of the public repository under the agreed encrypted-source approach.
- Do not expose secrets to fork pull requests or other untrusted workflow contexts.
- Pin third-party actions by immutable commit SHA; grant least-privilege workflow permissions.
- Do not print secrets or decrypted source in logs.
- Do not cache or publish decrypted source workspaces.
- Require protected-branch review for changes to workflows, encryption logic and build scripts.

## 4. Key management decisions still required
- Whether source-encryption keys and user cloud-sync keys are fully separate (required recommendation: yes).
- Exact key derivation, wrapping, recovery, rotation and revocation formats.
- Whether a Worker can authorize decryption without ever returning a long-lived master key.
- Build identity and short-lived authorization mechanism.
- Incident response and key compromise procedure.

## 5. Security limitations
- A public Android APK or Windows executable can be inspected and reverse engineered.
- Encryption of source files at rest protects repository contents but cannot make released binaries opaque.
- Client-side encryption does not protect data on an already compromised endpoint.
- Free-tier infrastructure is not a security boundary by itself.

## 6. Release gate
No production credential vault, encrypted sync or source-decryption workflow may be marked complete until threat modelling, implementation review, automated tests, recovery testing and independent verification are performed.
