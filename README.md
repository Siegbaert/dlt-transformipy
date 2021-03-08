# dlt-transformipy [![license](https://img.shields.io/badge/license-MIT-green.svg?style=flat)](https://raw.githubusercontent.com/Siegbaert/dlt-transformipy/main/LICENSE)


dlt-transformipy is a pure python implementation which features the transformation of Storaged DLT files (see: [Diagnostic, Log and Trace Protocol Specification v1.0](https://www.autosar.org/fileadmin/user_upload/standards/foundation/1-0/AUTOSAR_PRS_DiagnosticLogAndTraceProtocol.pdf)) into other formats (e.g. CSV).


## Getting Started

### Set-Up python virual environment
```sh
make setup
```

### Activate python virtual environment
```sh
.venv/bin/activate
```

### Install dependencies
```sh
make install
```

## Usage
To read a storaged DLT File and transform it to CSV:
```python
from dlt_transformipy import dlt_transformipy
dlt_file = dlt_transformipy.load("sample.dlt")
dlt_transformipy.as_csv(dlt_file, "sample-output.csv")
```

dlt-transformipy can also be used to simply read the DLTFile and iterate over every DLTMessage (e.g. for creating custom analysis tools based on DLT):
```python
from dlt_transformipy import dlt_transformipy
dlt_file = dlt_transformipy.load("sample.dlt")
for message in dlt_file.get_messages():
    # Enter custom code here
    pass     
```

### Supported Payload Data Types
- [x] RAWD
- [x] STRG
- [x] UINT (max 64 Bit)
- [x] SINT (max 64 Bit)
- [ ] BOOL
- [ ] FLOA
- [ ] ARAY
- [ ] FIXP
- [ ] TRAI
- [ ] STRU
- [ ] VARI
- [ ] SCOD

### Backlog
- [ ] Full DLT specification support (Non-Verbose messages, all specified payload data types, ...)
- [ ] Transform to JSON
- [ ] Offer a non-bulk reading option to iterate over every DLT message without loading the whole DLT file at once
- [ ] DLT Filters
- [ ] Performance improvements