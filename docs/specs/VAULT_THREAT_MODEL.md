# RSS Netrix — Credential Vault Threat Model

**Status:** Specification for review
**Scope:** Local credential vault on Android and Windows. Cloud sync is out of scope here and covered in a later phase.
**Related:** `CORE_CONTRACTS.md` §5, `SECURITY.md`.

---

## 1. Purpose

Define what the local vault protects, what it does not, and the controls required so that SSH credentials and private keys never exist in plaintext outside platform-protected storage.

## 2. Assets

- SSH passwords
- Private keys (OpenSSH/PEM and platform formats)
- Key passphrases
- Reusable identities
- Host metadata that may reveal infrastructure (treated as sensitive-but-not-secret)

## 3. Trust boundaries

| Boundary | Inside | Outside (untrusted) |
|---|---|---|
| Device secure hardware / OS keystore | Keystore/DPAPI keys, wrapping keys | — |
| App process memory | Decrypted secrets transiently | — |
| App storage | Encrypted vault records | — |
| UI | Redacted display | Clipboard, screenshots, logs, analytics, crash reports |
| Network | — | Everything; secrets never transmitted |

## 4. Threats and controls

| ID | Threat | Control |
|---|---|---|
| V-01 | Device loss/theft | Secrets encrypted with hardware-protected keys; optional biometric/device-credential gating |
| V-02 | Malware with app privileges | Platform sandbox; minimise plaintext lifetime; clear buffers; no plaintext files |
| V-03 | Plaintext secret in storage | Vault records are AEAD ciphertext; keys never stored beside ciphertext |
| V-04 | Secret in logs/crash/analytics | Redaction; never log secret material; scrub exception paths |
| V-05 | Secret in clipboard history | Do not place secrets on clipboard by default; warn if user copies |
| V-06 | Screenshot/overlay capture | Mark secret screens as non-capturable where the platform allows |
| V-07 | Backup exfiltration | Exclude vault material from OS backups by default, or ensure it remains encrypted |
| V-08 | Weak KDF for user passphrase | Use a reviewed, memory-hard KDF (e.g. Argon2id) if a user passphrase is used |
| V-09 | Key confusion across purposes | Separate vault key from sync key and signing keys (see `SOURCE_PROTECTION.md`) |
| V-10 | Silent remote-revocation claim | UI states clearly that local deletion is not remote revocation |
| V-11 | Unauthorised export | Re-authentication before reveal/export of private material |
| V-12 | Downgrade to weak algorithms | Modern algorithm defaults; legacy disabled with warning |

## 5. Cryptographic design (per platform)

**Android**
- Generate a per-installation master key in the Android Keystore (non-exportable), gated by device credential/biometric as an optional policy.
- Encrypt each vault record with AES-256-GCM using a unique nonce; store ciphertext + nonce + versioned envelope in app-private storage.
- If a user passphrase is used for portability, derive a wrapping key with Argon2id and wrap the master key.

**Windows**
- Protect the master key with DPAPI (current user scope) or Credential Locker.
- Encrypt vault records with AES-256-GCM using a unique nonce; versioned envelope.
- Optional Windows Hello gating where supported by the chosen native API.

**Shared envelope requirements**
- Unique nonce per encryption; never reuse a nonce under the same key.
- Authenticated metadata (record id, version, purpose) as associated data.
- Strict envelope validation; reject unknown versions and malformed records.
- Versioned format to allow future rotation.

## 6. Key lifecycle

- **Generation:** cryptographically secure RNG only.
- **Storage:** platform-protected; never in the repository, workflows, logs or artefacts.
- **Rotation:** define and test re-wrapping; keep old/new overlap bounded.
- **Recovery:** user-controlled; document clearly that losing the vault key loses the secrets.
- **Revocation:** local removal is immediate; remote revocation is a separate, user-driven action on the server.

## 7. Non-goals and limitations

- The vault cannot protect against a fully compromised endpoint with app privileges.
- The vault does not protect secrets that the user copies elsewhere.
- The vault does not make released binaries opaque.
- Host-key trust and transport security are separate controls (`CORE_CONTRACTS.md` §3–4).

## 8. Acceptance tests (required before the vault is called complete)

1. Secrets are ciphertext at rest (inspect storage).
2. Wrong-key and tampered-record rejection.
3. Nonce uniqueness across many encryptions.
4. Re-authentication required before export/reveal.
5. No secret in logs, crash reports, clipboard or analytics.
6. Vault key rotation rehearsal passes.
7. Backup exclusion (or encrypted backup) verified.
8. Local-deletion-vs-remote-revocation messaging verified.
