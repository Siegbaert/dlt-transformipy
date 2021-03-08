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
PAYLOAD_TYPE_INFO_BYTE_SIZE = 4
PAYLOAD_RAWD_LENGTH_BYTE_SIZE = 2
PAYLOAD_STRG_LENGTH_BYTE_SIZE = 2
TYPE_INFO_BYTE_SIZE_HEX = PAYLOAD_TYPE_INFO_BYTE_SIZE * 2
RAWD_LENGTH_HEX = PAYLOAD_RAWD_LENGTH_BYTE_SIZE * 2
STRG_LENGTH_HEX = PAYLOAD_STRG_LENGTH_BYTE_SIZE * 2
# BITMASKS
TYPE_INFO_TYLE_BITMASK = 0b1111
TYPE_INFO_TYLE_8BIT_BITMASK = 0b1
TYPE_INFO_TYLE_16BIT_BITMASK = 0b10
TYPE_INFO_TYLE_32BIT_BITMASK = 0b11
TYPE_INFO_TYLE_64BIT_BITMASK = 0b100
TYPE_INFO_TYLE_128BIT_BITMASK = 0b101
TYPE_INFO_BOOL_BITMASK = 0b10000
TYPE_INFO_SINT_BITMASK = 0b100000
TYPE_INFO_UINT_BITMASK = 0b1000000
TYPE_INFO_FLOAT_BITMASK = 0b10000000
TYPE_INFO_ARRAY_BITMASK = 0b100000000
TYPE_INFO_STRG_BITMASK = 0b1000000000
TYPE_INFO_RAW_BITMASK = 0b10000000000
TYPE_INFO_VARI_BITMASK = 0b100000000000
TYPE_INFO_FIXP_BITMASK = 0b1000000000000
TYPE_INFO_TRAI_BITMASK = 0b10000000000000
TYPE_INFO_STRU_BITMASK = 0b100000000000000
TYPE_INFO_SCOD_BITMASK = 0b111000000000000000
TYPE_INFO_SCOD_ASCII_BITMASK = 0b000
TYPE_INFO_SCOD_UTF8_BITMASK = 0b001


class Payload:
    # List like access to arguments

    _payload_encoded = None
    _arguments = None
    _decodable = False  # only verbose-mode is supported at the moment
    _big_endian = False
    _noar = 0
    _index = 0

    def __init__(self, dlt_message_hex, start_byte_pointer, message):
        self._payload_encoded = dlt_message_hex[start_byte_pointer:]
        self._noar = (
            message.extended_header.noar
            if message.standard_header.header_type.use_extended_header
            else 0
        )
        self._big_endian = (
            message.standard_header.header_type.most_significant_byte_first
        )
        if message.standard_header.header_type.use_extended_header:
            self._decodable = message.extended_header.message_info.verbose
            if not self._decodable:
                logger.debug(
                    "Payload of message '{}' is not decodeable yet.".format(
                        dlt_message_hex
                    )
                )
        self._index = 0

    def __getitem__(self, index):
        """Accessing the payload item as a list"""
        if index < 0 or index > self._noar:
            return IndexError()

        # Check if already parsed
        if self._arguments is None:
            self._parse_payload()

        return self._arguments[index]

    def __len__(self):
        """Return number of arguments"""
        if self._arguments is None:
            self._parse_payload()

        return len(self._arguments)

    def __iter__(self):
        """ Returns the Iterator object """
        self._parse_payload()
        return self

    def __next__(self):
        """'Returns the argument """
        if self._index < len(self._arguments):
            result = self.__getitem__(self._index)
            self._index += 1
            return result
        # Reset iterator
        self._index = 0
        # End of Iteration
        raise StopIteration

    def _parse_payload(self):
        """Parse the payload into list of arguments"""
        if self._arguments is None:
            self._arguments = list()
            if self._decodable:
                offset = 0

                for _ in range(self._noar):
                    # Extract TYPE_INFO from Payload
                    type_info_int = hex_str_to_uint32(
                        self._payload_encoded[
                            offset : offset + TYPE_INFO_BYTE_SIZE_HEX
                        ],
                        big_endian=self._big_endian,
                    )

                    # Add size of TYPE_INFO to offset
                    offset += TYPE_INFO_BYTE_SIZE_HEX

                    value = None

                    if (
                        type_info_int & TYPE_INFO_VARI_BITMASK
                    ):  # VARI --> Not yet supported!
                        self._arguments.append("[VARI is not supported yet]")
                        logger.debug(
                            "VARI is not supported yet! Skipping this payload."
                        )
                        break

                    if type_info_int & TYPE_INFO_RAW_BITMASK:  # RAWD
                        # Extract the length of the actual payload (length without TYPE_INFO)
                        raw_length_bytes = (
                            hex_str_to_uint16(
                                self._payload_encoded[
                                    offset : offset + RAWD_LENGTH_HEX
                                ],
                                big_endian=self._big_endian,
                            )
                            * 2
                        )
                        offset += RAWD_LENGTH_HEX
                        # Get the RAWD value from the payload
                        value = self._payload_encoded[
                            offset : offset + raw_length_bytes
                        ]
                        offset += raw_length_bytes
                    elif type_info_int & TYPE_INFO_STRG_BITMASK:  # STRG

                        def get_scod(type_info):
                            """Helper function"""
                            return type_info & TYPE_INFO_SCOD_BITMASK

                        # Extract the length of the actual payload (length without TYPE_INFO)
                        strg_length_bytes = (
                            hex_str_to_uint16(
                                self._payload_encoded[
                                    offset : offset + STRG_LENGTH_HEX
                                ],
                                big_endian=self._big_endian,
                            )
                            * 2
                        )
                        offset += STRG_LENGTH_HEX
                        # Get the STRG value from the payload
                        value = (
                            hex_str_to_ascii(
                                self._payload_encoded[
                                    offset : offset + strg_length_bytes
                                ]
                            )
                            if get_scod(type_info_int) == TYPE_INFO_SCOD_ASCII_BITMASK
                            else hex_str_to_utf8(
                                self._payload_encoded[
                                    offset : offset + strg_length_bytes
                                ]
                            )
                        )  # "-2" to strip the \x00 at the end
                        offset += strg_length_bytes
                    elif type_info_int & TYPE_INFO_UINT_BITMASK:  # UINT
                        tyle = type_info_int & TYPE_INFO_TYLE_BITMASK
                        if tyle == TYPE_INFO_TYLE_8BIT_BITMASK:
                            value = hex_str_to_uint8(
                                self._payload_encoded[offset : offset + 2],
                                big_endian=self._big_endian,
                            )
                            offset += 2
                        if tyle == TYPE_INFO_TYLE_16BIT_BITMASK:
                            value = hex_str_to_uint16(
                                self._payload_encoded[offset : offset + 4],
                                big_endian=self._big_endian,
                            )
                            offset += 4
                        if tyle == TYPE_INFO_TYLE_32BIT_BITMASK:
                            value = hex_str_to_uint32(
                                self._payload_encoded[offset : offset + 8],
                                big_endian=self._big_endian,
                            )
                            offset += 8
                        if tyle == TYPE_INFO_TYLE_64BIT_BITMASK:
                            value = hex_str_to_uint64(
                                self._payload_encoded[offset : offset + 16],
                                big_endian=self._big_endian,
                            )
                            offset += 16
                        if tyle == TYPE_INFO_TYLE_128BIT_BITMASK:
                            raise TypeError("reading 128BIT values not supported")
                    elif type_info_int & TYPE_INFO_SINT_BITMASK:  # SINT
                        tyle = type_info_int & TYPE_INFO_TYLE_BITMASK
                        if tyle == TYPE_INFO_TYLE_8BIT_BITMASK:
                            value = hex_str_to_int8(
                                self._payload_encoded[offset : offset + 2],
                                big_endian=self._big_endian,
                            )
                            offset += 2
                        if tyle == TYPE_INFO_TYLE_16BIT_BITMASK:
                            value = hex_str_to_int16(
                                self._payload_encoded[offset : offset + 4],
                                big_endian=self._big_endian,
                            )
                            offset += 4
                        if tyle == TYPE_INFO_TYLE_32BIT_BITMASK:
                            value = hex_str_to_int32(
                                self._payload_encoded[offset : offset + 8],
                                big_endian=self._big_endian,
                            )
                            offset += 8
                        if tyle == TYPE_INFO_TYLE_64BIT_BITMASK:
                            value = hex_str_to_int64(
                                self._payload_encoded[offset : offset + 16],
                                big_endian=self._big_endian,
                            )
                            offset += 16
                        if tyle == TYPE_INFO_TYLE_128BIT_BITMASK:
                            raise TypeError("reading 128BIT values not supported")
                    else:
                        # Reset the arguments to NONE if parsing could not be done
                        self._arguments.append("[Unsupported type]")
                        logger.debug("Unsupported type {}".format(type_info_int))
                        break

                    # Add the parsed value to list of arguments
                    self._arguments.append(value)
            else:
                # If it's not decodable (non-verbose mode), then the encoded payload should be returned
                self._arguments.append(self._payload_encoded)