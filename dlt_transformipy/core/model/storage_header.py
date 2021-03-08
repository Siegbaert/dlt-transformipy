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
import logging

from dlt_transformipy.core.helpers import (
    hex_str_to_utf8,
    hex_str_to_int32,
    hex_str_to_uint32,
)

# STORAGE HEADER BYTE SIZES
STORAGE_HEADER_TIMESTAMP_BYTE_SIZE = 8
STORAGE_HEADER_ECU_ID_BYTE_SIZE = 4
STORAGE_HEADER_BYTE_SIZE = (
    STORAGE_HEADER_TIMESTAMP_BYTE_SIZE + STORAGE_HEADER_ECU_ID_BYTE_SIZE
)


class StorageHeader():
    timestamp_seconds = 0
    timestamp_microseconds = 0
    ecu_id = None

    def __init__(self, dlt_message_hex, start_byte_pointer):
        storage_header_hex = dlt_message_hex[
            start_byte_pointer : start_byte_pointer + STORAGE_HEADER_BYTE_SIZE * 2
        ]
        self.timestamp_seconds = self.__extract_timestamp_seconds(storage_header_hex)
        self.timestamp_microseconds = self.__extract_timestamp_microseconds(
            storage_header_hex
        )
        self.ecu_id = self.__extract_ecu_id(storage_header_hex)

    def __extract_timestamp_seconds(self, storage_header_hex):
        return hex_str_to_int32(storage_header_hex[0:8])

    def __extract_timestamp_microseconds(self, storage_header_hex):
        return hex_str_to_uint32(storage_header_hex[8:16])

    def __extract_ecu_id(self, storage_header_hex):
        return hex_str_to_utf8(storage_header_hex[16:24]).rstrip("\0")

    ###
    # Getters
    ###
    def get_byte_size(self):
        return STORAGE_HEADER_BYTE_SIZE