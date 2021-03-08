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
from dlt_transformipy.core.model.storage_header import StorageHeader
from dlt_transformipy.core.model.standard_header import StandardHeader
from dlt_transformipy.core.model.extended_header import ExtendedHeader
from dlt_transformipy.core.model.payload import Payload


class DLTMessage:
    storage_header = None
    standard_header = None
    extended_header = None
    payload = None

    def __init__(self, dlt_message_hex, is_storaged_file):
        # Always points to the starting byte of the next info to read from dlt_message_hex
        start_byte_pointer = 0
        # Read the storage-header, if applicable
        if is_storaged_file:
            self.storage_header = StorageHeader(dlt_message_hex, start_byte_pointer)
            # Update the start byte pointer (move it to the end of STORAGE_HEADER)
            start_byte_pointer += self.storage_header.get_byte_size() * 2

        # Read the standard-header
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
