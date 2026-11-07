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
- No cloud endpoint, R2 bucket, Worker, token or secret is created in this foundation commit.

## 5. Connection lifecycle
Model each connection explicitly: Created → Resolving → Connecting → HostKeyVerification → Authenticating → Ready → Reconnecting/Closing → Closed or Failed.
- Host-key verification must occur before credentials are sent.
- Cancellation must close transport resources.
- UI lifecycle changes must not accidentally duplicate sessions.
- Reconnect must not silently accept changed host keys.
- Tunnel and SFTP lifetimes must be tied to an explicit owning session or documented user-selected policy.

## 6. Terminal design
The terminal view is a renderer/input surface, not a shell implementation. The SSH channel handles PTY allocation, terminal dimensions, input bytes and output stream. The terminal renderer must handle ANSI/VT sequences, Unicode, resize events, scrollback and clipboard operations. Select or implement the terminal emulator only after compatibility and licensing review.

## 7. Build and source protection
The repository is public. Product documentation and build metadata may be readable; application source payloads must follow the user's approved encrypted-at-rest repository strategy before source code is added. Do not add plaintext application source files until the encryption/decryption/build trust model is implemented and reviewed.
- Build secrets are never available to untrusted pull requests.
- Decryption, if later approved, is restricted to a trusted, protected build path and a short-lived workspace.
- Plaintext source must not be uploaded as workflow artifacts, cached, logged or retained.
- Public binaries remain subject to reverse engineering; source encryption does not change that fact.

## 8. Deployment
Cloud sync is a later, optional service. Cloudflare Worker + R2 is the current $0-target candidate, not provisioned infrastructure. Before deployment, define authentication, object authorization, quota enforcement, deletion semantics, abuse controls, observability and cost limits.
