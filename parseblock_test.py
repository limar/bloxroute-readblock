import unittest
from parseblock import BlockHeader, HexStream
from io import BytesIO
import binascii

class GenesisBlock:
    block = b'0100000000000000000000000000000000000000000000000000000000000000000000003BA3EDFD7A7B12B27AC72C3E67768F617FC81BC3888A51323A9FB8AA4B1E5E4A29AB5F49FFFF001D1DAC2B7C0101000000010000000000000000000000000000000000000000000000000000000000000000FFFFFFFF4D04FFFF001D0104455468652054696D65732030332F4A616E2F32303039204368616E63656C6C6F72206F6E206272696E6B206F66207365636F6E64206261696C6F757420666F722062616E6B73FFFFFFFF0100F2052A01000000434104678AFDB0FE5548271967F1A67130B7105CD6A828E03909A67962E0EA1F61DEB649F6BC3F4CEF38C4F35504E51EC112DE5C384DF7BA0B8D578A4C702B6BF11D5FAC00000000'
    block_header = b'0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c'
    transaction_count = 1
    block_hash = b'000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
    prev_block = b'0000000000000000000000000000000000000000000000000000000000000000'
    merkle_root = b'4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b'
    version = 1
    bits = 486604799
    nonce = 2083236893

class GenesisTransaction:
    size = 204
    bits = 486604799
    nonce = 2083236893

class Test_ParseBlockTests(unittest.TestCase):
    def test_parse_genesis_block(self):
        binary_stream = BytesIO(GenesisBlock.block)
        stream = HexStream(binary_stream)
        header = BlockHeader.from_stream(stream)
        self.assertEqual(header.version, GenesisBlock.version)
        self.assertEqual(header.bits, GenesisBlock.bits)
        self.assertEqual(header.nonce, GenesisBlock.nonce)
        self.assertEqual(binascii.b2a_hex(header.prev_block), GenesisBlock.prev_block)
        self.assertEqual(binascii.b2a_hex(bytes(header.merkle_root)[::-1]), GenesisBlock.merkle_root)
    
    def test2(self):
        pass

if __name__ == '__main__':
    unittest.main()