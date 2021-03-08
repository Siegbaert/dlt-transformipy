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

from dlt_transformipy.core.model.dlt_message import DLTMessage

# BLOCK SIZE USED FOR READING DLT
READ_DLT_BLOCK_SIZE = 32000

### STORAGE FILE IDENTIFIERS ###
STORAGE_FILE_HEADER_BYTE_SIZE = 4
DLT_STORAGE_HEADER_IDENTIFIER_HEX = "444c5401"


class DLTFile:
    is_storaged_file = False

    __dlt_messages = None
    __dlt_file_path = None

    def __init__(self, dlt_file_path):
        self.__dlt_messages = list()
        self.__dlt_file_path = dlt_file_path

    def read(self):
        """Reads the whole DLTFile into memory"""
        dlt_file_descriptor = open(self.__dlt_file_path, "rb")
        self.is_storaged_file = self._check_if_storage_file(dlt_file_descriptor)
        for dlt_message_hex in self._hex_dlt_message_iterator(dlt_file_descriptor):
            if dlt_message_hex and len(dlt_message_hex) > 0:
                self.__dlt_messages.append(
                    DLTMessage(dlt_message_hex, self.is_storaged_file)
                )
        dlt_file_descriptor.close()
        logger.info(
            "Number of DLT-Messages in DLT File {}: {}".format(
                self.__dlt_file_path, len(self.__dlt_messages)
            )
        )

    def get_messages(self) -> "list(DLTMessage)":
        """Returns a list of all DLTMessages
        :returns: List of all DLTMessages
        :rtype: DLTMessage
        """
        if self.__dlt_messages is None or not len(self.__dlt_messages):
            self.read()
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