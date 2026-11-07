import base64
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.source_bundle import BundleError, decrypt_file, encrypt_file


class SourceBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.tar"
        self.bundle = self.root / "source.rssenc"
        self.output = self.root / "restored.tar"
        self.source.write_bytes(b"RSS Netrix prototype payload\x00with binary bytes")
        self.key_a = base64.b64encode(os.urandom(32)).decode("ascii")
        self.key_b = base64.b64encode(os.urandom(32)).decode("ascii")

    def tearDown(self):
        self.temp.cleanup()

    def test_round_trip(self):
        with patch.dict(os.environ, {"RSS_SOURCE_KEK": self.key_a}):
            encrypt_file(self.source, self.bundle, "prototype-key-v1")
            decrypt_file(self.bundle, self.output)
        self.assertEqual(self.source.read_bytes(), self.output.read_bytes())

    def test_wrong_key_is_rejected(self):
        with patch.dict(os.environ, {"RSS_SOURCE_KEK": self.key_a}):
            encrypt_file(self.source, self.bundle, "prototype-key-v1")
        with patch.dict(os.environ, {"RSS_SOURCE_KEK": self.key_b}):
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)
        self.assertFalse(self.output.exists())

    def test_ciphertext_tampering_is_rejected(self):
        with patch.dict(os.environ, {"RSS_SOURCE_KEK": self.key_a}):
            encrypt_file(self.source, self.bundle, "prototype-key-v1")
        data = bytearray(self.bundle.read_bytes())
        data[-1] ^= 0x01
        self.bundle.write_bytes(data)
        with patch.dict(os.environ, {"RSS_SOURCE_KEK": self.key_a}):
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)
        self.assertFalse(self.output.exists())

    def test_header_tampering_is_rejected(self):
        with patch.dict(os.environ, {"RSS_SOURCE_KEK": self.key_a}):
            encrypt_file(self.source, self.bundle, "prototype-key-v1")
        data = bytearray(self.bundle.read_bytes())
        data[-20] ^= 0x01
        self.bundle.write_bytes(data)
        with patch.dict(os.environ, {"RSS_SOURCE_KEK": self.key_a}):
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)
        self.assertFalse(self.output.exists())

    def test_existing_destination_is_not_overwritten_by_default(self):
        self.output.write_bytes(b"keep")
        with patch.dict(os.environ, {"RSS_SOURCE_KEK": self.key_a}):
            encrypt_file(self.source, self.bundle, "prototype-key-v1")
            with self.assertRaises(BundleError):
                decrypt_file(self.bundle, self.output)
        self.assertEqual(self.output.read_bytes(), b"keep")

    def test_invalid_key_length_is_rejected(self):
        with patch.dict(os.environ, {"RSS_SOURCE_KEK": base64.b64encode(b"short").decode("ascii")}):
            with self.assertRaises(BundleError):
                encrypt_file(self.source, self.bundle, "prototype-key-v1")


if __name__ == "__main__":
    unittest.main()
