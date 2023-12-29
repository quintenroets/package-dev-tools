# Dev Tools
[![PyPI version](https://badge.fury.io/py/dev-tools.svg)](https://badge.fury.io/py/dev-tools)
## Usage
1) Choose repository name
2) Instantiate new repository from the template repository
3) Enable or disable PyPI publishing
   * Enable
      1) Choose public package name
      2) Configure trusted publisher on [PyPI](https://pypi.org/manage/account/publishing/)
      3) Update public package name
         * pyproject.toml: update `name = ..`
         * README.md:
           * update `pip install ..`
           * remove `pip install git+https://github.com..`
           * update PyPI badge url: 1st url & 2nd url
   * Disable
      1) Update README.md:
           * remove `pip install <package-slug>`
           * remove PyPI badge
4) Configure displayed project information
   * Enable releases
   * Disable deployments and packages
5) Configure settings
   * General > Automatically delete head branches

=============================================================

Run
```shell
dev_tools
```
## Installation
```shell
pip install dev-tools
```
or
```shell
pip install git+https://github.com/quintenroets/dev-tools.git
```
make sure to use Python 3.10+
