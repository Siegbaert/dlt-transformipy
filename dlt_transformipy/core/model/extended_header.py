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
from dlt_transformipy.core.helpers import isKthBitSet, hex_str_to_utf8, hex_str_to_uint8

# EXTENDED HEADER BYTE SIZES
EXTENDED_HEADER_MESSAGE_INFO_BYTE_SIZE = 1
EXTENDED_HEADER_NO_ARGUMENTS_BYTE_SIZE = 1
EXTENDED_HEADER_APPLICATION_ID_BYTE_SIZE = 4
EXTENDED_HEADER_CONTEXT_ID_BYTE_SIZE = 4
EXTENDED_HEADER_BYTE_SIZE = (
    EXTENDED_HEADER_MESSAGE_INFO_BYTE_SIZE
    + EXTENDED_HEADER_NO_ARGUMENTS_BYTE_SIZE
    + EXTENDED_HEADER_APPLICATION_ID_BYTE_SIZE
    + EXTENDED_HEADER_CONTEXT_ID_BYTE_SIZE
)


class ExtendedHeader:
    message_info = None
    noar = None
    apid = None
    ctid = None

    def __init__(self, dlt_message_hex, start_byte_pointer):
        extended_header_hex = dlt_message_hex[
            start_byte_pointer : start_byte_pointer + EXTENDED_HEADER_BYTE_SIZE * 2
        ]
        self.message_info = ExtendedHeaderMessageInfo(extended_header_hex)
        self.noar = self.__extract_number_of_arguments(extended_header_hex)
        self.apid = self.__extract_application_id(extended_header_hex)
        self.ctid = self.__extract_context_id(extended_header_hex)

    def __extract_number_of_arguments(self, extended_header_hex):
        # In non-verbose mode, args shall be "0" according to Autosar spec
        return (
            hex_str_to_uint8(extended_header_hex[2:4], big_endian=True)
            if self.message_info.verbose
            else 0
        )

    @staticmethod
    def __extract_application_id(extended_header_hex):
        return hex_str_to_utf8(extended_header_hex[4:12], errors="ignore").rstrip("\0")

    @staticmethod
    def __extract_context_id(extended_header_hex):
        return hex_str_to_utf8(extended_header_hex[12:20], errors="ignore").rstrip("\0")

    ###
    # Getters
    ###
    @staticmethod
    def get_byte_size():
        return EXTENDED_HEADER_BYTE_SIZE


class ExtendedHeaderMessageInfo:
    verbose = False
    message_type = None
    message_type_info = None

    def __init__(self, extended_header_hex):
        extended_header_message_info_int = hex_str_to_uint8(
            extended_header_hex[:2], big_endian=True
        )

        self.verbose = self.__extract_verbose(extended_header_message_info_int)
        self.message_type = self.__extract_message_type(
            extended_header_message_info_int
        )
        self.message_type_info = self.__extract_message_type_info(
            extended_header_message_info_int
        )

    @staticmethod
    def __extract_verbose(extended_header_message_info_int):
        return isKthBitSet(extended_header_message_info_int, 0)

    @staticmethod
    def __extract_message_type(extended_header_message_info_int):
        return extended_header_message_info_int & 0b00001110

    @staticmethod
    def __extract_message_type_info(extended_header_message_info_int):
        return extended_header_message_info_int & 0b11110000
