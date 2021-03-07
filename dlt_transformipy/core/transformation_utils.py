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
import datetime


def as_csv(dlt_file, output_file_path, separator=";"):
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
        for message in dlt_file.get_messages():
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
                if dlt_file.is_storaged_file
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
