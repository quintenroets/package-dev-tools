config/template-Makefile:
<<<<<<< HEAD
	mkdir -p config
	curl https://raw.githubusercontent.com/quintenroets/package-dev-tools/refs/heads/main/config/template-Makefile -o config/template-Makefile
=======
	curl https://raw.githubusercontent.com/quintenroets/package-dev-tools/refs/heads/main/config/template-Makefile --create-dirs -o config/template-Makefile
>>>>>>> template

include config/template-Makefile
