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

## ADR-009: Encrypted source bundle and key separation
**Status:** Proposed; prototype and security review required  
Public source payloads will be encrypted before commit. Source encryption keys, cloud-sync keys and code-signing keys are separate. The bundle format and algorithm suite remain open pending a tested, versioned authenticated-encryption prototype. No key or encrypted bundle is created by this ADR.

## ADR-010: Single-public-repository trusted build
**Status:** Proposed; implementation and security review required  
Keep one public repository and do not rely on a separate private build-control repository. Ordinary public CI is secret-free. Any future decryption/release workflow must use protected approvals, immutable reviewed commit binding, least privilege and ephemeral runners. Public workflow code and maintainers remain trusted; GitHub secrets do not prevent malicious privileged workflow code from exfiltrating plaintext. No workflow, secret, key, runner or cloud resource is provisioned by this ADR.

## ADR-011: Free/Premium product and official distribution
**Status:** Accepted  
RSS Netrix includes a defined Free feature tier and paid Premium features. GitHub is not a customer download channel and must not host public APK, EXE, MSIX or installer release assets. Android customers obtain the app through the official RSS website or Google Play Store; Windows customers through the official RSS website or Microsoft Store, subject to channel readiness and store policies. Premium entitlements require valid licence validation and device controls. Free features do not imply unrestricted GitHub downloads.
