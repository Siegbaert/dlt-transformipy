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
csv_file_path = "tests/example_files/testfile_new.csv"


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)


def test_csv():
    dlt_file = dlt_transformipy.load(dlt_test_file_path)
    assert (
        dlt_file is not None
    ), "dlt_file is None --> DLT File could not be loaded properly!"
    dlt_file.as_csv(csv_file_path)
    assert os.path.exists(csv_file_path) == 1, "testfile.csv does not exist!"
