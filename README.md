# openrecon-template

This repo is a template made to help building OpenRecon apps.

The puropose is to build the `i2i` demo provided by Siemens for the SDK on https://www.magnetom.net, using a single build script, without any modification.

For later developments, the first step of a new OpenRecon project it to create a new repo based on this `openrecon-template`, then modify the `build.py` internal variables to the needs.


# Requirement

 A Python environment manager is strongly recomanded.

- Python
    - `python 3.10` minimum : 100% sure  
    OR
    - `python 3.12` : don't know
- Additional (non-builtin) modules
    - `jsonschema` : a simple `pip install jsonschema` should work
- Files from Siemens that have to placed in _from_siemens_ subdir
    - `OpenReconSchema_1.1.0.json`
    - `i2i.py`
    - `i2i_json_ui.json`


# Build
Simply run the `build.py` script :
```bash
python build.py
```
The script is quite verbose, helping troubleshooting at each step of the process in case of error.


# Outputs
All output files will be placed in a _build_ subdir.
The finale file, ready for the upload on the magnet will be the _.zip_ file.

