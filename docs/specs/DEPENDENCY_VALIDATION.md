# RSS Netrix — Dependency Validation Report

**Status:** Read-only validation record
**Date:** 2026-11-10
**Scope:** Dependency, licensing, API-compatibility and security validation of the approved dependencies. No application source, no build artifacts, no binaries.

> **Environment note.** This sandbox has **no JDK, Gradle, Android SDK, or .NET SDK** installed, so an actual compile/run build could not be executed here. This report therefore records the *verifiable* evidence obtainable from public registries and source: exact coordinates, licences, maintained versions, published security advisories, and the real public APIs needed to satisfy RSS Netrix's security invariants. Items that require a full toolchain are marked **Pending CI**.

---

## 1. Summary of findings

| Dependency | Coordinates | Licence | Latest | API-compat | Security | Verdict |
|---|---|---|---|---|---|---|
| ConnectBot cbssh | `org.connectbot.sshlib:sshlib` | Apache-2.0 | 0.6.7 (2026-11-02) | Verified | No GHSA entries | **Approved (pending CI build)** |
| ConnectBot termlib | `org.connectbot:termlib` | Apache-2.0 (libvterm MIT) | 0.3.14 | Verified | No GHSA entries | **Approved (pending CI build)** |
| SSH.NET | `SSH.NET` (NuGet) | MIT | 2026.0.0 | Verified | 2 high advisories fixed in 2026.0.0 | **Approved, pin >= 2026.0.0** |
| Windows App SDK | `Microsoft.WindowsAppSDK` | MIT | 2.6.5 | Verified | Current | **Approved (pending CI build)** |
| .NET | .NET 10 LTS | MIT | 10.0.14 | Verified | Current LTS | **Approved** |

## 2. Android — ConnectBot cbssh (`org.connectbot.sshlib:sshlib`)

**Licence:** Apache-2.0 (POM `<licenses>`; source headers "Licensed under the Apache License, Version 2.0").
**Maintenance:** Active. Maven Central `latest`/`release` = **0.6.7**, `lastUpdated` 2026-11-02; repository `connectbot/cbssh` pushed 2026-11-08. CI advertises SLSA v1 Build Level 3.

**Coordinates warning (important).** Two different artifacts share the name `sshlib`:
- `org.connectbot.sshlib:sshlib` — the **new** cbssh library (Apache-2.0), described as "ConnectBot SSH Client Library", source `connectbot/cbssh`. **Use this one.**
- `org.connectbot:sshlib` 2.2.x — an **older** library (BSD-3-Clause), source `connectbot/sshlib`. Do **not** use this.

**API compatibility (verified against `connectbot/cbssh` `main`).**
- **Host-key verification** is a first-class interface: `org.connectbot.sshlib.HostKeyVerifier` with `suspend fun verify(key: PublicKey): Boolean` plus optional `addKeys`/`removeKeys` persistence hooks. This directly supports the "verify host key before credentials" invariant.
- **Fingerprints:** `KeyFingerprint.kt` provides fingerprint support for trust-on-first-use and key-change warnings.
- **Algorithm policy:** `crypto/Algorithms.kt`, `SignatureAlgorithms.kt`, `KexAlgorithm.kt` expose algorithm selection, supporting "modern algorithms; disable legacy by default".
- **Interactive shell / PTY:** `client/SessionChannel.kt`, `SshConnection.kt`, `ChannelDelivery.kt`.
- **SFTP v3:** `SftpClient.kt`, `client/sftp/SftpClientImpl.kt`, `protocol/SftpStateMachine.kt` (+ formal model).
- **Port forwarding:** `client/LocalPortForwarder.kt`, `client/RemotePortForwarder.kt`, `client/DynamicPortForwarder.kt` (SOCKS), `client/Socks5Handler.kt`, `PortForwarder.kt`.
- **Agent forwarding:** `AgentProvider.kt`, `client/AgentChannel.kt`, `client/AgentProtocolHandler.kt`.
- **Crypto primitives:** Ed25519, Ed448, ECDSA, RSA (SHA-2), and modern ML-DSA/SK signature classes.

**Security:** No GitHub Security Advisory (GHSA) entries for `org.connectbot.sshlib:sshlib` (expected — it is a relatively new Kotlin artifact). No `security`-labelled issues in `connectbot/cbssh`. Mitigations in place: Apache-2.0, active CI with quality gate, SLSA L3 claim.

**Caveats.**
- Verify the POM transitive tree (kotlinx-coroutines, Kaitai runtime, KStateMachine) is compatible with the app's Compose/AndroidX versions.
- Confirm minimum Android API level against the app's chosen `minSdk`.
- **Pending CI:** a real Gradle compile + instrumented host-key test.

## 3. Android — ConnectBot termlib (`org.connectbot:termlib`)

**Licence:** Apache-2.0 (project `connectbot/termlib`); embeds **libvterm** (MIT).
**Maintenance:** Active. Maven Central `latest` = **0.3.14**; repo pushed 2026-11-10; releases 0.3.13 (2026-10-12), 0.3.12, 0.3.11.
**Coordinates:** `org.connectbot:termlib` (groupId `org.connectbot`, artifactId `termlib`; namespace `org.connectbot.terminal`). Confirmed present on Maven Central (metadata HTTP 200).

**API compatibility.** Jetpack Compose component ("ConnectBot's terminal emulator Android Compose component using libvterm"), matching the approved Compose stack. Features confirmed from the project README: 256-colour and true colour, East Asian double-width characters, combining characters, text selection, scrolling, zoom, dynamic resize, multiple fonts, inline images (iTerm2/Kitty), complex-script shaping.

**Gaps to implement ourselves (per owner instruction).** The README lists as *planned*: pasting support, forced-size terminal, shell-prompt integration, URL/error scanning. RSS Netrix must implement any of these it requires (notably **paste** and **forced-size**) on top of termlib.

**Security:** No GHSA entries; libvterm is a small, long-standing MIT emulation core. Termlib performs no networking (rendering only), limiting its attack surface.

**Caveats.** Native (JNI/C++) component: confirm ABIs (`arm64-v8a`, `armeabi-v7a`, `x86_64`) and NDK build support. **Pending CI:** compile and render test on an emulator/device.

## 4. Windows — SSH.NET (`Renci.SshNet`)

**Licence:** MIT.
**Maintenance:** Active; NuGet `2026.0.0`; repository pushed 2026-11-03.
**Targets:** .NET Standard 2.0 and .NET 8+ (compatible with .NET 10).

**Security (decisive constraint).**
| Advisory | Severity | Affected | Patched |
|---|---|---|---|
| GHSA-mggc-4xg6-vcxf — SCP server-side RCE via default SCP path handling | High | `< 2026.0.0` | **2026.0.0** |
| GHSA-q939-rpr3-3284 — SCP recursive download arbitrary file write via server-controlled filenames | High | `<= 2025.1.0` | **2026.0.0** |

Both are in `ScpClient`. **Pin >= 2026.0.0.** Independently, RSS Netrix should prefer **SFTP** over SCP, which sidesteps this class of issue entirely.

**API compatibility (verified).**
- **Host-key verification:** `BaseClient` exposes `public event EventHandler<HostKeyEventArgs> HostKeyReceived`; `HostKeyEventArgs` provides `CanTrust` (settable bool), `HostKey`, `HostKeyName`, `FingerPrintSHA256`, `KeyLength`, `Certificate`. Setting `CanTrust = false` refuses the connection — exactly what the "verify before credentials / reject changed key" invariant needs.
- **Interactive shell:** `Renci.SshNet.ShellStream`.
- **SFTP:** `SftpClient` (sync + async).
- **Port forwarding:** `Renci.SshNet.ForwardedPort` — remote, dynamic and local.

**Caveats.** Review the `HostKeyEventArgs` default (`CanTrust` defaults to `true`), so the client **must** actively set it and must not rely on the default. **Pending CI:** `dotnet build`/`dotnet test` on a Windows runner.

## 5. Windows — Microsoft.WindowsAppSDK and .NET

- `Microsoft.WindowsAppSDK` latest stable **2.6.5** (MIT); requires Windows 10 1809+.
- .NET **10 LTS** current (`10.0.14`), supported runtime.
- **Terminal rendering:** no first-party, supported, redistributable NuGet terminal control exists (`Microsoft.Terminal.Control`/`.Wpf` are not on NuGet). Plan: implement an RSS Netrix VT renderer over a proven emulation core (**libvterm**, MIT, or **VtNetCore**, MIT) and render via WinUI/Skia. Third-party re-packagings exist but are unofficial and low-adoption — not approved.
- **Pending CI:** `dotnet build` + WinUI smoke test on a Windows runner.

## 6. Cross-cutting dependency/licence policy

Adopted gate: **permissive licence (MIT/Apache-2.0/BSD) + actively maintained + no unpatched advisory affecting our usage.** All selected dependencies satisfy this. See `../../THIRD_PARTY_NOTICES.md`.

## 7. Outstanding validation (requires a full toolchain / CI)

| ID | Item | Status |
|---|---|---|
| V-01 | Android Gradle compile with cbssh + termlib | Pending CI |
| V-02 | cbssh host-key verify-before-credentials integration test | Pending CI |
| V-03 | termlib render test (256/true colour, resize, paste implementation) | Pending CI |
| V-04 | Windows `dotnet build` + SSH.NET host-key callback test | Pending CI |
| V-05 | WinUI 3 smoke test and minimum Windows version confirmation | Pending CI |
| V-06 | Transitive dependency tree + hash lockfiles for both platforms | Pending |
| V-07 | Dependency vulnerability scan wired into CI | Pending |

**Conclusion.** All four approved decisions are validated at the level obtainable without a toolchain: coordinates, licences, maintenance and public APIs are confirmed, and the one material advisory (SSH.NET SCP) is mitigated by pinning >= 2026.0.0. Full build validation (V-01…V-07) is deferred to CI and will be reported factually when a toolchain is available.
