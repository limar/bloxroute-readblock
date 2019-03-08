import unittest
from parseblock import BlockHeader, HexStream, Transaction, read_varint
from io import BytesIO
import binascii
import struct

class GenesisBlock:
    block = b'0100000000000000000000000000000000000000000000000000000000000000000000003BA3EDFD7A7B12B27AC72C3E67768F617FC81BC3888A51323A9FB8AA4B1E5E4A29AB5F49FFFF001D1DAC2B7C0101000000010000000000000000000000000000000000000000000000000000000000000000FFFFFFFF4D04FFFF001D0104455468652054696D65732030332F4A616E2F32303039204368616E63656C6C6F72206F6E206272696E6B206F66207365636F6E64206261696C6F757420666F722062616E6B73FFFFFFFF0100F2052A01000000434104678AFDB0FE5548271967F1A67130B7105CD6A828E03909A67962E0EA1F61DEB649F6BC3F4CEF38C4F35504E51EC112DE5C384DF7BA0B8D578A4C702B6BF11D5FAC00000000'
    block_header = b'0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c01'
    transaction_count = 1
    block_hash = b'000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
    prev_block = b'0000000000000000000000000000000000000000000000000000000000000000'
    merkle_root = b'4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b'
    version = 1
    bits = 486604799
    nonce = 2083236893
    block_hash = b'000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'

class GenesisTransaction:
    size = 204
    bits = 486604799
    nonce = 2083236893
    inputs = 0
    transaction_hash = b'4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b'
'''
    ('version', 
                                   'flag',
                                   'tx_in_count',
                                   'tx_out_count',
                                   'lock_time',
                                   'start_offset',
                                   'end_offset'))
'''

class Test_read_varint(unittest.TestCase):
    def test_1byte(self):
        stream = BytesIO(b'\x01')
        i = read_varint(stream)
        self.assertEqual(i, 1)

        stream = BytesIO(b'\x01\x22')
        i = read_varint(stream)
        self.assertEqual(i, 1)
        self.assertEqual(stream.tell(), 1)

        stream = BytesIO(b'\xFC')
        i = read_varint(stream)
        self.assertEqual(i, 0xFC)

        stream = BytesIO(b'\xFD')
        self.assertRaises(struct.error, lambda: read_varint(stream))

    def test_2bytes(self):
        stream = BytesIO(b'\xFD\x00')
        self.assertRaises(struct.error, lambda: read_varint(stream))

        stream = BytesIO(b'\xFD\x00\x00')
        i = read_varint(stream)
        self.assertEqual(i, 0)

        stream = BytesIO(b'\xFD\x11\x22')
        i = read_varint(stream)
        self.assertEqual(i, 0x2211)

        stream = BytesIO(b'\xFD\x11\x22\x33')
        i = read_varint(stream)
        self.assertEqual(i, 0x2211)

    def test_4bytes(self):
        stream = BytesIO(b'\xFE\x00')
        self.assertRaises(struct.error, lambda: read_varint(stream))

        stream = BytesIO(b'\xFE\x00\x00')
        self.assertRaises(struct.error, lambda: read_varint(stream))

        stream = BytesIO(b'\xFE\x00\x00\x00')
        self.assertRaises(struct.error, lambda: read_varint(stream))

        stream = BytesIO(b'\xFE\x00\x00\x00\x00')
        i = read_varint(stream)
        self.assertEqual(i, 0)

        stream = BytesIO(b'\xFE\x11\x22\x33\x44')
        i = read_varint(stream)
        self.assertEqual(i, 0x44332211)

    def test_8bytes(self):
        stream = BytesIO(b'\xFF\x11\x22\x33\x44\x11\x22\x33\x44')
        i = read_varint(stream)
        self.assertEqual(i, 0x4433221144332211)

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
        self.assertEqual(header.txn_count, GenesisBlock.transaction_count)
        
        block_hexdigest = binascii.b2a_hex(header.block_hash.digest()[::-1])
        self.assertEqual(block_hexdigest, GenesisBlock.block_hash)

        self.assertEqual(binary_stream.tell(), len(GenesisBlock.block_header))
        
        transaction = Transaction.from_stream(stream)
        self.assertEqual(transaction.tx_in_count, 1)
        self.assertEqual(transaction.tx_out_count, 1)
        self.assertEqual(transaction.end_offset - transaction.start_offset, GenesisTransaction.size)
        
        hexdigest = binascii.b2a_hex(transaction.transaction_hash.digest()[::-1])
        self.assertEqual(hexdigest, GenesisTransaction.transaction_hash)


if __name__ == '__main__':
    unittest.main()