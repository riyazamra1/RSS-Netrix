# RSS Netrix — Core Platform-Neutral Contracts

**Status:** Specification for review
**Applies to:** Android and Windows implementations
**Scope:** Product-level contracts only. No proprietary implementation source. This document defines behaviour and invariants that both platforms must honour so security properties stay identical across platforms.

---

## 1. Principles

1. **Security invariants are shared; UI is native.** Android (Kotlin/Compose) and Windows (.NET 10/WinUI 3) implement the same contracts independently.
2. **Fail closed.** Any state that cannot be proven safe must refuse to proceed rather than degrade silently.
3. **Explicit state.** Connection, trust and transfer states are modelled and surfaced, never inferred.
4. **No plaintext secrets** in persistence, logs, analytics, crash reports or clipboard history.
5. **Free tier is local-first.** Core SSH, secure local credentials and terminal operation must not require cloud availability.

---

## 2. Host profile model

A host profile is non-secret metadata plus a reference to credential material stored in the vault.

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | yes | Stable, client-generated |
| `displayName` | string | yes | User-facing label |
| `hostname` | string | yes | Hostname or IP; validated, no control characters |
| `port` | int | yes | Default 22; range 1–65535 |
| `username` | string | no | May come from identity |
| `authMethod` | enum | yes | `password` \| `privateKey` \| `agent` \| `keyVault` |
| `identityRef` | UUID | no | Reference to a vault identity |
| `credentialRef` | UUID | no | Reference to a vault secret record |
| `jumpHostRef` | UUID | no | Reference to another host profile (chain) |
| `connectTimeoutMs` | int | no | Bounded range |
| `groupIds` | UUID[] | no | Grouping |
| `tags` | string[] | no | Free-form, searchable |
| `notes` | string | no | Non-secret |
| `terminalPrefs` | object | no | Font/theme reference by id |
| `envVars` | map | no | Non-secret by policy; warn on secret-looking values |

**Invariants**
- A host profile never contains a password, private key or passphrase in plaintext.
- Deleting a host does not silently delete a shared vault secret referenced by other hosts.
- Import/export excludes secret material by default and requires explicit opt-in with encryption.

## 3. Connection lifecycle state machine

```
Created
  → Resolving
  → Connecting
  → HostKeyVerification
  → Authenticating
  → Ready
  → Reconnecting ──┐
  → Closing        │
  → Closed         │
  → Failed ◄───────┘
```

**Transitions and invariants**
- `HostKeyVerification` **must complete before** any credential is transmitted. This is absolute.
- A host key that is unknown requires explicit trust-on-first-use confirmation; a host key that **changed** must never be auto-accepted and must surface a prominent warning with fingerprint comparison.
- `Reconnecting` re-enters `HostKeyVerification`; a changed key aborts the reconnect.
- Cancellation from any state closes transport resources deterministically.
- UI lifecycle changes (background/foreground, window close) must not silently duplicate or orphan sessions.
- Every failure carries a typed error (see §7) and never a raw secret.

## 4. Known-hosts trust store

| Field | Type | Notes |
|---|---|---|
| `host` | string | Canonical hostname or `[ip]:port` |
| `keyType` | string | e.g. `ssh-ed25519`, `rsa-sha2-256` |
| `fingerprint` | string | SHA-256, base64 |
| `trustedAt` | timestamp | |
| `decision` | enum | `trusted` \| `changed` \| `revoked` |

**Invariants**
- Lookup is by `host` + `keyType`; a mismatch for a trusted host is a `changed` event, never a silent replacement.
- The store is user-visible and user-editable (remove/revoke).
- Modern algorithms preferred; legacy algorithms disabled by default (see §8).

## 5. Credential vault contract

The vault stores secret material only through platform-protected storage. See `VAULT_THREAT_MODEL.md` for the security design.

**Operations**
- `generateKey(type, params)` → public key + `secretRef`
- `importKey(format, bytes, passphrase?)` → public key + `secretRef`
- `storePassword(hostRef, password)` → `secretRef`
- `getSecret(secretRef)` → secret bytes (requires re-auth where configured)
- `listIdentities()` → non-secret metadata + public keys + fingerprints
- `deleteSecret(secretRef)` / `revokeLocal(secretRef)`

**Invariants**
- Secrets are encrypted with a key protected by Android Keystore / Windows DPAPI-Credential Locker.
- Secrets are never returned in list/metadata operations.
- Export/reveal of private material requires an explicit user action and re-authentication where the platform supports it.
- Deleting a local key is local removal only; the UI must never claim remote revocation.
- Transient secret buffers are cleared as far as the runtime allows.

## 6. Transfer (SFTP) model

States: `Queued → Active → Paused? → Completed` | `Cancelled` | `Failed`.

**Invariants**
- Destructive operations (overwrite, delete, move over existing) require explicit confirmation.
- Partial transfers never masquerade as complete; resume verifies remote size/state before continuing.
- Cancellation stops transfer and cleans up partial local artifacts.
- Local and remote path namespaces are always visually distinct.
- Transfers are bound to a session's lifetime or a documented user-selected policy.

## 7. Error taxonomy

| Category | Examples | Handling |
|---|---|---|
| `NetworkError` | DNS failure, timeout, reset | Retry affordance, no secret in message |
| `HostKeyError` | unknown key, changed key | Block, warn, require decision |
| `AuthError` | bad credentials, key rejected | Re-prompt; never log credential |
| `PermissionError` | bind denied, remote EACCES | Surface cause, no silent retry |
| `TransferError` | disk full, remote closed | Report, keep partial state safe |
| `ConfigError` | invalid port, malformed key | Validate before attempt |
| `InternalError` | unexpected | Redacted report; no secrets |

**Invariant:** error messages and telemetry never contain passwords, private keys, passphrases or unredacted authentication exchanges.

## 8. Cryptography policy (client)

- Prefer modern algorithms; disable obsolete algorithms by default:
  - Key exchange: curve25519-sha256, ecdh-sha2-nistp256/384/521
  - Host keys: ssh-ed25519, ecdsa, rsa-sha2-256/512 (SHA-1 `ssh-rsa` disabled by default)
  - Ciphers: chacha20-poly1305, aes*-gcm, aes*-ctr
  - MACs: hmac-sha2-256/512, encrypt-then-MAC preferred
- Local secret encryption: platform-protected keys; authenticated encryption for synchronizable envelopes (see sync spec, later phase).
- Never invent a cryptographic construction; use reviewed library primitives.

## 9. Command history and snippets

- History retains at least the 10 most recent commands per session/host context.
- Selecting a history item or snippet **copies** it; it never auto-executes.
- Snippet execution in a terminal requires a deliberate confirming action.
- History/log capture is opt-in, clearly indicated, with retention and deletion controls and redaction of authentication secrets.

## 10. Port forwarding

- Types: local, remote, dynamic (SOCKS).
- Validate local/remote endpoints before binding; surface bind/permission failures with cause.
- Tunnels stop when their owning session closes unless a documented alternative policy is selected.
- Active tunnels display bound endpoints and state.

## 11. Compatibility with Free/Premium allocation

This contract set covers Free-tier behaviour. Premium capabilities (advanced workspaces, multi-host execution, encrypted sync, team features) build on these contracts and must not weaken any invariant above. See `FEATURE_PARITY_SPEC.md`.
