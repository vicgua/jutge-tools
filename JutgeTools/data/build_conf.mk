# This file contains the configuration for building the program and,
# optionally, the tar archive to be sent.

# PROGRAMNAME: Name of the produced executable
PROGRAMNAME = program

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

OBJECTS = {default_objects}

# TARNAME: Name of the produced tar. Should end with a .tar
# FORBIDDEN VALUES: "tar"
TARNAME = program.tar

# TARFILES: Files to be added to the tar archive
TARFILES = {default_tarfiles}
