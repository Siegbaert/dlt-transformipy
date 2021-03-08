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
from dlt_transformipy.core.model.dlt_file import DLTFile
from dlt_transformipy.core.transform import transform_csv


def load(file_path):
    """Load the file_path as a DLT File

    :param str file_path: Absolute Path + Filename of the DLT file to load
    :returns: A DLTFile object
    :rtype: DLTFile object
    """
    dlt_file = DLTFile(file_path)
    return dlt_file


def as_csv(dlt_file, output_file_path, separator=None):
    """Transforms the given DLTFile to a CSV file and writes the result to the specified output path

    :param DLTFile dlt_file: DLTFIle which shall be transformed
    :param str output_file_path: Absolute Path + Filename of the CSV file to write
    :param str separator: Optional separator used in CSV file (default: ';')
    """
    transform_csv.transform(dlt_file, output_file_path, separator)