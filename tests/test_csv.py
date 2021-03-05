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
import dlt_transformipy
import os
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
    assert (
        dlt_file is not None
    ), "dlt_file is None --> DLT File could not be loaded properly!"
    dlt_file.as_csv(csv_output_file_path)
    assert os.path.exists(csv_output_file_path) == 1, "testfile.csv does not exist!"
