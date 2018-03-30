include build_conf.mk

# If your version of GNU tar is not named "tar", use "make TAR=gtar" (for
# example). Other versions such as BSD tar may also work, though.
TAR = tar

# Internal variables to simplify the Makefile
DEPS.cc = $(CXX) $(CXXFLAGS) $(CPPFLAGS) $(TARGET_ARCH)
DEPS.c = $(CC) $(CFLAGS) $(CPPFLAGS) $(TARGET_ARCH)

built_objs := .build/built_objs
sort_bo = sort -u $(built_objs) -o $(built_objs)
addobject = echo $(1) >> $(built_objs) && $(sort_bo)

.PHONY: all
all: $(PROGRAMNAME) $(TARNAME)

.PHONY: clean
clean:
	@# The `cat` is not the safest option, but is the easiest and most
	@# portable. Since this will run in YOUR system, you are responsible
	@# for having sanely named object files and not messing with
	@# .build/built_objs
	@[ -f $(built_objs) ] && rm -v -- `cat $(built_objs)` || true
	@rm -rvf .build/*
	@[ -d .build ] && rmdir -v .build || true

.PHONY: exe
exe: $(PROGRAMNAME)

.PHONY: tar
tar: $(TARFILES)

%.o: %.cc
	@mkdir -pv .build
	$(DEPS.cc) -MM -MF .build/$@.d $<
	$(COMPILE.cc) -o $@ $<
	@$(call addobject,$@)

%.o: %.c
	@mkdir -pv .build
	$(DEPS.c) -MM -MF .build/$@.d $<
	$(COMPILE.c) -o $@ $<
	@$(call addobject,$@)

$(PROGRAMNAME): $(OBJECTS)
	@mkdir -pv .build
	$(LINK.cc)   -o $@ $^
	@$(call addobject,$@)

$(TARNAME): $(TARFILES)
	@mkdir -pv .build
	$(TAR) $(TARFLAGS) rf $@ $?
	@$(call addobject,$@)

-include .build/*.d
