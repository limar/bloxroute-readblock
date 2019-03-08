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
from io import BytesIO


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
        stream.seek(inst.script_length, SEEK_CUR)
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
        stream.seek(inst.pk_script_length, SEEK_CUR)
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
            stream.seek(data_size, SEEK_CUR)
        return TxWitness(data_components)
    
class Transaction(ReadableUnit):
#    TransactionTuple = namedtuple('TransactionTuple', 
#                                  ('version', 
#                                   'flag',
#                                   'tx_in_count',
#                                   'tx_in',
#                                   'tx_out_count',
#                                   'tx_out',
#                                   'tx_witnesses',
#                                   'lock_time'))
    
    TransactionTuple = namedtuple('TransactionTuple', 
                                  ('version', 
                                   'flag',
                                   'tx_in_count',
                                   'tx_out_count',
                                   'lock_time',
                                   'start_offset',
                                   'end_offset'))
        
        
    @classmethod
    def from_stream(cls, stream):

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
        for i in range(tx_in_count):
            print('\t tx_in', i, 'out of', tx_in_count)
            ti = TxIn.from_stream(stream)
        
        tx_out_count = read_varint(stream)
        # skip tx outputs
        for _ in range(tx_out_count):
            to = TxOut.from_stream(stream)
        
        if flag is not None:
            for _ in range(tx_in_count):
                # skip witness
                TxWitness.from_stream(stream)
        
        lock_time = c_uint32()
        stream.readinto(lock_time)
        
        end_offset = stream.tell()
        
        return cls.TransactionTuple(version, flag, tx_in_count, tx_out_count, 
                                lock_time, start_offset, end_offset)
        
            

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
        stream.readinto(inst)
        inst.txn_count = read_varint(stream)
        return inst
    
class HexStream():
    def __init__(self, stream):
        self.stream = stream
    
    def read(self, n):
        text = self.stream.read(n*2)
        return binascii.a2b_hex(text)
    
    def readinto(self, b):
        size = sizeof(b)
        data = self.read(size)
        BytesIO(data).readinto(b)
  
    def tell(self):
        return int(self.stream.tell()/2)
    
    def seek(self, offset, whence = SEEK_SET):
        self.stream.seek(int(offset*2), whence)


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
        for i in range(block_header.txn_count):
            t = Transaction.from_stream(stream)
            print('Transaction', i + 1, 'from', block_header.txn_count, 'start', t.start_offset, 'end', t.end_offset)

    return message_header

def main():
    with open('/Users/marklifshits/work/bitcoin-block/sample_block.txt', 'rb') as f:
        hs = HexStream(f)
        read_message(hs)

if __name__ == '__main__':
    main()
