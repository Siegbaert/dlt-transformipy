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
