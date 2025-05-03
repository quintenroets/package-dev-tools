<<<<<<< HEAD
.SILENT:

define run
unset VIRTUAL_ENV && uv run
endef

.venv/bin/python:
	command -v uv >/dev/null 2>&1 || (curl -LsSf https://astral.sh/uv/install.sh | sh)
	uv sync --dev --all-extras

.pre-commit-config.yaml: .pre-commit-seed.yaml
	$(run) export-pre-commit-config

pre-commit: .venv/bin/python .pre-commit-config.yaml
	$(run) pre-commit run --show-diff-on-failure --color=always --all-files

test: .venv/bin/python
	$(run) pytest
=======
template-Makefile:
	curl https://raw.githubusercontent.com/quintenroets/package-dev-tools/refs/heads/main/template-Makefile -o template-Makefile

include template-Makefile
>>>>>>> template
