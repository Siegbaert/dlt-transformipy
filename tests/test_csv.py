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
import os
import time
from dlt_transformipy import dlt_transformipy

dlt_test_file_path = "tests/example_files/testfile.dlt"
test_output_file_path = "tests/output"
csv_output_file_path = "tests/output/testfile.csv"


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    if not os.path.exists(test_output_file_path):
        os.makedirs(test_output_file_path)
    elif os.path.exists(csv_output_file_path):
        os.remove(csv_output_file_path)


def test_csv():
    dlt_file = dlt_transformipy.load(dlt_test_file_path)
    dlt_file.read()
    assert (
        len(dlt_file.get_messages()) > 0
    ), "DLTMessage size is 0 --> DLT messages could not be read properly!"
    dlt_transformipy.as_csv(dlt_file, csv_output_file_path)
    assert os.path.exists(csv_output_file_path) == 1, "{} does not exist!".format(
        csv_output_file_path
    )
