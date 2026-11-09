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


## ADR-009: RSS Netrix Free/Premium feature placement
**Status:** Accepted for planning  
The owner approved the feature split recorded in [FEATURE_PARITY_SPEC.md](FEATURE_PARITY_SPEC.md). Free includes core local SSH, secure local credential storage, terminal tabs/basic splits, all terminal themes and custom colour controls, terminal file attachment/path insertion, basic SFTP, basic tunnels, basic history/snippets and basic host import/export. Premium is planned for advanced workspaces/productivity, advanced SFTP, encrypted multi-device sync, team vaults, live collaboration and team audit/administration. Additional protocols and advanced authentication integrations remain unassigned pending feasibility review. This ADR does not approve prices, trial terms, renewal, device limits, payment provider, licence enforcement details or paid infrastructure.
