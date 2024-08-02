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


# App

## Objective : templatization & seperation of environements

The `app` dir will contained the versionned code.  
The `python-ismrmrd-server` dir is **NOT** versionned.  
To _add_ your app files files in the `python-ismrmrd-server`, create symbolic links.

## Howto

Open a Terminal in the repository directory, then :

```bash
# setup Conda environnement
conda create --name openrecon-template
conda activate openrecon-template
conda install python=3.12
conda install ipython
pip install ismrmrd
pip install pydicom
pip install pynetdicom

# create .py file symbolic link in `python-ismrmrd-server`
# this is how the MRD client/server will behave : all files/modules in the same dir
cd python-ismrmrd-server
ln -s ../app/i2i-save-original-images.py .
```
Repeat the `ln -s` for the files you need.


## Test locally the app

!!! TO DO !!!  
some scripts that uses the images provided by in SDK...  
server.py -> VSCode (for debugging)  
client.py -> in terminal to start "sending" data to the server  
!!! TO DO !!!  

## Build

!!! TO DO !!!
