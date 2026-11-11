import base64
import io
import json
import os
import struct
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.source_bundle import (
    CHUNK_SIZE,
    FORMAT_VERSION,
    MAGIC,
    ArchiveValidationError,
    BundleError,
    ExtractionLimits,
    _canonical_json,
    _chunk_count_for,
    _parse_manifest,
    _validate_manifest,
    decrypt_file,
    encrypt_file,
    extract_archive,
)

KEY_ID = "test-key-v1"


def _env(key: bytes):
    return patch.dict(os.environ, {"RSS_SOURCE_KEK": base64.b64encode(key).decode("ascii")})


class SourceBundleCryptoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.tar"
        self.bundle = self.root / "source.rssenc"
        self.output = self.root / "restored.tar"
        self.payload = b"RSS Netrix proprietary payload\x00\x01\x02" * 1000
        self.source.write_bytes(self.payload)
        self.key_a = os.urandom(32)
        self.key_b = os.urandom(32)

    def tearDown(self):
        self.temp.cleanup()

    def _encrypt(self, **kwargs):
        with _env(self.key_a):
            return encrypt_file(self.source, self.bundle, KEY_ID, **kwargs)

    def test_round_trip_small(self):
        manifest = self._encrypt()
        with _env(self.key_a):
            decrypt_file(self.bundle, self.output)
        self.assertEqual(self.source.read_bytes(), self.output.read_bytes())
        self.assertEqual(manifest["plaintext_length"], len(self.payload))
        self.assertEqual(manifest["chunk_count"], _chunk_count_for(len(self.payload)))

    def test_round_trip_empty_file(self):
        self.source.write_bytes(b"")
        self._encrypt()
        with _env(self.key_a):
            decrypt_file(self.bundle, self.output)
        self.assertEqual(self.output.read_bytes(), b"")

    def test_round_trip_multichunk(self):
        big = os.urandom(CHUNK_SIZE * 2 + 12345)
        self.source.write_bytes(big)
        manifest = self._encrypt()
        self.assertEqual(manifest["chunk_count"], 3)
        with _env(self.key_a):
            decrypt_file(self.bundle, self.output)
        self.assertEqual(self.output.read_bytes(), big)

    def test_wrong_key_rejected(self):
        self._encrypt()
        with _env(self.key_b):
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)
        self.assertFalse(self.output.exists())

    def test_ciphertext_tampering_rejected(self):
        self._encrypt()
        data = bytearray(self.bundle.read_bytes())
        data[-1] ^= 0x01
        self.bundle.write_bytes(data)
        with _env(self.key_a):
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)
        self.assertFalse(self.output.exists())

    def test_chunk_swap_rejected(self):
        big = os.urandom(CHUNK_SIZE * 2)
        self.source.write_bytes(big)
        self._encrypt()
        data = self.bundle.read_bytes()
        header_end = len(MAGIC) + 4 + struct.unpack(">I", data[len(MAGIC):len(MAGIC) + 4])[0]
        first_len = struct.unpack(">I", data[header_end:header_end + 4])[0]
        second_start = header_end + 4 + first_len
        second_len = struct.unpack(">I", data[second_start:second_start + 4])[0]
        c1 = data[header_end:second_start]
        c2 = data[second_start:second_start + 4 + second_len]
        swapped = bytearray(data[:header_end]) + bytearray(c2) + bytearray(c1) + bytearray(data[second_start + 4 + second_len:])
        self.bundle.write_bytes(swapped)
        with _env(self.key_a):
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)

    def test_truncated_bundle_rejected(self):
        self._encrypt()
        data = self.bundle.read_bytes()
        self.bundle.write_bytes(data[:-10])
        with _env(self.key_a):
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)

    def test_trailing_data_rejected(self):
        self._encrypt()
        self.bundle.write_bytes(self.bundle.read_bytes() + b"EXTRA")
        with _env(self.key_a):
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)

    def test_manifest_tampering_rejected(self):
        self._encrypt()
        data = bytearray(self.bundle.read_bytes())
        offset = data.index(b"test-key-v1")
        data[offset] = ord("q")
        self.bundle.write_bytes(data)
        with _env(self.key_a):
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)

    def test_existing_destination_not_overwritten(self):
        self.output.write_bytes(b"keep")
        self._encrypt()
        with _env(self.key_a):
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)
        self.assertEqual(self.output.read_bytes(), b"keep")

    def test_invalid_key_length_rejected(self):
        with _env(b"short"):
            with self.assertRaises(BundleError):
                encrypt_file(self.source, self.bundle, KEY_ID)

    def test_missing_key_rejected(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("RSS_SOURCE_KEK", None)
            with self.assertRaises(BundleError):
                encrypt_file(self.source, self.bundle, KEY_ID)

    def test_invalid_key_id_rejected(self):
        with _env(self.key_a):
            with self.assertRaises(BundleError):
                encrypt_file(self.source, self.bundle, "bad key id!")

    def test_unique_bundle_id_and_nonce_prefix(self):
        m1 = self._encrypt()
        self.bundle.unlink()
        m2 = self._encrypt()
        self.assertNotEqual(m1["bundle_id"], m2["bundle_id"])
        self.assertNotEqual(m1["nonce_prefix"], m2["nonce_prefix"])

    def test_nonce_uniqueness_across_chunks(self):
        from tools.source_bundle import _chunk_nonce
        prefix = os.urandom(8)
        nonces = {_chunk_nonce(prefix, i) for i in range(10000)}
        self.assertEqual(len(nonces), 10000)
        for nonce in nonces:
            self.assertEqual(len(nonce), 12)

    def test_large_file_streams_within_memory_bound(self):
        # 8 MiB across 8 chunks must not require holding the whole file plus its
        # ciphertext in memory at once. We assert peak tracemalloc stays well
        # below the file size, proving chunked streaming.
        import tracemalloc
        size = CHUNK_SIZE * 8
        big = os.urandom(size)
        self.source.write_bytes(big)
        tracemalloc.start()
        self._encrypt()
        _, peak_encrypt = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        with _env(self.key_a):
            tracemalloc.start()
            decrypt_file(self.bundle, self.output)
            _, peak_decrypt = tracemalloc.get_traced_memory()
            tracemalloc.stop()
        self.assertEqual(self.output.read_bytes(), big)
        bound = size // 2  # generous: still far below whole-file buffering
        self.assertLess(peak_encrypt, bound, f"encrypt peak {peak_encrypt} exceeded {bound}")
        self.assertLess(peak_decrypt, bound, f"decrypt peak {peak_decrypt} exceeded {bound}")


class ManifestTests(unittest.TestCase):
    def _valid_manifest(self):
        return {
            "version": FORMAT_VERSION,
            "algorithm": "AES-256-GCM-CHUNKED",
            "wrap_algorithm": "AES-256-KW",
            "key_id": KEY_ID,
            "product": "rss-netrix",
            "platforms": ["android", "windows"],
            "revision": "abc123",
            "bundle_id": "0" * 32,
            "nonce_prefix": base64.b64encode(os.urandom(8)).decode(),
            "wrapped_dek": base64.b64encode(os.urandom(40)).decode(),
            "plaintext_length": 10,
            "chunk_size": CHUNK_SIZE,
            "chunk_count": 1,
            "plaintext_sha256": base64.b64encode(os.urandom(32)).decode(),
        }

    def test_valid_manifest_accepted(self):
        m = self._valid_manifest()
        self.assertIs(_validate_manifest(m), m)

    def test_unknown_field_rejected(self):
        m = self._valid_manifest()
        m["extra"] = 1
        with self.assertRaises(BundleError):
            _validate_manifest(m)

    def test_missing_field_rejected(self):
        m = self._valid_manifest()
        del m["revision"]
        with self.assertRaises(BundleError):
            _validate_manifest(m)

    def test_duplicate_json_keys_rejected(self):
        raw = b'{"version":2,"version":2}'
        with self.assertRaises(BundleError):
            _parse_manifest(raw)

    def test_non_canonical_manifest_rejected(self):
        m = self._valid_manifest()
        raw = json.dumps(m, indent=2).encode()
        with self.assertRaises(BundleError):
            _parse_manifest(raw)

    def test_wrong_version_rejected(self):
        m = self._valid_manifest()
        m["version"] = 999
        with self.assertRaises(BundleError):
            _validate_manifest(m)

    def test_bad_type_rejected(self):
        m = self._valid_manifest()
        m["plaintext_length"] = "ten"
        with self.assertRaises(BundleError):
            _validate_manifest(m)

    def test_out_of_range_rejected(self):
        m = self._valid_manifest()
        m["plaintext_length"] = -1
        with self.assertRaises(BundleError):
            _validate_manifest(m)

    def test_chunk_count_mismatch_rejected(self):
        m = self._valid_manifest()
        m["plaintext_length"] = CHUNK_SIZE * 3
        m["chunk_count"] = 1
        with self.assertRaises(BundleError):
            _validate_manifest(m)

    def test_bad_platform_rejected(self):
        m = self._valid_manifest()
        m["platforms"] = ["solaris"]
        with self.assertRaises(BundleError):
            _validate_manifest(m)

    def test_canonical_roundtrip(self):
        m = self._valid_manifest()
        raw = _canonical_json(m)
        self.assertEqual(_parse_manifest(raw), m)


class ArchiveExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.dest = self.root / "out"

    def tearDown(self):
        self.temp.cleanup()

    def _tar_with(self, entries, name="a.tar"):
        path = self.root / name
        with tarfile.open(path, "w") as tar:
            for member_name, data, kind in entries:
                info = tarfile.TarInfo(member_name)
                if kind == "file":
                    info.size = len(data)
                    tar.addfile(info, io.BytesIO(data))
                elif kind == "dir":
                    info.type = tarfile.DIRTYPE
                    tar.addfile(info)
                elif kind == "sym":
                    info.type = tarfile.SYMTYPE
                    info.linkname = data.decode() if isinstance(data, bytes) else data
                    tar.addfile(info)
        return path

    def test_valid_tar_extracts(self):
        path = self._tar_with([("src/main.kt", b"fun main() {}", "file"), ("src", b"", "dir")])
        files = extract_archive(path, self.dest)
        self.assertEqual(files, ["src/main.kt"])
        self.assertEqual((self.dest / "src/main.kt").read_bytes(), b"fun main() {}")

    def test_path_traversal_rejected(self):
        path = self._tar_with([("../evil.txt", b"x", "file")])
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest)

    def test_absolute_path_rejected(self):
        path = self._tar_with([("/etc/passwd", b"x", "file")])
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest)

    def test_drive_qualified_path_rejected(self):
        path = self._tar_with([("C:/Windows/system32/x.dll", b"x", "file")])
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest)

    def test_symlink_rejected(self):
        path = self._tar_with([("link", b"/etc/passwd", "sym")])
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest)

    def test_duplicate_paths_rejected(self):
        path = self._tar_with([("a.txt", b"1", "file"), ("a.txt", b"2", "file")])
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest)

    def test_case_collision_rejected(self):
        path = self._tar_with([("A.txt", b"1", "file"), ("a.txt", b"2", "file")])
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest)

    def test_zip_valid_extracts(self):
        path = self.root / "a.zip"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("src/app.kt", "val x = 1")
        files = extract_archive(path, self.dest)
        self.assertEqual(files, ["src/app.kt"])

    def test_zip_traversal_rejected(self):
        path = self.root / "a.zip"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("../evil.txt", "x")
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest)

    def test_entry_count_limit(self):
        path = self._tar_with([(f"f{i}.txt", b"x", "file") for i in range(20)])
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest, ExtractionLimits(max_entries=10))

    def test_oversize_member_rejected(self):
        path = self._tar_with([("big.bin", b"x" * 100, "file")])
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest, ExtractionLimits(max_single_uncompressed=10))

    def test_zip_bomb_ratio_rejected(self):
        path = self.root / "bomb.zip"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("bomb.bin", b"\x00" * (2 * 1024 * 1024))
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest, ExtractionLimits(max_ratio=10))

    def test_deep_path_rejected(self):
        deep = "/".join(f"d{i}" for i in range(100)) + "/f.txt"
        path = self._tar_with([(deep, b"x", "file")])
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest, ExtractionLimits(max_depth=10))

    def test_non_empty_destination_rejected(self):
        path = self._tar_with([("a.txt", b"x", "file")])
        self.dest.mkdir(parents=True)
        (self.dest / "existing.txt").write_text("y")
        with self.assertRaises(ArchiveValidationError):
            extract_archive(path, self.dest)


if __name__ == "__main__":
    unittest.main()
