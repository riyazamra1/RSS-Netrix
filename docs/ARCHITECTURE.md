# RSS Netrix — Architecture

## 1. Architectural goals
- Native user experience on Android and Windows.
- Clear separation between UI, connection lifecycle, protocol operations, persistence and security.
- Keep secrets on-device by default.
- Make cloud sync optional and independently deployable.
- Avoid a mandatory dependency on RSS Core for basic SSH connectivity.

## 2. Proposed platform stacks

### Android
- Kotlin
- Jetpack Compose + Material 3
- Android Keystore-backed key encryption and Android platform storage APIs
- Coroutines/Flow for connection and transfer state
- SSH/SFTP library: evaluate maintained JVM-compatible candidates, licensing, host-key verification, algorithm support and terminal integration before selection.

Application ID: `com.riyaz.rssnetrix`.

### Windows
- Native Windows desktop application.
- Current candidate: modern .NET + WinUI 3.
- Evaluate SSH.NET and alternatives for SSH/SFTP/tunnel support, license compatibility, host-key callbacks and long-running interactive shell behaviour.
- Windows DPAPI or Credential Locker-backed protection for local secrets.
- Do not use a WebView as the primary application shell.

## 3. Logical modules
1. **Presentation:** host list, terminal workspace, SFTP browser, tunnels, settings.
2. **Application services:** host management, session orchestration, transfer orchestration, command history.
3. **Protocol adapters:** SSH transport, interactive shell, SFTP, port forwarding.
4. **Security:** host-key trust, credential vault, key import/generation, encryption envelope.
5. **Persistence:** non-secret profile metadata, encrypted local secret records, user preferences and opt-in history.
6. **Cloud adapter (later):** authenticated API, encrypted object transfer, sync metadata and conflict resolution.

## 4. Data boundaries
- Host profile metadata can be stored locally with normal application storage protections.
- Passwords, private keys and passphrases must be isolated in platform-protected secret storage.
- Cloud sync payloads are encrypted on the client before leaving the device.
- Cloud infrastructure must not receive plaintext SSH credentials.
- No cloud endpoint, R2 bucket, Worker, token or secret is created in this foundation stage.

## 5. Connection lifecycle
Model each connection explicitly: Created → Resolving → Connecting → HostKeyVerification → Authenticating → Ready → Reconnecting/Closing → Closed or Failed.
- Host-key verification must occur before credentials are sent.
- Cancellation must close transport resources.
- UI lifecycle changes must not accidentally duplicate sessions.
- Reconnect must not silently accept changed host keys.
- Tunnel and SFTP lifetimes must be tied to an explicit owning session or documented user-selected policy.

## 6. Terminal design
The terminal view is a renderer/input surface, not a shell implementation. The SSH channel handles PTY allocation, terminal dimensions, input bytes and output stream. The terminal renderer must handle ANSI/VT sequences, Unicode, resize events, scrollback and clipboard operations. Select or implement the terminal emulator only after compatibility and licensing review.

## 7. Public/private build boundaries
The public repository contains product documentation, non-sensitive build metadata and (once implemented) authenticated encrypted source bundles only. It must not contain plaintext application source, decryption keys, signing keys or credentials.

The public repository remains the single RSS Netrix repository. It may contain documentation, non-sensitive build metadata and encrypted source bundles after encryption and acceptance gates pass. It must not contain plaintext app source, decryption keys, signing keys, credentials or customer release binaries.

Public CI must be secret-free. Any future decryption workflow must be a protected release path in this same repository, tied to an immutable reviewed commit, protected-environment approval and an ephemeral runner. Fork PRs and untrusted workflows must never receive secrets. Public workflow code and repository administrators remain part of the trust boundary. No separate private build-control repository is required. Cloudflare R2 is a possible ciphertext store only and has not been provisioned. The trusted build runner is a separate, short-lived trust zone in which source is decrypted only for an authorized build. No decrypted workspace, cache or source artifact may persist beyond the job.

The build-control workflow, its administrators, build scripts and dependencies are part of the trusted computing base. A runner cannot guarantee source confidentiality against malicious code executing while source is decrypted. See `docs/SOURCE_PROTECTION.md` and `docs/BUILD_PIPELINE.md`.

## 8. Customer distribution and entitlement
- Free features are available under the defined Free product policy.
- Android installation is through the official RSS website or Google Play Store.
- Windows installation is through the official RSS website or Microsoft Store.
- GitHub is not a customer binary download channel. Do not publish public APK/EXE/MSIX release assets.
- Premium features require a valid licence, with server-side validation and device activation/revocation controls.
- Do not claim a store channel is live until its listing, review and download flow are verified.

## 9. Deployment
Cloud sync is a later, optional service. Cloudflare Worker + R2 is the current $0-target candidate, not provisioned infrastructure. Before deployment, define authentication, object authorization, quota enforcement, deletion semantics, abuse controls, observability and cost limits.
