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
"""Python implementation for DLT"""
import logging
import datetime

from dlt_transformipy.helpers import (
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

logger = logging.getLogger("dlt-transformipy")

# BLOCK SIZE USED FOR READING DLT
READ_DLT_BLOCK_SIZE = 32000

### STORAGE HEADER ###
DLT_STORAGE_HEADER_IDENTIFIER_HEX = "444c5401"

# STORAGE HEADER BYTE SIZES
STORAGE_HEADER_DLT_PATTERN_BYTE_SIZE = 4
STORAGE_HEADER_TIMESTAMP_BYTE_SIZE = 8
STORAGE_HEADER_ECU_ID_BYTE_SIZE = 4
# TODO: Currently DLT_PATTERN SIZE because it is filtered automatically for every message --> do not filter below (see hex_dlt_message_iterator) and then add the size here as well
STORAGE_HEADER_BYTE_SIZE = (
    STORAGE_HEADER_TIMESTAMP_BYTE_SIZE + STORAGE_HEADER_ECU_ID_BYTE_SIZE
)

### STANDARD HEADER ###
# STANDARD HEADER BYTE SIZES
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

### EXTENDED HEADER ###
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

### PAYLOAD ###
# TYPE INFO #
PAYLOAD_TYPE_INFO_BYTE_SIZE = 4
PAYLOAD_RAWD_LENGTH_BYTE_SIZE = 2
PAYLOAD_STRG_LENGTH_BYTE_SIZE = 2
TYPE_INFO_BYTE_SIZE_HEX = PAYLOAD_TYPE_INFO_BYTE_SIZE * 2
RAWD_LENGTH_HEX = PAYLOAD_RAWD_LENGTH_BYTE_SIZE * 2
STRG_LENGTH_HEX = PAYLOAD_STRG_LENGTH_BYTE_SIZE * 2
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


class DLTFile(object):
    __dlt_messages = None
    is_storaged_file = False

    def __init__(self, dlt_file_path):
        self.__dlt_messages = list()
        dlt_file_descriptor = open(dlt_file_path, "rb")
        self.is_storaged_file = self._check_if_storage_file(dlt_file_descriptor)
        self._create_dlt_messages(dlt_file_descriptor)
        dlt_file_descriptor.close()
        logger.debug("Number of DLT-Messages: {}".format(len(self.__dlt_messages)))

    def get_messages(self) -> "list(DLTMessage)":
        """Get a list of all DLTMessages | Reads in complete file --> tough on memory
        :returns: List of all DLTMessages
        :rtype: DLTMessage
        """
        return self.__dlt_messages

    def clean_up(self):
        self.__dlt_messages = None

    def as_csv(self, output_file_path, separator=";"):
        with open(output_file_path, "w", encoding="utf8") as f:
            message_idx = 0
            # Write header
            f.write(
                separator.join(
                    [
                        '"Index"',
                        '"DateTime"',
                        '"Timestamp"',
                        '"Count"',
                        '"Ecuid"',
                        '"Apid"',
                        '"Ctid"',
                        '"SessionId"',
                        '"Mode"',
                        '"#Args"',
                        '"Payload"',
                    ]
                )
            )
            f.write("\n")

            # Write contents
            for message in self.get_messages():
                has_extended_header = (
                    message.standard_header.header_type.use_extended_header
                )
                csv_line_result = list()
                # idx
                csv_line_result.append(str(message_idx))
                # dateTime
                csv_line_result.append(
                    datetime.datetime.utcfromtimestamp(
                        message.storage_header.timestamp_seconds
                    ).isoformat()
                    + "Z"
                )
                # timeSinceStartup
                csv_line_result.append(
                    str(message.standard_header.timestamp)
                    if message.standard_header.header_type.with_timestamp
                    else ""
                )
                # mcnt
                csv_line_result.append(str(message.standard_header.message_counter))
                # ecuId
                csv_line_result.append(
                    str(message.storage_header.ecu_id)
                    if self.is_storaged_file
                    else str(message.standard_header.ecu_id)
                )
                # apid
                csv_line_result.append(
                    str(message.extended_header.apid) if has_extended_header else ""
                )
                # ctid
                csv_line_result.append(
                    str(message.extended_header.ctid) if has_extended_header else ""
                )
                # sid
                csv_line_result.append(str(message.standard_header.session_id))
                # mode
                csv_line_result.append(
                    str(
                        "verbose"
                        if message.extended_header.message_info.verbose
                        else "non-verbose"
                    )
                    if has_extended_header
                    else ""
                )
                # args
                csv_line_result.append(
                    str(message.extended_header.noar if has_extended_header else "")
                )
                # payload
                payload_result = list()
                for msg_payload_arg in message.payload:
                    payload_result.append(str(msg_payload_arg))
                csv_line_result.append(
                    " ".join(payload_result)
                    .replace('"', '""')
                    .replace("\n", "")
                    .replace("\r", "")
                    .replace("\0", "")
                )

                # Write the line to the output file
                f.write(separator.join('"' + item + '"' for item in csv_line_result))
                f.write("\n")

                message_idx += 1

    def _check_if_storage_file(self, dlt_file_descriptor):
        # Read the first few bytes of the file and check if it starts with SOTRAGE_HEADER_DLT_PATTERN (DLT\x01)
        file_start_pattern_hex = dlt_file_descriptor.read(
            STORAGE_HEADER_DLT_PATTERN_BYTE_SIZE
        ).hex()
        # Reset the read-pointer
        dlt_file_descriptor.seek(0)
        return file_start_pattern_hex == DLT_STORAGE_HEADER_IDENTIFIER_HEX

    def _create_dlt_messages(self, dlt_file_descriptor):
        for dlt_message_hex in self._hex_dlt_message_iterator(dlt_file_descriptor):
            if dlt_message_hex and len(dlt_message_hex) > 0:
                self.__dlt_messages.append(
                    DLTMessage(dlt_message_hex, self.is_storaged_file)
                )

    def _hex_dlt_message_iterator(
        self,
        dlt_file_descriptor,
        message_begin_marker=DLT_STORAGE_HEADER_IDENTIFIER_HEX,
        block_size=READ_DLT_BLOCK_SIZE,
    ):
        current = ""
        while True:
            hex_block = dlt_file_descriptor.read(block_size).hex()
            if not hex_block:  # end-of-file
                yield current
                return
            current += hex_block
            while True:
                markerpos = current.find(message_begin_marker)
                if markerpos < 0:
                    break
                yield current[:markerpos]
                current = current[markerpos + len(message_begin_marker) :]


class DLTMessage(object):
    storage_header = None
    standard_header = None
    extended_header = None
    payload = None

    # helper info
    noar = 0

    def __init__(self, dlt_message_hex, is_storaged_file):
        # Read the storage-header if necessary
        if is_storaged_file:
            # Extract storage header from the message
            storage_header_hex = dlt_message_hex[: STORAGE_HEADER_BYTE_SIZE * 2]
            self.storage_header = StorageHeader(storage_header_hex)
            # 'Consume' the storage header of the message
            dlt_message_hex = dlt_message_hex[STORAGE_HEADER_BYTE_SIZE * 2 :]

        standard_header_hex = dlt_message_hex[: STANDARD_HEADER_BYTE_SIZE * 2]
        self.standard_header = StandardHeader(standard_header_hex)

        # Calculate standard header's dynamic byte size
        standard_header_dynamic_byte_size = STANDARD_HEADER_BYTE_SIZE

        if not self.standard_header.header_type.with_ecu_id:
            standard_header_dynamic_byte_size -= STANDARD_HEADER_ECU_ID_BYTE_SIZE

        if not self.standard_header.header_type.with_session_id:
            standard_header_dynamic_byte_size -= STANDARD_HEADER_SESSION_ID_BYTE_SIZE

        if not self.standard_header.header_type.with_timestamp:
            standard_header_dynamic_byte_size -= STANDARD_HEADER_TIMESTAMP_BYTE_SIZE

        # 'Consume' the standard header of the message
        dlt_message_hex = dlt_message_hex[standard_header_dynamic_byte_size * 2 :]

        # Check if extended-header is used
        if self.standard_header.header_type.use_extended_header:
            self.extended_header = ExtendedHeader(dlt_message_hex)
            self.noar = self.extended_header.noar
            # 'Consume' the extended header of the message
            dlt_message_hex = dlt_message_hex[EXTENDED_HEADER_BYTE_SIZE * 2 :]

        # Create the payload
        self.payload = Payload(dlt_message_hex, self)


class StorageHeader(object):
    timestamp_seconds = 0
    timestamp_microseconds = 0
    ecu_id = None

    def __init__(self, storage_header_hex):
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


class StandardHeader(object):
    header_type = None
    message_counter = 0
    length = 0
    ecu_id = None
    session_id = None
    timestamp = None

    def __init__(self, standard_header_hex):
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


class StandardHeaderType(object):
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


class ExtendedHeader(object):
    message_info = None
    noar = None
    apid = None
    ctid = None

    def __init__(self, extended_header_hex):
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

    def __extract_application_id(self, extended_header_hex):
        return hex_str_to_utf8(extended_header_hex[4:12], errors="ignore").rstrip("\0")

    def __extract_context_id(self, extended_header_hex):
        return hex_str_to_utf8(extended_header_hex[12:20], errors="ignore").rstrip("\0")


class ExtendedHeaderMessageInfo(object):
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

    def __extract_verbose(self, extended_header_message_info_int):
        return isKthBitSet(extended_header_message_info_int, 0)

    def __extract_message_type(self, extended_header_message_info_int):
        return extended_header_message_info_int & 0b00001110

    def __extract_message_type_info(self, extended_header_message_info_int):
        return extended_header_message_info_int & 0b11110000


class Payload(object):
    # List like access to arguments

    _payload_encoded = None
    _arguments = None
    _decodable = False  # only verbose-mode is supported at the moment
    _big_endian = False
    _noar = 0
    _index = 0

    def __init__(self, payload_hex, message):
        self._payload_encoded = payload_hex
        self._noar = message.noar
        self._big_endian = (
            message.standard_header.header_type.most_significant_byte_first
        )
        if message.standard_header.header_type.use_extended_header:
            self._decodable = message.extended_header.message_info.verbose
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

                    # Check if VARI is set --> Not yet supported!
                    if type_info_int & TYPE_INFO_VARI_BITMASK:
                        self._arguments.append("[VARI is not supported yet]")
                        logger.debug(
                            "VARI is not supported yet! Skipping this payload."
                        )
                        break

                    if type_info_int & TYPE_INFO_RAW_BITMASK:  # Check if RAW
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
                    elif type_info_int & TYPE_INFO_STRG_BITMASK:  # Check if STRING

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
                    elif type_info_int & TYPE_INFO_UINT_BITMASK:  # Check if UINT
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
                    elif type_info_int & TYPE_INFO_SINT_BITMASK:  # Check if SINT
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


def load(file):
    """Load the DLT File and read all DLT messages
    :param str file: Absolute Path + Filename of the DLT file to load
    :returns: A DLTFile object
    :rtype: DLTFile object
    """
    dlt_file = DLTFile(file)
    return dlt_file