# RSS Netrix — Comprehensive Feature-Parity Specification

**Status:** Draft requirements baseline for review  
**Product:** RSS Netrix  
**Publisher:** Razeen Secure Solution  
**Android application ID:** `com.riyaz.rssnetrix`  
**Platforms:** Native Android and native Windows

This document defines the intended functional coverage for RSS Netrix. It uses publicly documented Termius product capabilities as a competitive feature checklist, not as a source of code, assets, branding, private implementation details or copied UI. RSS Netrix must use original implementation, interaction design and RSS visual identity.

Feature parity means equivalent user outcomes where the platform and protocol permit them. It does not mean reproducing proprietary internals or promising identical implementation.

## 1. Product-wide requirements

- Deliver a complete, useful SSH and remote-server management product rather than a demonstration shell.
- Build native Android and native Windows applications. Do not use a WebView as the primary application shell.
- Keep core SSH connectivity local-first and independent of mandatory RSS Core/cloud availability.
- Maintain feature parity across Android and Windows wherever technically practical. Document platform-specific limitations rather than silently omitting features.
- Use a coherent RSS design system, responsive layouts, accessibility support and clear security states.
- Support offline access to locally stored hosts, identities, keys and preferences; an internet connection must not be required merely to connect directly to a reachable SSH server.
- Do not automatically execute commands when selecting a snippet, history item, file attachment or autocomplete suggestion.
- Treat destructive file and host operations as explicit, confirmable actions.

## 2. Host and connection management

- Create, edit, duplicate, delete, group, tag, sort, filter and search hosts.
- Save hostname/IP, port, username, authentication method, connection timeout, notes, terminal preferences and optional startup configuration.
- Support reusable identities and credentials, host-specific overrides and group-level configuration.
- Support host chains / jump hosts and multi-hop connection profiles.
- Support environment variables and per-host or per-group connection settings where the remote protocol permits.
- Provide one-tap connection, reconnect, disconnect, connection status and useful diagnostics.
- Support importing and exporting host configuration with explicit secret-exclusion and encryption options.
- Provide host aliases and local host mapping support where the operating system permits.
- Maintain a known-hosts database and clear host-key trust/change workflows.

## 3. Terminal and protocol support

### 3.1 Interactive terminal

- Real interactive SSH shell with PTY allocation, terminal resize, Unicode, ANSI/VT processing, scrollback, selection, copy/paste and keyboard handling.
- Multi-tab sessions and multiple independent connections.
- Resizable split-pane workspaces, with the ability to create, close, reorder and focus panes.
- Save, name, restore and reopen workspaces and their session layouts.
- Preserve background session geometry and avoid spurious resize events when switching tabs.
- Support terminal font family, size, weight, line spacing, cursor style/blink, scrollback limits and keyboard preferences.
- Provide terminal search, clear-screen, select-all, copy, paste and configurable shortcuts.
- Support broadcast input to explicitly selected sessions as an opt-in action, with a highly visible enabled state and safeguards against accidental multi-server execution.
- Support local terminal access on Windows. Android local-shell capabilities must be evaluated against Android sandbox restrictions and must not imply unrestricted device shell access.
- Support Telnet, Mosh, serial and other advertised connection protocols only after separate protocol, security, platform and dependency feasibility reviews. SSH remains the core protocol.
- Support agent forwarding and SSH certificate authentication where the selected libraries and platform security model permit it.
- Support SOCKS and HTTP proxy connection paths where compatible.

### 3.2 Terminal themes and colours — confirmed Free features

These capabilities are explicitly required in the Free tier and must not be paywalled:

- At least 30 built-in themes, including dark, light, black/OLED and high-contrast families.
- Custom theme editor and colour picker.
- Colour wheel and brightness/value selector.
- HEX, RGB and HSL input.
- Live preview against a functioning terminal renderer.
- Separate background, foreground, cursor, selection background and selection foreground colours.
- Editable ANSI 16-colour palette, bold text colours and support for 256-colour and 24-bit true-colour output.
- Save, rename, duplicate, delete, import, export and restore default themes.
- Assign a different theme to each host/connection.
- Import/export theme definitions in a documented, versioned format.
- Sync user-selected theme preferences only when optional encrypted sync is enabled.
- Theme changes must affect the actual terminal renderer, not only application chrome.

### 3.3 File attachment into terminal input — confirmed requirement

- Provide an attachment action beside the terminal input/keyboard toolbar.
- Android: open the native Storage Access Framework picker.
- Windows: open the native file picker.
- After selection, insert the selected local file path into the active terminal input.
- Keep the inserted command/path editable; do not execute it automatically.
- Quote or escape paths safely for the configured shell where possible, while allowing the user to edit the result.
- Handle spaces and shell-special characters.
- Clearly distinguish a local device path from a remote server path.
- For a remote file, provide a separate SFTP action to copy its remote path into the terminal input.
- Respect Android URI permissions and Windows file access permissions. If a provider supplies a content URI rather than a filesystem path, stage or expose the file through a safe, documented mechanism; never invent a path that the shell cannot access.
- Explain that a local mobile/PC path is not automatically accessible to the remote server. Provide an explicit upload-to-remote workflow when the user's intention is to use the file on the server.

## 4. Productivity tools

- Searchable shell command history with host/session context and user-controlled retention.
- Command snippets and script library with names, descriptions, categories, tags and optional prompted variables.
- Startup snippets and optional per-host/per-group startup actions, disabled by default until explicitly configured.
- Run a snippet in the active terminal only after deliberate user confirmation.
- Multi-execution of a selected snippet across explicitly selected sessions/hosts, with a review step and clear per-host result reporting.
- Terminal autocomplete for commands, arguments and file paths using local history and permitted shell context.
- Autocomplete must never silently execute a suggestion.
- Workspace presets, session restoration and saved layouts.
- Optional session logging and searchable session records with retention, export and deletion controls.
- Clearly indicate when recording/logging is active; redact authentication secrets and support sensitive-output exclusions.
- Optional command/output capture must be user-controlled.

## 5. SFTP and file transfer

- Remote directory browsing, navigation, sorting, filtering and file metadata.
- Upload, download, multi-select, drag-and-drop where supported, create directory, rename, move, copy and delete.
- Transfer queue with progress, speed, elapsed time, remaining time estimates, pause/resume where protocol/library permits, cancellation, retry and failure details.
- Confirm destructive operations and protect against accidental overwrite.
- Support large-file transfers, interruption recovery and safe handling of partial files.
- Support local and remote dual-pane workflows where the platform layout permits.
- Provide file and folder context menus.
- Show local and remote paths distinctly.
- Provide remote file preview/edit only for explicitly supported text formats; never imply safe editing of arbitrary binary files.
- Support host-to-host transfer through a controlled relay or client-mediated transfer workflow, with explicit bandwidth/privacy implications, only after architecture review.
- File attachment and terminal path insertion must integrate with the SFTP browser without conflating local and remote filesystem namespaces.

## 6. SSH tunnels and network tools

- Local, remote and dynamic SOCKS port forwarding.
- Multiple forwarding rules per host/session, with names, local/remote endpoints and status.
- Start, stop, edit and remove tunnel rules.
- Validate ports, bind addresses and remote destinations; surface permission, bind and connection failures.
- Clear tunnel lifecycle behaviour when sessions disconnect or reconnect.
- Agent forwarding where supported.
- Jump hosts / host chains.
- SOCKS and HTTP proxy support where supported.
- Network diagnostics such as connection test and latency visibility where technically available; avoid presenting estimates as guaranteed measurements.

## 7. Keychain, identities and authentication

- Local encrypted vault for host credentials, passwords, private keys, passphrases, certificates and reusable identities.
- Import supported OpenSSH, PEM and platform-compatible key formats after library validation.
- Generate supported SSH keys, set passphrases, inspect public keys and SHA-256 fingerprints.
- Support key rotation and replacement workflows.
- Support SSH certificates and FIDO2/security-key authentication where compatible with the platform and SSH library.
- Support device-bound keys and biometric/PIN/app-lock protection where the OS provides secure APIs.
- Android: Android Keystore-backed protection and Android biometric/device credential APIs.
- Windows: DPAPI/Credential Locker or another reviewed Windows-protected storage mechanism; Windows Hello integration only where supported by the chosen native API.
- Re-authenticate before revealing/exporting sensitive key material.
- Never display or export secrets by default.
- Never claim that a private key can be revoked on a remote server merely by deleting its local copy; distinguish local removal from remote authorized_keys/certificate revocation.
- Optional secure sharing of credentials through encrypted team vaults requires a reviewed key distribution, membership, revocation and recovery design.

## 8. Encrypted vault and synchronization

- Optional, explicit opt-in encrypted sync across supported RSS Netrix devices.
- Client-side authenticated encryption before data leaves the device.
- End-to-end encryption for synchronized host records, settings, snippets and user-selected vault content.
- Keep basic local operation available if sync service is offline.
- Device enrollment, device list, revoke device, sync status and last-sync visibility.
- Conflict resolution, versioning, backup/restore, key rotation, recovery and permanent deletion.
- Secrets/private keys excluded from sync by default until the recovery and sharing model is explicitly approved.
- Never send plaintext SSH passwords, private keys or vault contents to the sync service.
- Use per-user authorization, quotas, rate limits, object size limits and audit events.
- Do not provision paid cloud resources without explicit approval; development target remains $0/month where feasible, without guaranteeing free-tier availability.

## 9. Team and collaboration capabilities

- Team workspaces and encrypted shared vaults.
- Multiple vaults with separated access boundaries.
- Invite, remove and manage team members.
- Roles and granular permissions for hosts, identities, keys, snippets and vaults.
- Secure sharing and membership-change re-encryption/revocation.
- Shared session logs with explicit recording and access controls.
- Real-time terminal collaboration / session handoff with visible participants, clear control ownership and explicit read/write permissions.
- Audit trail for sharing, membership, permission and vault operations.
- Team and collaboration capabilities require a server-side authorization model and must not be simulated solely in the client UI.

## 10. Application security and privacy

- SSH host-key verification before credentials are sent.
- Strong warning and explicit recovery workflow for changed host keys.
- Modern cryptographic algorithms enabled by default; obsolete algorithms disabled unless explicitly enabled with a warning.
- Encrypted local secret storage and protected key handling.
- App lock and biometric/PIN re-authentication where supported.
- No credentials or terminal secrets in logs, analytics, crash reports, source control or build artifacts.
- Session logging is opt-in and transparent.
- Clear local data deletion, vault deletion, device revocation and sync deletion controls.
- Threat model and dependency/license audit before release.
- Public source encryption is not a substitute for secure binaries; released APK/Windows installers remain subject to reverse engineering.

## 11. Platform-specific expectations

### Android
- Native Kotlin and Jetpack Compose.
- Phone and tablet responsive layouts.
- Android keyboard and extra-key toolbar for terminal control keys.
- Android file picker / Storage Access Framework integration.
- Lifecycle-safe foreground connection handling with clear notification and battery policy where long-running sessions require it.
- Android Keystore and biometric integration.
- Respect scoped storage; never claim arbitrary filesystem access.

### Windows
- Native Windows desktop application, not a WebView wrapper.
- Keyboard-first workflow, shortcuts, mouse support, resizable panes and multi-window behaviour where feasible.
- Native file picker, drag-and-drop and clipboard integration.
- Secure Windows credential storage and optional Windows Hello integration.
- Windows installer/package signed for official RSS distribution.

## 12. Free/Premium feature classification — approved scope

The owner approved the following proposed feature split for RSS Netrix planning. This approves **feature placement only**; it does not approve prices, trial duration, subscription terms, device limits, payment providers, licence enforcement details or paid infrastructure.

| Capability | Tier | Scope |
|---|---|---|
| Direct SSH connections and local host profiles | **Free** | Core SSH access, saved hosts, groups, tags and local connection settings |
| SSH password and key authentication | **Free** | Secure local credential handling and host-key verification |
| Local encrypted credential vault | **Free** | Device-protected local storage; no mandatory cloud account |
| Interactive SSH terminal | **Free** | PTY, ANSI/VT, Unicode, scrollback, copy/paste and terminal keyboard |
| Terminal tabs and split panes | **Free** | Multiple live SSH sessions and basic split workspace |
| All terminal themes and customization | **Free** | 30+ themes, custom theme editor, colour wheel, HEX/RGB/HSL, ANSI palette and true colour |
| File attachment/path insertion | **Free** | Native picker, editable path insertion, no automatic execution |
| Basic SFTP | **Free** | Browse, upload, download, create folder, rename and delete with safeguards |
| Basic SSH port forwarding | **Free** | Local, remote and dynamic SOCKS tunnels |
| Basic command history and snippets | **Free** | Recent command list and user-created snippets with deliberate execution |
| Basic host import/export | **Free** | Host configuration export/import with secrets excluded by default |
| Advanced workspace presets and session restoration | **Premium proposal approved** | Saved multi-host layouts and advanced workspace management |
| Advanced productivity | **Premium proposal approved** | Multi-host snippet execution, advanced autocomplete and enhanced command/script management |
| Advanced SFTP workflows | **Premium proposal approved** | Advanced transfer queue features, host-to-host transfer and enhanced file workflows |
| Encrypted multi-device sync | **Premium proposal approved** | Optional end-to-end encrypted sync, device management and recovery |
| Team workspaces and shared vaults | **Premium proposal approved** | Team membership, shared encrypted data and granular permissions |
| Live terminal collaboration and session handoff | **Premium proposal approved** | Multi-user session collaboration and control handoff |
| Team audit and administration | **Premium proposal approved** | Audit trails, shared session records and administrative controls |
| Telnet, Mosh, serial and other additional protocols | **Unassigned** | Keep subject to technical, security, platform and licensing feasibility review |
| SSH certificates, FIDO2/security keys and advanced auth integrations | **Unassigned** | Do not restrict or promise until compatibility and security review |

### Commercial and implementation boundaries

- Keep the Free tier independently useful for personal/local SSH administration. Do not make basic SSH access, secure local credential storage or essential security controls dependent on a subscription.
- Every terminal theme, custom colour picker, colour format and terminal colour capability remains Free.
- Premium capabilities must be genuinely implemented and tested before they are advertised or charged for. A UI-only lock screen is not an implementation.
- Any Premium entitlement must be enforced through a reviewed licensing/authorization design; do not trust a client-side flag alone.
- Exact prices, currency presentation, trial, renewal, device activation limits, grace periods, refunds, payment provider and licence recovery remain separate owner decisions.
- Do not provision paid services or infrastructure without explicit approval.
- Additional protocols and advanced authentication remain unassigned; do not silently classify them as Premium.

## 13. Release and distribution constraints

- Android application ID remains `com.riyaz.rssnetrix`.
- Android distribution: official RSS website and/or Google Play Store only.
- Windows distribution: official RSS website and/or Microsoft Store only.
- Do not publish APK, AAB, EXE, MSI, MSIX or installer binaries as public GitHub release assets.
- Use signed production builds and verify signing identity.
- Official download links should be authenticated and time-limited where appropriate.
- Do not claim store availability before the actual listing, review and download path are verified.
- Premium licensing and device activation must be enforced by a reviewed authorization design; do not rely solely on a client-side boolean.
- No paid service, infrastructure or subscription is provisioned without explicit owner approval.

## 14. Acceptance gates

A feature is complete only when:
1. The real protocol or platform operation works; a screen or mock response is insufficient.
2. Automated tests cover normal, error, cancellation and security-sensitive paths where practical.
3. Android and Windows platform tests pass for the supported matrix.
4. SSH host-key, credential, file transfer and permission failure cases are verified.
5. The feature does not leak secrets through logs, crash reports, analytics or artifacts.
6. Accessibility, keyboard, touch and responsive layout behaviour is checked.
7. Documentation and user-facing limitations are accurate.
8. The release artifact is signed and its actual distribution path is verified.

## 15. Public competitive references

These references are used only to identify publicly advertised feature categories. They are not permission to copy protected implementation or assets.

- Termius product overview: https://termius.com/
- Termius pricing and public feature comparison: https://termius.com/pricing
