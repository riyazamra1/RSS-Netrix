# RSS Netrix — Foundation Specifications

**Status:** Specification set for review
**Scope:** Platform-neutral contracts and product specifications. No proprietary implementation source.

These specifications define the behaviour and security invariants that both the Android and Windows implementations must honour. They are deliberately implementation-neutral so the proprietary source can be developed separately (see `../SOURCE_HANDLING_POLICY.md`).

| Document | Purpose |
|---|---|
| [CORE_CONTRACTS.md](CORE_CONTRACTS.md) | Host model, connection lifecycle, trust store, vault, transfer, error taxonomy, crypto policy |
| [VAULT_THREAT_MODEL.md](VAULT_THREAT_MODEL.md) | Local credential vault threats, controls and acceptance tests |
| [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) | Original RSS design system, core screens and UX rules |
| [RECOVERY_MODEL.md](RECOVERY_MODEL.md) | User-controlled credential and vault recovery |

Related product documents:
- [../PRODUCT_SPEC.md](../PRODUCT_SPEC.md)
- [../ARCHITECTURE.md](../ARCHITECTURE.md)
- [../SECURITY.md](../SECURITY.md)
- [../ROADMAP.md](../ROADMAP.md)
- [../DECISIONS.md](../DECISIONS.md)

## Status of each spec

| Spec | Status |
|---|---|
| Core contracts | Draft for review |
| Vault threat model | Draft for review |
| Design system | Draft for review |
| Recovery model | Draft for review |

These are drafts pending owner review. They do not authorise implementation of Premium sync/team features, which remain gated on the key-hierarchy and server-side authorization designs.
