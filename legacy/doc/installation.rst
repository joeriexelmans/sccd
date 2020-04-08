Installation
============
This section describes the necessary steps for installing SCCD.

Download
--------
The current version of SCCD is v0.9. You can download it using this link: https://msdl.uantwerpen.be/git/simon/SCCD/archive/v0.9.zip

Unzip the contents of the archive to a folder of your choice.

Dependencies
------------
SCCD depends on Python 2.7, which you can download from https://www.python.org/download/releases/2.7/

SCCD Installation
--------------------
Execute the following command inside the *src* folder::

    python setup.py install --user
    
Afterwards, SCCD should be installed. This can easily be checked with the command::

    python -c "import sccd"
    
If this returns without errors, SCCD is sucessfully installed.