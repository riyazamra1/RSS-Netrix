# RSS Netrix — Third-Party Notices

RSS Netrix application code is proprietary and all rights reserved (see `LICENSE`).
This file records the licences of third-party components that RSS Netrix plans
to use or already depends on. Third-party licences are preserved in full and are
not modified by the RSS Netrix licence.

This is a planning record. No dependency is vendored or redistributed by this
repository yet. Before any release, generate a complete dependency inventory for
the actual build and include the required notices and licence texts in the
release package.

## Approved / candidate dependencies

| Component | Purpose | Licence | Status |
|---|---|---|---|
| ConnectBot SSH library (`org.connectbot.sshlib`, a.k.a. cbssh) | Android SSH/SFTP/tunnels/agent forwarding | Apache-2.0 | Approved for evaluation |
| ConnectBot terminal (`org.connectbot:termlib`, libvterm via JNI) | Android terminal emulator (Jetpack Compose) | Apache-2.0 (libvterm: MIT) | Approved for evaluation |
| SSH.NET (`Renci.SshNet`) | Windows SSH/SFTP/tunnels/shell | MIT | Approved for evaluation; pin >= 2026.0.0 |
| Microsoft Windows App SDK (`Microsoft.WindowsAppSDK`) | Windows UI (WinUI 3) | MIT | Approved for evaluation |
| .NET runtime and SDK | Windows application runtime | MIT | Approved for evaluation |
| Jetpack Compose / AndroidX / Material 3 | Android UI | Apache-2.0 | Approved for evaluation |
| Kotlin standard library | Android/Kotlin | Apache-2.0 | Approved for evaluation |

## Evaluated alternatives (not selected)

| Component | Purpose | Licence | Notes |
|---|---|---|---|
| sshj (`com.hierynomus:sshj`) | Android/JVM SSH/SFTP | Apache-2.0 | Android alternative |
| mwiede JSch (`com.github.mwiede:jsch`) | Android/JVM SSH | BSD-style | Fallback |
| Apache MINA SSHD (`org.apache.sshd`) | JVM SSH | Apache-2.0 | Heavier; advisory history |
| Bouncy Castle (`bcprov-jdk18on`) | JCE crypto provider (if required) | MIT | Pin and monitor advisories |
| Termux `terminal-emulator` / `terminal-view` | Android terminal emulator | Apache-2.0 | Fallback (not on Maven Central) |

## Internal tooling (prototype, not shipped)

| Component | Purpose | Licence | Notes |
|---|---|---|---|
| Python `cryptography` | Encrypted-source prototype tooling | Apache-2.0 / BSD | Prototype only; not approved for production |

## Obligations

- Preserve all third-party copyright notices and licence texts.
- Do not apply the RSS Netrix proprietary licence to third-party components.
- Re-verify licences, versions and security advisories at each release gate.
- Record the exact resolved dependency set and hashes for each signed release.
