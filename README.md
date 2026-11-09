# RSS Netrix

**RSS Netrix** is an independently developed SSH and remote-server management client by Razeen Secure Solution.

- Android application ID: `com.riyaz.rssnetrix`
- Windows display name: `RSS Netrix`
- Repository: `riyazamra1/RSS-Netrix`

## Product direction

RSS Netrix aims to provide a polished, cross-device workflow for managing SSH hosts and remote systems. Its planned capabilities include:

- Interactive SSH terminal sessions and saved host profiles
- Multi-session tabs and split workspaces
- SFTP file browsing and transfers
- Local, remote and dynamic SSH port forwarding
- SSH key management and an encrypted credential vault
- Command snippets, recent command history and session logs
- Optional encrypted cloud synchronization

The interface, source code, product identity and assets will be original RSS work. The project may study publicly observable workflows and documented protocols in competing products, but will not copy proprietary source code, protected assets or branding.

## Platforms

- **Android:** Native Kotlin and Jetpack Compose.
- **Windows:** Native Windows desktop application (proposed foundation: .NET 10 with WinUI 3; validate SSH/SFTP library compatibility before locking dependencies).
- Shared protocol, security and product specifications will be maintained where practical. Platform-specific UI and secure storage remain native.

## Security principles

1. Never store plaintext passwords or private keys in source control.
2. Use platform secure storage for local secrets (Android Keystore-backed storage; Windows DPAPI/Credential Locker-backed storage).
3. Encrypt synchronizable data on the client before upload; use authenticated encryption such as AES-256-GCM with unique nonces and versioned envelopes.
4. Keep cloud authorization and key-management secrets in restricted server-side secret storage, never in APKs, EXEs, public workflows, logs or artifacts.
5. Treat GitHub Actions and every build dependency as part of the trusted computing base. Do not expose secrets to untrusted pull requests.
6. Do not claim that source encryption prevents reverse engineering of released binaries.
7. Document key rotation, recovery, revocation and data deletion before enabling production sync.

## Cost target

The initial development target is **$0/month**, using eligible free tiers where practical. This is a target, not a guarantee: quotas, service terms and pricing can change. Cloud resources must have usage monitoring, budget alerts where available, and safe failure behaviour. No paid resource should be provisioned without explicit approval.

## Delivery principles

- Finalize requirements and architecture before feature implementation.
- Review the complete change list before each commit.
- Keep commits consolidated and deployments sequential.
- Run platform-specific builds, tests and security checks before reporting success.
- Verify the actual release artifact and relevant functionality; never infer success from a queued workflow.

## Status

This repository is at the initial foundation stage. No production SSH client, cloud synchronization service, credentials, encryption master key, or deployment infrastructure is represented as complete.

See [docs/FEATURE_PARITY_SPEC.md](docs/FEATURE_PARITY_SPEC.md) for the comprehensive feature scope and approved Free/Premium feature split. The supporting [product specification](docs/PRODUCT_SPEC.md), [architecture](docs/ARCHITECTURE.md), [security design](docs/SECURITY.md), [roadmap](docs/ROADMAP.md), and [architecture decisions](docs/DECISIONS.md) define the implementation constraints and delivery gates.
