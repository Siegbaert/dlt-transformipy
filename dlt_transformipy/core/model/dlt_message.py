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
