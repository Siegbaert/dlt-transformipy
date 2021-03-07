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
from dlt_transformipy import logger

from dlt_transformipy.core.model.dlt_message import DLTMessage

# BLOCK SIZE USED FOR READING DLT
READ_DLT_BLOCK_SIZE = 32000

### STORAGE FILE IDENTIFIERS ###
STORAGE_FILE_HEADER_BYTE_SIZE = 4
DLT_STORAGE_HEADER_IDENTIFIER_HEX = "444c5401"


class DLTFile():
    is_storaged_file = False

    __dlt_messages = None
    __dlt_file_path = None

    def __init__(self, dlt_file_path):
        self.__dlt_messages = list()
        self.__dlt_file_path = dlt_file_path

    def get_messages(self) -> "list(DLTMessage)":
        """Get a list of all DLTMessages (reads in the whole DLT file at once --> tough on memory)
        :returns: List of all DLTMessages
        :rtype: DLTMessage
        """
        if self.__dlt_messages is None or not len(self.__dlt_messages):
            dlt_file_descriptor = open(self.__dlt_file_path, "rb")
            self.is_storaged_file = self._check_if_storage_file(dlt_file_descriptor)
            self._create_dlt_messages(dlt_file_descriptor)
            dlt_file_descriptor.close()
            logger.info(
                "Number of DLT-Messages in DLT File {}: {}".format(
                    self.__dlt_file_path, len(self.__dlt_messages)
                )
            )
        return self.__dlt_messages

    def clean_up(self):
        self.__dlt_messages = None

    def _check_if_storage_file(self, dlt_file_descriptor):
        # Read the first few bytes of the file and check if it starts with STORAGE_HEADER_DLT_PATTERN (DLT\x01)
        file_start_pattern_hex = dlt_file_descriptor.read(
            STORAGE_FILE_HEADER_BYTE_SIZE
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