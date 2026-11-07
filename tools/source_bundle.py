#!/usr/bin/env python3
"""Prototype authenticated-encryption wrapper for an already-created source archive.

This tool encrypts one archive file; it does not create or extract archives.
The wrapping key is supplied out-of-band through RSS_SOURCE_KEK as base64 for
exactly 32 random bytes. Never commit that key or place it in a client binary.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import secrets
import struct
import sys
import tempfile
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"RSSNETRIX-SOURCE\x00\x01"
FORMAT_VERSION = 1
ALGORITHM = "AES-256-GCM"
MAX_INPUT_BYTES = 512 * 1024 * 1024
MAX_HEADER_BYTES = 16 * 1024
KEY_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
ENV_KEY_NAME = "RSS_SOURCE_KEK"


class BundleError(Exception):
    """Raised when a source bundle cannot be safely processed."""


def _load_kek() -> bytes:
    encoded = os.environ.get(ENV_KEY_NAME)
    if not encoded:
        raise BundleError(f"{ENV_KEY_NAME} is not set")
    try:
        key = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise BundleError(f"{ENV_KEY_NAME} must be valid base64") from exc
    if len(key) != 32:
        raise BundleError(f"{ENV_KEY_NAME} must decode to exactly 32 bytes")
    return key


def _canonical_json(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _atomic_write(destination: Path, data: bytes, force: bool) -> None:
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        raise BundleError(f"destination exists (use --force to replace): {destination}")
    fd, temporary_name = tempfile.mkstemp(prefix=".rssnetrix-", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if destination.exists() and not force:
            raise BundleError(f"destination appeared during write: {destination}")
        os.replace(temporary_name, destination)
    finally:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass


def encrypt_file(source: Path, destination: Path, key_id: str, force: bool = False) -> None:
    if not KEY_ID_PATTERN.fullmatch(key_id):
        raise BundleError("key id may contain only letters, digits, dot, underscore and hyphen")
    source = source.resolve()
    destination = destination.resolve()
    if source == destination:
        raise BundleError("input and output must be different files")
    plaintext = source.read_bytes()
    if len(plaintext) > MAX_INPUT_BYTES:
        raise BundleError(f"input exceeds prototype limit of {MAX_INPUT_BYTES} bytes")

    kek = _load_kek()
    dek = secrets.token_bytes(32)
    payload_nonce = secrets.token_bytes(12)
    wrap_nonce = secrets.token_bytes(12)
    wrap_aad = f"RSSNETRIX|SOURCE|WRAP|v{FORMAT_VERSION}|{key_id}".encode("ascii")
    wrapped_dek = AESGCM(kek).encrypt(wrap_nonce, dek, wrap_aad)

    header = {
        "version": FORMAT_VERSION,
        "algorithm": ALGORITHM,
        "key_id": key_id,
        "payload_nonce": base64.b64encode(payload_nonce).decode("ascii"),
        "wrap_nonce": base64.b64encode(wrap_nonce).decode("ascii"),
        "wrapped_dek": base64.b64encode(wrapped_dek).decode("ascii"),
    }
    aad = MAGIC + _canonical_json(header)
    ciphertext = AESGCM(dek).encrypt(payload_nonce, plaintext, aad)
    encoded_header = _canonical_json(header)
    if len(encoded_header) > MAX_HEADER_BYTES:
        raise BundleError("generated header exceeds format limit")
    bundle = MAGIC + struct.pack(">I", len(encoded_header)) + encoded_header + ciphertext
    _atomic_write(destination, bundle, force)


def decrypt_file(source: Path, destination: Path, force: bool = False) -> None:
    source = source.resolve()
    destination = destination.resolve()
    if source == destination:
        raise BundleError("input and output must be different files")
    bundle = source.read_bytes()
    prefix_length = len(MAGIC) + 4
    if len(bundle) < prefix_length or not bundle.startswith(MAGIC):
        raise BundleError("not a supported RSS Netrix source bundle")
    header_length = struct.unpack(">I", bundle[len(MAGIC):prefix_length])[0]
    if header_length < 2 or header_length > MAX_HEADER_BYTES:
        raise BundleError("invalid header length")
    header_start = prefix_length
    header_end = header_start + header_length
    if len(bundle) < header_end + 16:
        raise BundleError("truncated bundle")
    try:
        header = json.loads(bundle[header_start:header_end].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError("invalid bundle header") from exc
    required = {"version", "algorithm", "key_id", "payload_nonce", "wrap_nonce", "wrapped_dek"}
    if not isinstance(header, dict) or set(header) != required:
        raise BundleError("unexpected bundle header fields")
    if header["version"] != FORMAT_VERSION or header["algorithm"] != ALGORITHM:
        raise BundleError("unsupported bundle version or algorithm")
    key_id = header["key_id"]
    if not isinstance(key_id, str) or not KEY_ID_PATTERN.fullmatch(key_id):
        raise BundleError("invalid key id")

    def decode_field(name: str, expected_length: int | None = None) -> bytes:
        value = header[name]
        if not isinstance(value, str):
            raise BundleError(f"invalid {name}")
        try:
            decoded = base64.b64decode(value, validate=True)
        except Exception as exc:
            raise BundleError(f"invalid {name}") from exc
        if expected_length is not None and len(decoded) != expected_length:
            raise BundleError(f"invalid {name} length")
        return decoded

    payload_nonce = decode_field("payload_nonce", 12)
    wrap_nonce = decode_field("wrap_nonce", 12)
    wrapped_dek = decode_field("wrapped_dek", 48)
    kek = _load_kek()
    wrap_aad = f"RSSNETRIX|SOURCE|WRAP|v{FORMAT_VERSION}|{key_id}".encode("ascii")
    try:
        dek = AESGCM(kek).decrypt(wrap_nonce, wrapped_dek, wrap_aad)
        aad = MAGIC + _canonical_json(header)
        plaintext = AESGCM(dek).decrypt(payload_nonce, bundle[header_end:], aad)
    except InvalidTag as exc:
        raise BundleError("authentication failed: wrong key or modified bundle") from exc
    if len(plaintext) > MAX_INPUT_BYTES:
        raise BundleError("decrypted payload exceeds prototype size limit")
    _atomic_write(destination, plaintext, force)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Encrypt/decrypt RSS Netrix source archive bundles")
    subparsers = parser.add_subparsers(dest="command", required=True)
    encrypt_parser = subparsers.add_parser("encrypt", help="encrypt an existing archive file")
    encrypt_parser.add_argument("input", type=Path)
    encrypt_parser.add_argument("output", type=Path)
    encrypt_parser.add_argument("--key-id", required=True)
    encrypt_parser.add_argument("--force", action="store_true")
    decrypt_parser = subparsers.add_parser("decrypt", help="decrypt a bundle to an archive file")
    decrypt_parser.add_argument("input", type=Path)
    decrypt_parser.add_argument("output", type=Path)
    decrypt_parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "encrypt":
            encrypt_file(args.input, args.output, args.key_id, args.force)
        else:
            decrypt_file(args.input, args.output, args.force)
    except (BundleError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"{args.command} completed: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
