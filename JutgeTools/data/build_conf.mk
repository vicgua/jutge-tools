# This file contains the configuration for building the program and,
# optionally, the tar archive to be sent.

# PROGRAMNAME: Name of the produced executable
PROGRAMNAME = ${default_programname}

# OBJECTS: The objects that have to be linked together to form the program.
# For example, if the program consists of a "main.cc", "example.cc",
# "example.hh, you have to write:
# OBJECTS = main.o example.o
# Other files like the "example.hh" will be figured automatically.
# It is important that: 1) they end in .o and 2) for every object, there's
# a .cc or .c file with the same name.
# FORBIDDEN VALUES: all, clean, exe, tar. All other values will be interpreted
# with the usual Make meaning (i.e.: avoid names with * or other strange
# symbols if you don't know what you are doing).
# WARNING: This implies that spaces are not allowed and are likely to
# go wrong. Check the Make manual for other unusual symbols

OBJECTS = ${default_objects}

# TARNAME: Name of the produced tar. Should end with a .tar
# FORBIDDEN VALUES: "tar"
TARNAME = ${default_tarname}

# TARFILES: Files to be added to the tar archive
TARFILES = ${default_tarfiles}

# Advanced settings
# (You usually don't have to touch this)

# BUILD_DIR: Directory where internal build files (such as dependency files
# and a list of built objects) will be kept.
BUILD_DIR := .build

# TARAPPEND: Set to true to append to the tar file when files are updated
# instead of creating a new tar.
# WARNING: When appending to a tar file, the old version of the file is not
# deleted, it is kept in the tar, increasing its size. Also, the Jutge
# might choke on tars with duplicated files, or with more files than it
# expects. Change this if the tar step takes too much time (unlikely for
# Jutge problems).
TARAPPEND := false

# ORDERED_BUILD_OBJECTS: Set to false to simply append created objects
# to the built objects list. Otherwise, the list is guaranted to be sorted
# and with no repeated elements.
# As with TARAPPEND, this setting is only relevant when you have a lot of
# source files (unlikely for Jutge)
ORDERED_BUILD_OBJECTS := true
