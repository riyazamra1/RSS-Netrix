# RSS Netrix — Credential and Vault Recovery Model

**Status:** Specification for review
**Scope:** User-controlled recovery of local vault material and (later) encrypted sync material.
**Related:** `VAULT_THREAT_MODEL.md`, `SECURITY.md` §4.

---

## 1. Principles

1. **User-controlled.** RSS cannot recover a user's secrets on the user's behalf; there is no server-side escrow.
2. **Explicit.** Recovery setup is opt-in and clearly explained; the consequence of loss is stated plainly.
3. **No silent weakening.** Recovery must not reduce the strength of the vault or sync encryption.
4. **Tested.** Recovery is only "supported" after a successful rehearsal.

## 2. Recovery options

### 2.1 Recovery phrase (recommended)
- On vault creation, optionally generate a high-entropy recovery phrase (or key file).
- The phrase wraps the vault master key using a reviewed, memory-hard KDF.
- The phrase is shown once, with an explicit "I have stored this safely" acknowledgement.
- The phrase is never uploaded, logged or emailed.

### 2.2 User passphrase
- User may set a passphrase that derives a wrapping key (Argon2id) for the master key.
- Passphrase strength is evaluated; weak passphrases are warned against, not silently accepted.

### 2.3 Platform backup (limited)
- If the OS provides encrypted, credential-protected backup, it may carry vault material **only** while it remains encrypted and protected by the platform key.
- Vault material is excluded from ordinary, unprotected backups.

## 3. What cannot be recovered

- A lost vault master key with no recovery phrase/passphrase means the secrets are unrecoverable.
- RSS cannot reset a user's vault remotely.
- Deleting a local key does not revoke it on any remote server (see `CORE_CONTRACTS.md` §5).

## 4. Rotation and revocation

| Action | Effect |
|---|---|
| Rotate vault key | Re-wrap records under a new master key; bounded old/new overlap |
| Remove device (sync, later) | Server stops serving that device's data; client key material wiped |
| Revoke local key | Local removal only; user must separately remove from `authorized_keys`/certificate authority |

## 5. Interaction with encrypted sync (later phase)

- Sync keys and vault keys are **separate cryptographic domains** (`SOURCE_PROTECTION.md` §3).
- Sync recovery uses the same user-controlled phrase/passphrase approach.
- Secrets/private keys are excluded from sync by default until this recovery model is available and approved.

## 6. Acceptance tests

1. Recovery phrase restores vault on a clean install.
2. Wrong recovery phrase fails closed.
3. Passphrase-derived wrapping matches on both platforms.
4. Rotation rehearsal passes without data loss.
5. Removing a device (sync) wipes that device's key material.
6. Documentation accurately states what is and is not recoverable.
