config/template-Makefile:
	mkdir -p config
	curl https://raw.githubusercontent.com/quintenroets/package-dev-tools/refs/heads/main/config/template-Makefile -o config/template-Makefile

include config/template-Makefile
