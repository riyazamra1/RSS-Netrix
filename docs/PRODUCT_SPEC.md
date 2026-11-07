# RSS Netrix — Product Specification

## 1. Product identity

- Product: RSS Netrix
- Publisher: Razeen Secure Solution
- Android application ID: `com.riyaz.rssnetrix`
- Windows display name: `RSS Netrix`
- Product class: SSH client and remote-server management tool
- Design rule: original RSS visual identity and interaction design; no reuse of Termius branding, artwork, proprietary code or protected assets.

## 2. Platforms

### Android
Native Android application using Kotlin and Jetpack Compose. The app must support phone and tablet layouts, lifecycle-safe connection handling, secure local storage, and adaptive terminal/file-manager layouts.

### Windows
Native Windows desktop application, not a browser wrapper. WinUI 3 with a modern .NET runtime is the current candidate. Final framework and SSH/SFTP dependencies remain subject to a compatibility and licensing review before implementation is locked.

## 3. Functional requirements

### 3.1 Host manager
- Create, edit, duplicate, group, tag, search and delete SSH host profiles.
- Fields: display name, hostname/IP, port (default 22), username, authentication method, optional jump-host reference, connection timeout and notes.
- Support password, private-key and agent/key-vault authentication as capabilities permit.
- Never display or export stored secrets in plaintext by default.

### 3.2 SSH terminal
- Interactive terminal with correct keyboard handling, terminal resize and ANSI/VT escape support.
- Connect, disconnect, reconnect and show explicit connection state.
- Multiple independent sessions, tabs and split workspaces.
- Copy/paste, selection, scrollback and configurable terminal font/appearance.
- Session logs are opt-in, clearly indicated and stored with access controls. Secrets and authentication prompts must be redacted where feasible.

### 3.3 SFTP
- Browse remote directories and file metadata.
- Upload, download, create directory, rename, move and delete.
- Transfer progress, cancellation, retry and clear error reporting.
- Confirm destructive operations and handle partial transfers safely.

### 3.4 SSH port forwarding
- Local forwarding, remote forwarding and dynamic SOCKS forwarding.
- Display active tunnel state and bound endpoints.
- Validate ports and surface bind, permission and remote-side failures.
- Tunnels stop when their owning session closes unless the user explicitly configures another supported lifecycle.

### 3.5 Credential and SSH key management
- Generate supported key types, import existing keys, add passphrases, inspect public-key fingerprints and remove/revoke local entries.
- Passwords, private keys and key passphrases are stored only through platform-protected storage.
- Private-key export requires an explicit user action and re-authentication where supported.

### 3.6 Command manager
- Show at least the 10 most recent commands for a session/host context.
- Allow tapping a history item to copy its command.
- Provide user-saved snippets with names, descriptions and optional categories.
- Executing a command from history/snippets always requires a deliberate user action; no automatic execution on tap.
- Command output capture is opt-in and must support sensitive-output exclusion.

### 3.7 Workspaces and productivity
- Multiple terminal tabs and split-pane sessions.
- Searchable command history and snippets.
- Optional autocomplete based on locally available history; do not transmit shell input to cloud services without explicit consent.
- Session logs with retention and deletion controls.

### 3.8 Encrypted cloud sync (later phase)
- Optional, opt-in sync for host metadata, snippets, preferences and user-selected encrypted backup data.
- Client-side authenticated encryption before upload.
- Secrets/private keys are excluded by default unless the user explicitly opts in after the recovery model is available.
- Conflict handling, device revocation, key rotation, backup/restore and permanent deletion must be specified before production release.
- No cloud resources are provisioned in the foundation stage.

## 4. UX and accessibility
- Original RSS design system; responsive Android and Windows layouts.
- Clear connection, trust, host-key-changed and security-warning states.
- Keyboard navigation on Windows; accessible labels and scalable text.
- No silent destructive actions and no misleading success states.

## 5. Security and privacy
- Verify SSH host keys; persist trust decisions and warn on changed keys.
- Support modern cryptographic algorithms and disable obsolete algorithms by default.
- Never log passwords, private keys, access tokens or unredacted authentication exchanges.
- Secrets must not enter source control, crash reports, analytics or build artifacts.
- Provide local data deletion and clear sync status.

## 6. Commercial direction
The initial engineering target is $0/month using free tiers where eligible. This does not guarantee zero cost. Paid plans, subscriptions, licensing and any paid infrastructure require a separate business decision and must not be introduced silently.

## 7. Acceptance baseline
A feature is not complete merely because a screen exists. Each capability needs automated tests where practical, device/OS testing, security checks, failure-path tests and verification against a real SSH/SFTP test environment.
