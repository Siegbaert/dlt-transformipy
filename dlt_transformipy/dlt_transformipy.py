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
import datetime

from dlt_transformipy.core.model.storage_header import StorageHeader
from dlt_transformipy.core.model.standard_header import StandardHeader
from dlt_transformipy.core.model.extended_header import ExtendedHeader
from dlt_transformipy.core.model.payload import Payload

logger = logging.getLogger("dlt-transformipy")
logger.setLevel(logging.INFO)

# BLOCK SIZE USED FOR READING DLT
READ_DLT_BLOCK_SIZE = 32000

### STORAGE HEADER ###
DLT_STORAGE_HEADER_IDENTIFIER_HEX = "444c5401"


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
        # TODO: Move to a helper method?!
        # Read the first few bytes of the file and check if it starts with STORAGE_HEADER_DLT_PATTERN (DLT\x01)
        # file_start_pattern_hex = dlt_file_descriptor.read(
        #    STORAGE_HEADER_DLT_PATTERN_BYTE_SIZE
        # ).hex()
        # Reset the read-pointer
        # dlt_file_descriptor.seek(0)
        return True  # file_start_pattern_hex == DLT_STORAGE_HEADER_IDENTIFIER_HEX

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

    def __init__(self, dlt_message_hex, is_storaged_file):
        # Always points to the starting byte of the next info to read from dlt_message_hex
        start_byte_pointer = 0
        logger.info("StartBytePointer: {}".format(start_byte_pointer))
        # Read the storage-header, if applicable
        if is_storaged_file:
            logger.info("Reading StorageHeader")
            self.storage_header = StorageHeader(dlt_message_hex, start_byte_pointer)
            # Update the start byte pointer (move it to the end of STORAGE_HEADER)
            start_byte_pointer += self.storage_header.get_byte_size() * 2

        logger.info("StartBytePointer: {}".format(start_byte_pointer))
        # Read the standard-header
        logger.info("Reading StandardHeader")
        self.standard_header = StandardHeader(dlt_message_hex, start_byte_pointer)
        # Update the start byte pointer (move it to the end of STANDARD_HEADER)
        start_byte_pointer += self.standard_header.get_byte_size() * 2

        # Check if extended-header is used
        if self.standard_header.header_type.use_extended_header:
            self.extended_header = ExtendedHeader(dlt_message_hex, start_byte_pointer)
            # Update the start byte pointer (move it to the end of EXTENDED_HEADER)
            start_byte_pointer += self.extended_header.get_byte_size() * 2

        # Create the payload
        self.payload = Payload(dlt_message_hex, start_byte_pointer, self)


def load(file):
    """Load the DLT File and read all DLT messages
    :param str file: Absolute Path + Filename of the DLT file to load
    :returns: A DLTFile object
    :rtype: DLTFile object
    """
    dlt_file = DLTFile(file)
    return dlt_file