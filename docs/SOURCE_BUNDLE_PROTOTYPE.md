# Source Bundle Encryption Prototype

**Status: experimental prototype only — not approved for production source protection.**

## Purpose

This utility encrypts an already-created source archive file. It does not create archives, inspect their contents, extract them, create keys, manage key rotation or provide a secure build runner. The application source is not present in this repository yet.

## Format

- AES-256-GCM authenticated encryption.
- A fresh random 256-bit data-encryption key (DEK) per bundle.
- A separate 256-bit key-encryption key (KEK), supplied out-of-band, wraps the DEK using AES-GCM.
- Independent 96-bit nonces for payload and DEK wrapping.
- Canonical JSON header authenticated as associated data.
- Key identifier is metadata only; it is not a key or secret.
- Prototype payload size is limited to 512 MiB because this implementation uses one-shot in-memory AEAD operations.

The wrapping key must be 32 cryptographically random bytes encoded as base64 in the environment variable \`RSS_SOURCE_KEK\`. Never commit the value, place it in an application, or pass it in a command-line argument. This prototype does not provision or store any key.

## Setup

Use Python 3.11 or newer in a clean virtual environment:

\`\`\`sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-source-prototype.txt
\`\`\`

Generate a temporary test key locally (do not use this key for production):

\`\`\`sh
python -c "import base64,secrets; print(base64.b64encode(secrets.token_bytes(32)).decode())"
\`\`\`

Set it only in the current local shell:

\`\`\`sh
export RSS_SOURCE_KEK='BASE64_TEST_KEY'
\`\`\`

Encrypt an archive:

\`\`\`sh
python tools/source_bundle.py encrypt source-archive.tar source-archive.rssenc --key-id test-key-v1
\`\`\`

Decrypt it for a round-trip test:

\`\`\`sh
python tools/source_bundle.py decrypt source-archive.rssenc restored-archive.tar
cmp source-archive.tar restored-archive.tar
\`\`\`

Run tests:

\`\`\`sh
python -m unittest discover -s tests -v
\`\`\`

## Security boundaries and limitations

- This is not a production key-management system. It has no hardware-backed key custody, KMS integration, rotation, revocation, audit service or protected workflow.
- The caller is responsible for creating and validating the archive. Do not extract untrusted archives without separate path traversal, symlink, duplicate-entry and decompression-bomb protections.
- The tool reads the complete input and output into memory; do not use it for large production source trees.
- A compromised machine or process can read the KEK and plaintext.
- It does not prevent a build script or dependency from exfiltrating source after decryption.
- The KEK must be a randomly generated 32-byte value. Do not use a human password as the key.
- Production adoption requires independent cryptographic review, key custody and recovery design, streaming support, archive validation, workflow isolation, negative tests and verified cleanup.
- Do not add plaintext application source, production keys or customer binaries to the public repository.
