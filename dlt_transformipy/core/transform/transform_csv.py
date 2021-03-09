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
import datetime


def transform(dlt_file, output_file_path, separator=None):
    if separator is None:
        separator = ";"

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
            csv_line_result.append(str(message.storage_header.ecu_id))
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
