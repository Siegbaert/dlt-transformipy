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
from dlt_transformipy.core.model.dlt_file import DLTFile


def load(file_path):
    """Load the file_path as a DLT File
    :param str file_path: Absolute Path + Filename of the DLT file to load
    :returns: A DLTFile object
    :rtype: DLTFile object
    """
    dlt_file = DLTFile(file_path)
    return dlt_file