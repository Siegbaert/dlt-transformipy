# This file is part of dlt-transformipy
# Copyright 2021  Dennis Schwarz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
