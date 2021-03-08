# MIT License
# 
# Copyright (c) 2021 Dennis Schwarz
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import codecs
from struct import unpack
from binascii import unhexlify


def isKthBitSet(n, k):
    return n & (1 << k)


def hex_str_to_ascii(hex_str, errors="ignore"):
    return codecs.decode(hex_str, "hex").decode(errors=errors)


def hex_str_to_utf8(hex_str, errors="ignore"):
    return codecs.decode(hex_str, "hex").decode("utf-8", errors=errors)


def hex_str_to_int8(hex_str, big_endian=False):
    return unpack(">b" if big_endian else "<b", unhexlify(hex_str))[0]


def hex_str_to_uint8(hex_str, big_endian=False):
    return unpack(">B" if big_endian else "<B", unhexlify(hex_str))[0]


def hex_str_to_int16(hex_str, big_endian=False):
    return unpack(">h" if big_endian else "<h", unhexlify(hex_str))[0]


def hex_str_to_uint16(hex_str, big_endian=False):
    return unpack(">H" if big_endian else "<H", unhexlify(hex_str))[0]


def hex_str_to_int32(hex_str, big_endian=False):
    return unpack(">i" if big_endian else "<i", unhexlify(hex_str))[0]


def hex_str_to_uint32(hex_str, big_endian=False):
    return unpack(">I" if big_endian else "<I", unhexlify(hex_str))[0]


def hex_str_to_int64(hex_str, big_endian=False):
    return unpack(">q" if big_endian else "<q", unhexlify(hex_str))[0]


def hex_str_to_uint64(hex_str, big_endian=False):
    return unpack(">Q" if big_endian else "<Q", unhexlify(hex_str))[0]
