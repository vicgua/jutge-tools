Jutge Tools
===========
This package downloads, compiles and tests [Jutge](https://jutge.org/)
problems written in C++.

Available commands can be viewed with: `jutge-tools -h`:

`download`
----------

Download an exercise:
```console
$ tree
.

0 directories, 0 files

$ jutge-tools dl P12509_en
Downloading https://jutge.org/problems/P12509_en/zip
Removing zip file
Creating stub files

$ tree
.
└── P12509_en
    ├── P12509.cc
    ├── problem.pdf
    ├── sample.cor
    └── sample.inp

1 directory, 4 files
```

`compile`
---------

Compile (but do not test) an exercise:
```console
$ jutge-tools c
Compiling...
Compiled successfully
```

`test`
------

Test the exercise:
```console
Compiling...
Compiled successfully
sample failed
```
A diff will be shown by default with `diff -y`, but other commands may be used
(e.g.: `jutge-tools t -d 'kompare $output $correct'`)

Install
=======

To install use `pip` (depending on your setup, this may require
root permissions):
```console
# pip install https://github.com/vicgua/jutge-tools/archive/master.zip
Collecting https://github.com/vicgua/jutge-tools/archive/master.zip
  Downloading https://github.com/vicgua/jutge-tools/archive/master.zip
Installing collected packages: jutge-tools
  Running setup.py install for jutge-tools ... done
Successfully installed jutge-tools-1.0
```

On most systems, you can get root permissions with:
```console
$ sudo -H pip install https://github.com/vicgua/jutge-tools/archive/master.zip
[sudo] password for user:
...
```

To uninstall:
```console
# pip uninstall jutge-tools
Uninstalling jutge-tools-1.0:
  .../bin/jutge-tools
  .../lib/python3.5/site-packages/JutgeTools/__init__.py
  .../lib/python3.5/site-packages/JutgeTools/__pycache__/__init__.cpython-35.pyc
  .../lib/python3.5/site-packages/JutgeTools/__pycache__/cli.cpython-35.pyc
  .../lib/python3.5/site-packages/JutgeTools/__pycache__/compile.cpython-35.pyc
  .../lib/python3.5/site-packages/JutgeTools/__pycache__/download.cpython-35.pyc
  .../lib/python3.5/site-packages/JutgeTools/__pycache__/errors.cpython-35.pyc
  .../lib/python3.5/site-packages/JutgeTools/__pycache__/test.cpython-35.pyc
  .../lib/python3.5/site-packages/JutgeTools/cli.py
  .../lib/python3.5/site-packages/JutgeTools/compile.py
  .../lib/python3.5/site-packages/JutgeTools/download.py
  .../lib/python3.5/site-packages/JutgeTools/errors.py
  .../lib/python3.5/site-packages/JutgeTools/test.py
  .../lib/python3.5/site-packages/jutge_tools-1.0-py3.5.egg-info
Proceed (y/n)? y
  Successfully uninstalled jutge-tools-1.0
```