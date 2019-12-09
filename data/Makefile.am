KOLIBRI_USER = kolibri
KOLIBRI_USER_HOME = $(sharedstatedir)/lib/kolibri
KOLIBRI_DATA_HOME = $(KOLIBRI_USER_HOME)/data

%: %.in Makefile
	$(AM_V_GEN) m4 \
	    -D__bindir__=$(bindir) \
		-D__KOLIBRI_USER__=$(KOLIBRI_USER) \
		-D__KOLIBRI_USER_HOME__=$(KOLIBRI_USER_HOME) \
		-D__KOLIBRI_DATA_HOME__=$(KOLIBRI_DATA_HOME) \
		-D__KOLIBRI_PORT__=$(KOLIBRI_PORT) \
		$< > $@

# systemd files for socket activated service
systemdsystemunit_DATA = \
	system/eos-kolibri-system-helper.service \
	system/eos-kolibri-system-helper.socket \
	$(NULL)

# systemd tmpfiles.d
tmpfilesdir = $(prefix)/lib/tmpfiles.d
tmpfiles_DATA = tmpfiles.d/eos-kolibri-system-helper.conf

# systemd environment.d
environmentdir = $(prefix)/lib/environment.d
environment_DATA = environment.d/00-eos-kolibri.conf

# systemd sysusers.d
sysusersdir = $(prefix)/lib/sysusers.d
sysusers_DATA = sysusers.d/kolibri.conf

EXTRA_DIST = \
	system/eos-kolibri-system-helper.service \
	system/eos-kolibri-system-helper.socket \
	tmpfiles.d/eos-kolibri-system-helper.conf \
	environment.d/00-eos-kolibri.conf \
	sysusers.d/kolibri.conf \
	$(NULL)

CLEANFILES = \
	system/eos-kolibri-system-helper.service \
	system/eos-kolibri-system-helper.socket \
	tmpfiles.d/eos-kolibri-system-helper.conf \
	environment.d/00-eos-kolibri.conf \
	sysusers.d/kolibri.conf \
	$(NULL)
