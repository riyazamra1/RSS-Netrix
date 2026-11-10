# RSS Netrix — Architecture Decision Records

## ADR-001: Product identity
**Status:** Accepted  
Use RSS Netrix as the product name and `com.riyaz.rssnetrix` as the Android application ID. Preserve Razeen Secure Solution branding and use original product assets and interface design.

## ADR-002: Native platform applications
**Status:** Accepted direction  
Android will be native Kotlin/Jetpack Compose. Windows will be a native Windows desktop application, not a browser wrapper. The current Windows framework candidate is modern .NET with WinUI 3; final selection is gated on library compatibility, packaging and supported Windows versions.

## ADR-003: Independent SSH implementation
**Status:** Accepted  
Implement protocol workflows independently using documented SSH/SFTP standards and appropriately licensed libraries. Competitive product research may inform feature parity, but proprietary code, assets, branding and protected implementation details will not be copied.

## ADR-004: Local-first credentials
**Status:** Accepted  
SSH credentials and private keys remain local by default and use platform-protected storage. Basic SSH functionality must not depend on RSS Core or cloud sync.

## ADR-005: Encrypted cloud sync
**Status:** Proposed; implementation deferred  
Cloud sync is optional. Client-side authenticated encryption is required before upload. Cloudflare R2 and Workers are candidates for a $0/month target, subject to current free-tier limits and explicit provisioning approval. No infrastructure or secrets are created by this decision.

## ADR-006: Public repository and encrypted source
**Status:** Accepted constraint; implementation deferred  
The repository is public. Product documentation/build metadata may be public, but application source payloads must be encrypted at rest in the repository as previously requested. Do not commit plaintext app source until the trusted decryption/build workflow has been designed, reviewed and tested. Public release binaries can still be reverse engineered.

## ADR-007: Cost discipline
**Status:** Accepted  
Target $0/month during development. Do not provision paid services without approval. Free-tier availability and quotas are not guaranteed; enforce quotas and safe failure behaviour.

## ADR-008: Delivery discipline
**Status:** Accepted  
Requirements first; show change list before commits; consolidate changes; run only one deployment at a time; verify actual builds and functionality before reporting success.

## ADR-009: Proprietary licence and third-party notices
**Status:** Accepted
RSS Netrix is proprietary commercial software owned by Razeen Secure Solution and is licensed "all rights reserved". Do not apply MIT, Apache-2.0 or any other permissive licence to RSS Netrix application code. Public availability of the repository grants no licence. All third-party dependency licences and notices are preserved and recorded in `THIRD_PARTY_NOTICES.md`. See `LICENSE`.

## ADR-010: Single public repository with encrypted proprietary source
**Status:** Accepted
Keep the single public repository `riyazamra1/RSS-Netrix`. Proprietary application source is never committed in plaintext to any public branch, artifact, log or release. Application source is developed in an isolated, access-controlled workspace and is admitted to the public repository only as an approved encrypted bundle. See `docs/SOURCE_HANDLING_POLICY.md`.

## ADR-011: Encrypted source is a parallel workstream, not a development blocker
**Status:** Accepted
Ordinary development proceeds independently of the encrypted-source workstream. A strict security gate applies at all times: no plaintext proprietary source in public GitHub commits, public artifacts, logs or releases, and no production decryption or source-bearing CI/CD until the encrypted-source security design is reviewed and approved by the owner. The gate is never bypassed for convenience.

## ADR-012: Dependency selection
**Status:** Accepted for evaluation; final lock gated on validation
- Android: ConnectBot cbssh (`org.connectbot.sshlib`) for SSH/SFTP/forwarding, and ConnectBot termlib (`org.connectbot:termlib`) for the terminal emulator. Any missing terminal functionality is implemented by RSS Netrix.
- Windows: SSH.NET (`Renci.SshNet`) at version 2026.0.0 or a newer compatible stable release, on .NET 10 with WinUI 3.
- Final lock is subject to dependency, licensing, API-compatibility, security and build validation. Known constraint: SSH.NET SCP path-handling advisories are fixed only in 2026.0.0, so earlier versions must not be used.
- All selected components are permissively licensed and preserved in `THIRD_PARTY_NOTICES.md`.

## ADR-013: Native platform applications, no WebView shell
**Status:** Accepted (confirms ADR-002)
Android remains native Kotlin and Jetpack Compose; Windows remains a native Windows desktop application on .NET 10 and WinUI 3. A WebView must not be the primary application shell on either platform.

## ADR-014: Cost and provisioning discipline
**Status:** Accepted (confirms ADR-007)
Continue the $0/month infrastructure target. Do not create paid resources, accounts, secrets, infrastructure or signing credentials without explicit owner approval. Do not publish APKs, installers or proprietary source publicly.

## ADR-015: Phased delivery, tests and factual reporting
**Status:** Accepted (extends ADR-008)
Continue development in independently reviewable phases, each with automated tests where practical and a factual progress report that states the commit SHA and exact build/test statuses. Do not merge any pull request or release a production build without explicit owner approval.

