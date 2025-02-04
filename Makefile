.PHONY: all clean install uninstall depends

.DEFAULT_GOAL := all

PACKAGE := $(shell sed -nr 's/^name = (.*)$$/\1/p' setup.cfg | tr - _)
VERSION := $(shell sed -nr 's/^version = (.*)$$/\1/p' setup.cfg)

WHEEL := dist/$(PACKAGE)-$(VERSION)-py3-none-any.whl

all::
	python3 -m build

clean::
	rm -rf dist/
	rm -rf src/$(PACKAGE).egg-info/

install::
	pip install --no-index $(WHEEL)

uninstall::
	pip uninstall -y $(WHEEL)

reinstall:: uninstall install

depends::
	pip install build nose2 coverage
