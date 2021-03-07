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


class StorageHeader(object):
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