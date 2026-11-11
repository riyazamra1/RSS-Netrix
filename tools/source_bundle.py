#!/usr/bin/env python3
"""RSS Netrix source-bundle pipeline.

Production-grade authenticated-encryption tooling for proprietary source
archives. It implements the design in ``docs/SOURCE_PROTECTION.md`` and the
requirements in ``docs/ENCRYPTED_SOURCE_REVIEW.md``:

* a strict, canonical, authenticated manifest (rejects duplicate keys, unknown
  fields, wrong types, out-of-range values and trailing garbage);
* streaming chunked AES-256-GCM so large trees never load fully into memory;
* per-chunk nonces derived from a bundle-random nonce prefix and the chunk
  index, with chunk index/count/final-marker authenticated as associated data;
* a fresh random data-encryption key (DEK) per bundle, wrapped with a standard
  AES Key Wrap construction (RFC 3394) under a key-encryption key (KEK);
* a hardened archive validator/extractor that rejects traversal, absolute and
  drive-qualified paths, symlinks, special files, duplicate and case-colliding
  paths, and enforces size/count/ratio limits (decompression-bomb defence).

The KEK is supplied out-of-band through the ``RSS_SOURCE_KEK`` environment
variable as base64 for exactly 32 random bytes. Never commit that key, place it
in a client binary, or pass it on a command line.

This module intentionally performs no network access and holds no secrets.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import secrets
import struct
import sys
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterator

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.keywrap import (
    InvalidUnwrap,
    aes_key_unwrap,
    aes_key_wrap,
)

MAGIC = b"RSSNETRIX-SOURCE\x00\x02"
FORMAT_VERSION = 2
ENCRYPTION_SUITE = "AES-256-GCM-CHUNKED"
WRAP_SUITE = "AES-256-KW"  # RFC 3394
CHUNK_SIZE = 1024 * 1024  # 1 MiB plaintext chunks
NONCE_PREFIX_BYTES = 8
WRAPPED_DEK_BYTES = 40  # 32-byte DEK + 8-byte RFC 3394 integrity check value
MAX_HEADER_BYTES = 64 * 1024
MAX_PLAINTEXT_BYTES = 4 * 1024 * 1024 * 1024  # 4 GiB
MAX_CHUNKS = (MAX_PLAINTEXT_BYTES // CHUNK_SIZE) + 2
KEY_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
REVISION_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
PRODUCT_PATTERN = re.compile(r"^[a-z0-9.-]{1,64}$")
PLATFORMS = frozenset({"android", "windows", "all"})
ENV_KEY_NAME = "RSS_SOURCE_KEK"

MANIFEST_FIELDS = frozenset(
    {
        "version",
        "algorithm",
        "wrap_algorithm",
        "key_id",
        "product",
        "platforms",
        "revision",
        "bundle_id",
        "nonce_prefix",
        "wrapped_dek",
        "plaintext_length",
        "chunk_size",
        "chunk_count",
        "plaintext_sha256",
    }
)


class BundleError(Exception):
    """Raised when a source bundle cannot be safely processed."""


class ArchiveValidationError(BundleError):
    """Raised when an archive fails the safe-extraction allowlist."""


# --------------------------------------------------------------------------
# Key handling
# --------------------------------------------------------------------------
def _load_kek() -> bytes:
    encoded = os.environ.get(ENV_KEY_NAME)
    if not encoded:
        raise BundleError(f"{ENV_KEY_NAME} is not set")
    try:
        key = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise BundleError(f"{ENV_KEY_NAME} must be valid base64") from exc
    if len(key) != 32:
        raise BundleError(f"{ENV_KEY_NAME} must decode to exactly 32 bytes")
    return key


# --------------------------------------------------------------------------
# Canonical manifest encoding
# --------------------------------------------------------------------------
def _canonical_json(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _reject_duplicate_keys(pairs):
    seen: dict[str, object] = {}
    for key, val in pairs:
        if key in seen:
            raise BundleError(f"duplicate manifest key: {key}")
        seen[key] = val
    return seen


def _parse_manifest(raw: bytes) -> dict:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BundleError("manifest is not valid UTF-8") from exc
    if text != text.strip():
        raise BundleError("manifest must not have leading or trailing whitespace")
    try:
        manifest = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise BundleError("manifest is not valid JSON") from exc
    if not isinstance(manifest, dict):
        raise BundleError("manifest must be a JSON object")
    if _canonical_json(manifest) != raw:
        raise BundleError("manifest is not canonically encoded")
    return manifest


def _validate_manifest(manifest: dict) -> dict:
    if set(manifest) != MANIFEST_FIELDS:
        missing = MANIFEST_FIELDS - set(manifest)
        extra = set(manifest) - MANIFEST_FIELDS
        raise BundleError(f"unexpected manifest fields (missing={sorted(missing)}, extra={sorted(extra)})")

    if manifest["version"] != FORMAT_VERSION:
        raise BundleError("unsupported bundle version")
    if manifest["algorithm"] != ENCRYPTION_SUITE:
        raise BundleError("unsupported encryption suite")
    if manifest["wrap_algorithm"] != WRAP_SUITE:
        raise BundleError("unsupported key-wrap suite")

    key_id = manifest["key_id"]
    if not isinstance(key_id, str) or not KEY_ID_PATTERN.fullmatch(key_id):
        raise BundleError("invalid key id")

    product = manifest["product"]
    if not isinstance(product, str) or not PRODUCT_PATTERN.fullmatch(product):
        raise BundleError("invalid product identifier")

    platforms = manifest["platforms"]
    if not isinstance(platforms, list) or not platforms or not set(platforms) <= PLATFORMS:
        raise BundleError("invalid platform set")

    revision = manifest["revision"]
    if not isinstance(revision, str) or not REVISION_PATTERN.fullmatch(revision):
        raise BundleError("invalid revision identifier")

    bundle_id = manifest["bundle_id"]
    if not isinstance(bundle_id, str) or not re.fullmatch(r"[0-9a-f]{32}", bundle_id):
        raise BundleError("invalid bundle id")

    for name, expected in (
        ("nonce_prefix", NONCE_PREFIX_BYTES),
        ("wrapped_dek", WRAPPED_DEK_BYTES),
        ("plaintext_sha256", 32),
    ):
        value = manifest[name]
        if not isinstance(value, str):
            raise BundleError(f"invalid {name}")
        try:
            decoded = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise BundleError(f"invalid {name}") from exc
        if len(decoded) != expected:
            raise BundleError(f"invalid {name} length")

    for name, minimum, maximum in (
        ("plaintext_length", 0, MAX_PLAINTEXT_BYTES),
        ("chunk_size", 1, MAX_PLAINTEXT_BYTES),
        ("chunk_count", 0, MAX_CHUNKS),
    ):
        value = manifest[name]
        if not isinstance(value, int) or isinstance(value, bool):
            raise BundleError(f"invalid {name}")
        if value < minimum or value > maximum:
            raise BundleError(f"{name} out of range")

    if manifest["chunk_size"] != CHUNK_SIZE:
        raise BundleError("unsupported chunk size")

    expected_chunks = _chunk_count_for(manifest["plaintext_length"])
    if manifest["chunk_count"] != expected_chunks:
        raise BundleError("chunk count does not match plaintext length")

    return manifest


def _chunk_count_for(plaintext_length: int) -> int:
    if plaintext_length == 0:
        return 1  # a single (empty) chunk with an authentication tag
    return (plaintext_length + CHUNK_SIZE - 1) // CHUNK_SIZE


# --------------------------------------------------------------------------
# Chunk nonce derivation and AAD
# --------------------------------------------------------------------------
def _chunk_nonce(prefix: bytes, index: int) -> bytes:
    # 8-byte random prefix || 4-byte big-endian chunk index -> 12-byte GCM nonce.
    # Uniqueness holds because (prefix, index) pairs never repeat for one DEK.
    if index < 0 or index >= 2**32:
        raise BundleError("chunk index out of range")
    return prefix + struct.pack(">I", index)


def _chunk_aad(manifest_digest: str, bundle_id: str, index: int, count: int) -> bytes:
    final = 1 if index == count - 1 else 0
    # The manifest digest binds every security-relevant manifest byte into the
    # chunk authentication, so tampering with any manifest field is detected.
    return (
        f"RSSNETRIX|CHUNK|v{FORMAT_VERSION}|{manifest_digest}|{bundle_id}|{index}|{count}|{final}"
    ).encode("ascii")


def _wrap_dek(kek: bytes, dek: bytes, key_id: str, bundle_id: str) -> bytes:
    # RFC 3394 AES-KW: deterministic, integrity-checked, no nonce management.
    return aes_key_wrap(kek, dek)


def _unwrap_dek(kek: bytes, wrapped: bytes) -> bytes:
    try:
        return aes_key_unwrap(kek, wrapped)
    except InvalidUnwrap as exc:
        raise BundleError("key unwrap failed: wrong key or modified bundle") from exc


# --------------------------------------------------------------------------
# Encrypt / decrypt
# --------------------------------------------------------------------------
def _iter_plaintext_chunks(stream: BinaryIO, length: int) -> Iterator[bytes]:
    remaining = length
    while remaining > 0:
        take = min(CHUNK_SIZE, remaining)
        chunk = stream.read(take)
        if len(chunk) != take:
            raise BundleError("input truncated while reading plaintext")
        remaining -= take
        yield chunk
    if length == 0:
        yield b""


def _hash_stream(stream: BinaryIO, length: int) -> bytes:
    digest = hashlib.sha256()
    for chunk in _iter_plaintext_chunks(stream, length):
        digest.update(chunk)
    return digest.digest()


def _atomic_write_bytes(destination: Path, data: bytes, force: bool) -> None:
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


def encrypt_file(
    source: Path,
    destination: Path,
    key_id: str,
    product: str = "rss-netrix",
    platforms: list[str] | None = None,
    revision: str = "unknown",
    force: bool = False,
) -> dict:
    """Encrypt ``source`` into a versioned bundle at ``destination``.

    Returns the authenticated manifest (without secret material).
    """
    if not KEY_ID_PATTERN.fullmatch(key_id):
        raise BundleError("key id may contain only letters, digits, dot, underscore and hyphen")
    if not PRODUCT_PATTERN.fullmatch(product):
        raise BundleError("invalid product identifier")
    if not REVISION_PATTERN.fullmatch(revision):
        raise BundleError("invalid revision identifier")
    platforms = platforms or ["all"]
    if not set(platforms) <= PLATFORMS:
        raise BundleError("invalid platform set")

    source = source.resolve()
    destination = destination.resolve()
    if source == destination:
        raise BundleError("input and output must be different files")

    plaintext_length = source.stat().st_size
    if plaintext_length > MAX_PLAINTEXT_BYTES:
        raise BundleError(f"input exceeds maximum of {MAX_PLAINTEXT_BYTES} bytes")
    chunk_count = _chunk_count_for(plaintext_length)

    # First pass: hash the plaintext (streamed, constant memory).
    with source.open("rb") as stream:
        plaintext_sha256 = _hash_stream(stream, plaintext_length)

    kek = _load_kek()
    dek = secrets.token_bytes(32)
    nonce_prefix = secrets.token_bytes(NONCE_PREFIX_BYTES)
    bundle_id = secrets.token_hex(16)
    wrapped_dek = _wrap_dek(kek, dek, key_id, bundle_id)

    manifest = {
        "version": FORMAT_VERSION,
        "algorithm": ENCRYPTION_SUITE,
        "wrap_algorithm": WRAP_SUITE,
        "key_id": key_id,
        "product": product,
        "platforms": platforms,
        "revision": revision,
        "bundle_id": bundle_id,
        "nonce_prefix": base64.b64encode(nonce_prefix).decode("ascii"),
        "wrapped_dek": base64.b64encode(wrapped_dek).decode("ascii"),
        "plaintext_length": plaintext_length,
        "chunk_size": CHUNK_SIZE,
        "chunk_count": chunk_count,
        "plaintext_sha256": base64.b64encode(plaintext_sha256).decode("ascii"),
    }
    encoded_manifest = _canonical_json(manifest)
    if len(encoded_manifest) > MAX_HEADER_BYTES:
        raise BundleError("generated manifest exceeds format limit")

    aad = MAGIC + struct.pack(">I", len(encoded_manifest)) + encoded_manifest
    manifest_digest = hashlib.sha256(aad).hexdigest()
    cipher = AESGCM(dek)

    # Second pass: stream chunks straight to disk, one chunk in memory at a time.
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        raise BundleError(f"destination exists (use --force to replace): {destination}")
    fd, temporary_name = tempfile.mkstemp(prefix=".rssnetrix-", dir=destination.parent)
    try:
        with source.open("rb") as stream, os.fdopen(fd, "wb") as out:
            out.write(aad)
            for index, chunk in enumerate(_iter_plaintext_chunks(stream, plaintext_length)):
                ciphertext = cipher.encrypt(
                    _chunk_nonce(nonce_prefix, index),
                    chunk,
                    _chunk_aad(manifest_digest, bundle_id, index, chunk_count),
                )
                out.write(struct.pack(">I", len(ciphertext)))
                out.write(ciphertext)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary_name, destination)
    finally:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass

    return manifest


def _read_exact(stream: BinaryIO, count: int) -> bytes:
    data = stream.read(count)
    if len(data) != count:
        raise BundleError("bundle truncated")
    return data


def decrypt_file(source: Path, destination: Path, force: bool = False) -> None:
    source = source.resolve()
    destination = destination.resolve()
    if source == destination:
        raise BundleError("input and output must be different files")

    with source.open("rb") as stream:
        prefix = _read_exact(stream, len(MAGIC) + 4)
        if not prefix.startswith(MAGIC):
            raise BundleError("not a supported RSS Netrix source bundle")
        manifest_length = struct.unpack(">I", prefix[len(MAGIC):])[0]
        if manifest_length < 2 or manifest_length > MAX_HEADER_BYTES:
            raise BundleError("invalid manifest length")
        encoded_manifest = _read_exact(stream, manifest_length)
        manifest = _validate_manifest(_parse_manifest(encoded_manifest))
        aad = prefix + encoded_manifest
        manifest_digest = hashlib.sha256(aad).hexdigest()

        kek = _load_kek()
        dek = _unwrap_dek(kek, base64.b64decode(manifest["wrapped_dek"]))
        nonce_prefix = base64.b64decode(manifest["nonce_prefix"])
        bundle_id = manifest["bundle_id"]
        chunk_count = manifest["chunk_count"]
        expected_sha = base64.b64decode(manifest["plaintext_sha256"])

        cipher = AESGCM(dek)
        digest = hashlib.sha256()
        total = 0
        destination = destination.resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and not force:
            raise BundleError(f"destination exists (use --force to replace): {destination}")
        fd, temporary_name = tempfile.mkstemp(prefix=".rssnetrix-", dir=destination.parent)
        try:
            with os.fdopen(fd, "wb") as out:
                for index in range(chunk_count):
                    length = struct.unpack(">I", _read_exact(stream, 4))[0]
                    if length < 16 or length > CHUNK_SIZE + 16:
                        raise BundleError("invalid chunk length")
                    ciphertext = _read_exact(stream, length)
                    try:
                        plaintext = cipher.decrypt(
                            _chunk_nonce(nonce_prefix, index),
                            ciphertext,
                            _chunk_aad(manifest_digest, bundle_id, index, chunk_count),
                        )
                    except InvalidTag as exc:
                        raise BundleError("authentication failed: wrong key or modified bundle") from exc
                    digest.update(plaintext)
                    total += len(plaintext)
                    if total > MAX_PLAINTEXT_BYTES:
                        raise BundleError("decrypted payload exceeds maximum size")
                    out.write(plaintext)
                trailing = stream.read(1)
                if trailing:
                    raise BundleError("trailing data after final chunk")
                out.flush()
                os.fsync(out.fileno())

            if total != manifest["plaintext_length"]:
                raise BundleError("decrypted length does not match manifest")
            if digest.digest() != expected_sha:
                raise BundleError("decrypted digest does not match manifest")
            os.replace(temporary_name, destination)
        except BaseException:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise
        finally:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass


# --------------------------------------------------------------------------
# Safe archive extraction
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ExtractionLimits:
    max_entries: int = 200_000
    max_total_uncompressed: int = 8 * 1024 * 1024 * 1024
    max_single_uncompressed: int = 2 * 1024 * 1024 * 1024
    max_ratio: int = 400  # uncompressed / compressed
    max_path_length: int = 1024
    max_depth: int = 64


def _safe_relative_member(name: str, limits: ExtractionLimits) -> PurePosixPath:
    if "\x00" in name:
        raise ArchiveValidationError("archive member name contains NUL")
    if len(name) > limits.max_path_length:
        raise ArchiveValidationError("archive member path too long")
    normalised = name.replace("\\", "/")
    if normalised.startswith("/") or re.match(r"^[A-Za-z]:", normalised):
        raise ArchiveValidationError(f"absolute or drive-qualified path: {name}")
    if normalised.startswith("//"):
        raise ArchiveValidationError(f"UNC path: {name}")
    parts = [p for p in normalised.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise ArchiveValidationError(f"path traversal component: {name}")
    if len(parts) > limits.max_depth:
        raise ArchiveValidationError(f"path nesting too deep: {name}")
    if not parts:
        raise ArchiveValidationError(f"empty archive member path: {name}")
    return PurePosixPath(*parts)


def _check_duplicate(target: Path, seen_casefold: set[str]) -> None:
    key = str(target).casefold()
    if key in seen_casefold:
        raise ArchiveValidationError(f"duplicate or case-colliding path: {target}")
    seen_casefold.add(key)


def _validate_tar(members: Iterator[tarfile.TarInfo], limits: ExtractionLimits) -> list[tarfile.TarInfo]:
    allowed: list[tarfile.TarInfo] = []
    seen: set[str] = set()
    total = 0
    for member in members:
        _safe_relative_member(member.name, limits)
        if member.issym() or member.islnk():
            raise ArchiveValidationError(f"links are not permitted: {member.name}")
        if member.ischr() or member.isblk() or member.isfifo():
            raise ArchiveValidationError(f"special files are not permitted: {member.name}")
        if not (member.isfile() or member.isdir()):
            raise ArchiveValidationError(f"unsupported member type: {member.name}")
        _check_duplicate(Path(member.name.replace("\\", "/")), seen)
        if member.isfile():
            total += member.size
            if member.size > limits.max_single_uncompressed:
                raise ArchiveValidationError(f"member too large: {member.name}")
            if total > limits.max_total_uncompressed:
                raise ArchiveValidationError("total uncompressed size exceeds limit")
        allowed.append(member)
        if len(allowed) > limits.max_entries:
            raise ArchiveValidationError("too many archive entries")
    return allowed


def _validate_zip(infolist: list[zipfile.ZipInfo], limits: ExtractionLimits) -> list[zipfile.ZipInfo]:
    allowed: list[zipfile.ZipInfo] = []
    seen: set[str] = set()
    total = 0
    for info in infolist:
        _safe_relative_member(info.filename, limits)
        mode = (info.external_attr >> 16) & 0o170000
        if mode == 0o120000:
            raise ArchiveValidationError(f"symlinks are not permitted: {info.filename}")
        if mode not in (0, 0o040000, 0o100000):
            raise ArchiveValidationError(f"special files are not permitted: {info.filename}")
        _check_duplicate(Path(info.filename.replace("\\", "/")), seen)
        if not info.is_dir():
            total += info.file_size
            if info.file_size > limits.max_single_uncompressed:
                raise ArchiveValidationError(f"member too large: {info.filename}")
            if total > limits.max_total_uncompressed:
                raise ArchiveValidationError("total uncompressed size exceeds limit")
            if info.compress_size > 0:
                if info.file_size / info.compress_size > limits.max_ratio:
                    raise ArchiveValidationError(f"suspicious compression ratio: {info.filename}")
        allowed.append(info)
        if len(allowed) > limits.max_entries:
            raise ArchiveValidationError("too many archive entries")
    return allowed


def extract_archive(archive: Path, destination: Path, limits: ExtractionLimits | None = None) -> list[str]:
    """Safely extract a tar or zip archive into ``destination``.

    Returns the sorted list of extracted relative file paths. Raises
    :class:`ArchiveValidationError` on any allowlist violation.
    """
    limits = limits or ExtractionLimits()
    archive = archive.resolve()
    destination = destination.resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ArchiveValidationError("destination directory must be new or empty")
    destination.mkdir(parents=True, exist_ok=True)
    os.chmod(destination, 0o700)

    extracted: list[str] = []
    if tarfile.is_tarfile(archive):
        with tarfile.open(archive, "r:*") as tar:
            members = _validate_tar(iter(tar), limits)
            for member in members:
                target = (destination / _safe_relative_member(member.name, limits)).resolve()
                if not str(target).startswith(str(destination) + os.sep) and target != destination:
                    raise ArchiveValidationError(f"member escapes destination: {member.name}")
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                source = tar.extractfile(member)
                if source is None:
                    raise ArchiveValidationError(f"cannot read member: {member.name}")
                with source, open(target, "wb") as out:
                    _copy_limited(source, out, member.size)
                extracted.append(str(target.relative_to(destination)))
    elif zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zf:
            infos = _validate_zip(zf.infolist(), limits)
            for info in infos:
                target = (destination / _safe_relative_member(info.filename, limits)).resolve()
                if not str(target).startswith(str(destination) + os.sep) and target != destination:
                    raise ArchiveValidationError(f"member escapes destination: {info.filename}")
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as source, open(target, "wb") as out:
                    _copy_limited(source, out, info.file_size)
                extracted.append(str(target.relative_to(destination)))
    else:
        raise ArchiveValidationError("archive is neither a supported tar nor zip file")

    return sorted(extracted)


def _copy_limited(source: BinaryIO, destination: BinaryIO, expected: int) -> None:
    written = 0
    while True:
        block = source.read(1024 * 1024)
        if not block:
            break
        written += len(block)
        if written > expected:
            raise ArchiveValidationError("member produced more data than declared")
        destination.write(block)
    if written != expected:
        raise ArchiveValidationError("member size mismatch")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RSS Netrix source-bundle pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encrypt_parser = subparsers.add_parser("encrypt", help="encrypt an archive into a bundle")
    encrypt_parser.add_argument("input", type=Path)
    encrypt_parser.add_argument("output", type=Path)
    encrypt_parser.add_argument("--key-id", required=True)
    encrypt_parser.add_argument("--product", default="rss-netrix")
    encrypt_parser.add_argument("--platforms", default="all")
    encrypt_parser.add_argument("--revision", default="unknown")
    encrypt_parser.add_argument("--force", action="store_true")

    decrypt_parser = subparsers.add_parser("decrypt", help="decrypt a bundle to an archive")
    decrypt_parser.add_argument("input", type=Path)
    decrypt_parser.add_argument("output", type=Path)
    decrypt_parser.add_argument("--force", action="store_true")

    extract_parser = subparsers.add_parser("extract", help="safely extract an archive")
    extract_parser.add_argument("input", type=Path)
    extract_parser.add_argument("output", type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "encrypt":
            manifest = encrypt_file(
                args.input,
                args.output,
                args.key_id,
                product=args.product,
                platforms=[p for p in args.platforms.split(",") if p],
                revision=args.revision,
                force=args.force,
            )
            print(json.dumps({"bundle_id": manifest["bundle_id"], "output": str(args.output)}, sort_keys=True))
        elif args.command == "decrypt":
            decrypt_file(args.input, args.output, args.force)
            print(f"decrypt completed: {args.output}")
        else:
            files = extract_archive(args.input, args.output)
            print(f"extracted {len(files)} files into {args.output}")
    except (BundleError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
