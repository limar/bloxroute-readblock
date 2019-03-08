#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 12:25:05 2019

@author: marklifshits
"""

'''
    - should we check Meassage header checksum?
    - how to detect transaction flag presense ?
'''

import struct
import binascii
from collections import namedtuple
from io import SEEK_SET, SEEK_CUR
from ctypes import Structure, c_uint32, c_int32, c_int64, c_uint16, c_char, c_byte, sizeof
import hashlib
from wrapper_streams import HashedStream, HexStream
import sys


class ReadableUnit:
    @classmethod
    def from_stream(cls, stream):
        raise AssertionError('Not implemented.')

class ReadableBufferObject(ReadableUnit):
    @classmethod
    def from_stream(cls, stream):
        inst = cls()
        stream.readinto(inst)
        return inst

class MessageHeader(Structure, ReadableBufferObject):
    _fields_ = [ ('magic', c_uint32),
                 ('command', c_char*12),
                 ('length', c_uint32),
                 ('checksum', c_uint32)
               ]
    

class OutPoint(Structure, ReadableBufferObject):
    _fields_ = [ ('hash', c_byte*32),
                 ('index', c_uint32)
               ]
    
class TxIn(ReadableUnit):
    @classmethod
    def from_stream(cls, stream):
        inst = TxIn()
        inst.previous_output = OutPoint.from_stream(stream)
        inst.script_length = read_varint(stream)
        # skip script
        stream.read(inst.script_length)
        inst.sequence = c_uint32()
        stream.readinto(inst.sequence)
        return inst

class TxOut(ReadableUnit):
    @classmethod
    def from_stream(cls, stream):
        inst = TxOut()
        inst.value = c_int64()
        stream.readinto(inst.value)
        inst.pk_script_length = read_varint(stream)
        # skip pk_skript
        stream.read(inst.pk_script_length)
        return inst

class TxWitness(ReadableUnit):

    def __init__(self, data_components):
        self.data_components = data_components

    @classmethod
    def from_stream(cls, stream):
        
        count_data_components = read_varint(stream)
        data_components = []
        for _ in range(count_data_components):
            data_size = read_varint(stream)
            data_components.append(data_size)
            # skip data
            stream.read(data_size)
        return TxWitness(data_components)
    
class Transaction(ReadableUnit):
    TransactionTuple = namedtuple('TransactionTuple', 
                                  ('version', 
                                   'flag',
                                   'tx_in_count',
                                   'tx_out_count',
                                   'lock_time',
                                   'start_offset',
                                   'end_offset',
                                   'transaction_hash'))
        
        
    @classmethod
    def from_stream(cls, stream):

        stream = HashedStream(stream)
        start_offset = stream.tell()
        version = c_int32()
        stream.readinto(version)

        flag = None
        # flag = c_uint16()
        # stream.readinto(flag)
        
        # if flag.value != 1:
        #     stream.seek(- sizeof(flag), SEEK_CUR)
        #     flag = None
        # else:
        #     flag = flag.value
        
        tx_in_count = read_varint(stream)
        # skip tx inputs
        for _ in range(tx_in_count):
            TxIn.from_stream(stream)
        
        tx_out_count = read_varint(stream)
        # skip tx outputs
        for _ in range(tx_out_count):
            TxOut.from_stream(stream)
        
        if flag is not None:
            for _ in range(tx_in_count):
                # skip witness
                TxWitness.from_stream(stream)
        
        lock_time = c_uint32()
        stream.readinto(lock_time)
        
        end_offset = stream.tell()
        
        transaction_hash = hashlib.sha256(stream.hash.digest())
        return cls.TransactionTuple(version, flag, tx_in_count, tx_out_count, 
                                lock_time, start_offset, end_offset, transaction_hash)
        

class BlockHeader(Structure):
    _fields_ = [ ('version', c_int32),
                 ('prev_block', c_byte*32),
                 ('merkle_root', c_byte*32),
                 ('timestamp', c_uint32),
                 ('bits', c_uint32),
                 ('nonce', c_uint32)
            ]
    
    @classmethod
    def from_stream(cls, stream):
        inst = cls()
        stream = HashedStream(stream)
        stream.readinto(inst)
        inst.block_hash = hashlib.sha256(stream.hash.digest())
        inst.txn_count = read_varint(stream)
        return inst


def read_varint(stream):
    data = stream.read(1)
    i = struct.unpack('B',data)[0]
    if i < 0xfd:
        return i
    
    bytes_to_read, fmt = {
     0xfd: (2, '<H'),
     0xfe: (4, '<I'),
     0xff: (8, '<Q')
    }[i]
    
    data = stream.read(bytes_to_read)
    i = struct.unpack(fmt, data)[0]
    return i

       
def read_message(stream):
    message_header = MessageHeader.from_stream(stream)
    if message_header.command.decode('ascii') == 'block':
        block_header = BlockHeader.from_stream(stream)
        print("Block header:")
        print("\tblock hash:", block_header.block_hash.hexdigest())
        print("\tprevious block hash:", binascii.b2a_hex(block_header.prev_block))
        print("\tnumber of transactions: ", block_header.txn_count)
        print()
        for i in range(block_header.txn_count):
            t = Transaction.from_stream(stream)
            print('Transaction', i + 1,
            'start', t.start_offset,
            'length',t.end_offset - t.start_offset,
            'end', t.end_offset,
            'hash', t.transaction_hash.hexdigest())

    return message_header

def main(argv):
    if len(argv) < 2:
        print("Usage:\n", "\tparseblock.py <filepath>")
        return

    filepath = argv[1]
    with open(filepath, 'rb') as f:
        hs = HexStream(f)
        read_message(hs)

if __name__ == '__main__':
    main(sys.argv)
