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
from dlt_transformipy import logger

from dlt_transformipy.core.helpers import (
    isKthBitSet,
    hex_str_to_ascii,
    hex_str_to_utf8,
    hex_str_to_int32,
    hex_str_to_uint32,
    hex_str_to_int8,
    hex_str_to_uint8,
    hex_str_to_uint16,
    hex_str_to_int16,
    hex_str_to_int64,
    hex_str_to_uint64,
)

# BYTE SIZES
STANDARD_HEADER_HEADER_TYPE_BYTE_SIZE = 1
STANDARD_HEADER_MESSAGE_COUNTER_BYTE_SIZE = 1
STANDARD_HEADER_LENGTH_BYTE_SIZE = 2
STANDARD_HEADER_ECU_ID_BYTE_SIZE = 4
STANDARD_HEADER_SESSION_ID_BYTE_SIZE = 4
STANDARD_HEADER_TIMESTAMP_BYTE_SIZE = 4
STANDARD_HEADER_BYTE_SIZE = (
    STANDARD_HEADER_HEADER_TYPE_BYTE_SIZE
    + STANDARD_HEADER_MESSAGE_COUNTER_BYTE_SIZE
    + STANDARD_HEADER_LENGTH_BYTE_SIZE
    + STANDARD_HEADER_ECU_ID_BYTE_SIZE
    + STANDARD_HEADER_SESSION_ID_BYTE_SIZE
    + STANDARD_HEADER_TIMESTAMP_BYTE_SIZE
)


class StandardHeader():
    header_type = None
    message_counter = 0
    length = 0
    ecu_id = None
    session_id = None
    timestamp = None

    def __init__(self, dlt_message_hex, start_byte_pointer):
        standard_header_hex = dlt_message_hex[
            start_byte_pointer : start_byte_pointer + STANDARD_HEADER_BYTE_SIZE * 2
        ]

        # StandardHeader.header_type
        self.header_type = StandardHeaderType(standard_header_hex)
        # StandardHeader.message_counter
        self.message_counter = self.__extract_message_counter(standard_header_hex)
        # StandardHeader.length
        self.length = self.__extract_length(standard_header_hex)

        optional_header_dynamic_byte_offset = 4  # Start offset of ecu_id
        # StandardHeader.ecu_id
        if self.header_type.with_ecu_id:
            self.ecu_id = self.__extract_ecu_id(
                standard_header_hex, optional_header_dynamic_byte_offset
            )
            optional_header_dynamic_byte_offset += STANDARD_HEADER_ECU_ID_BYTE_SIZE
        # StandardHeader.session_id
        if self.header_type.with_session_id:
            self.session_id = self.__extract_session_id(
                standard_header_hex, optional_header_dynamic_byte_offset
            )
            optional_header_dynamic_byte_offset += STANDARD_HEADER_SESSION_ID_BYTE_SIZE
        # StandardHeader.timestamp
        if self.header_type.with_timestamp:
            self.timestamp = self.__extract_timestamp(
                standard_header_hex, optional_header_dynamic_byte_offset
            )

    def __extract_message_counter(self, standard_header_hex):
        return hex_str_to_uint8(standard_header_hex[2:4])

    def __extract_length(self, standard_header_hex):
        return hex_str_to_uint16(standard_header_hex[4:8], big_endian=True)

    def __extract_ecu_id(
        self, standard_header_hex, optional_header_dynamic_byte_offset
    ):
        return hex_str_to_utf8(
            standard_header_hex[
                optional_header_dynamic_byte_offset
                * 2 : (
                    optional_header_dynamic_byte_offset
                    + STANDARD_HEADER_ECU_ID_BYTE_SIZE
                )
                * 2
            ],
            errors="ignore",
        )

    def __extract_session_id(
        self, standard_header_hex, optional_header_dynamic_byte_offset
    ):
        return hex_str_to_uint32(
            standard_header_hex[
                optional_header_dynamic_byte_offset
                * 2 : (
                    optional_header_dynamic_byte_offset
                    + STANDARD_HEADER_SESSION_ID_BYTE_SIZE
                )
                * 2
            ],
            big_endian=True,
        )

    def __extract_timestamp(
        self, standard_header_hex, optional_header_dynamic_byte_offset
    ):
        return hex_str_to_int32(
            standard_header_hex[
                optional_header_dynamic_byte_offset
                * 2 : (
                    optional_header_dynamic_byte_offset
                    + STANDARD_HEADER_TIMESTAMP_BYTE_SIZE
                )
                * 2
            ],
            big_endian=True,
        )

    ###
    # Getters
    ###
    def get_byte_size(self):
        standard_header_dynamic_byte_size = STANDARD_HEADER_BYTE_SIZE

        if not self.header_type.with_ecu_id:
            standard_header_dynamic_byte_size -= STANDARD_HEADER_ECU_ID_BYTE_SIZE

        if not self.header_type.with_session_id:
            standard_header_dynamic_byte_size -= STANDARD_HEADER_SESSION_ID_BYTE_SIZE

        if not self.header_type.with_timestamp:
            standard_header_dynamic_byte_size -= STANDARD_HEADER_TIMESTAMP_BYTE_SIZE

        return standard_header_dynamic_byte_size


class StandardHeaderType():
    use_extended_header = False
    most_significant_byte_first = False
    with_ecu_id = False
    with_session_id = False
    with_timestamp = False
    version_number = None

    def __init__(self, standard_header_hex):
        standard_header_type_hex = standard_header_hex[
            : STANDARD_HEADER_HEADER_TYPE_BYTE_SIZE * 2
        ]
        header_type_int = hex_str_to_uint8(standard_header_type_hex)

        self.use_extended_header = isKthBitSet(header_type_int, 0)
        self.most_significant_byte_first = isKthBitSet(header_type_int, 1)
        self.with_ecu_id = isKthBitSet(header_type_int, 2)
        self.with_session_id = isKthBitSet(header_type_int, 3)
        self.with_timestamp = isKthBitSet(header_type_int, 4)
        self.version_number = header_type_int & 0b11100000