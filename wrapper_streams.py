#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
from io import BytesIO
import hashlib
from ctypes import sizeof


class HexStream:
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
    
    # def seek(self, offset, whence = SEEK_SET):
    #     self.stream.seek(int(offset*2), whence)

class HashedStream:
    def __init__(self, stream):
        self.stream = stream
        self.hash = hashlib.sha256()
    
    def read(self, n):
        data = self.stream.read(n)
        self.hash.update(data)
        return data
    
    def readinto(self, b):
        size = sizeof(b)
        data = self.read(size)
        BytesIO(data).readinto(b)
    
    def tell(self):
        return self.stream.tell()
