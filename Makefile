PYTHON ?= python

.PHONY: test smoke validate verify

test:
	$(PYTHON) -m pytest

smoke:
	$(PYTHON) tools/smoke.py

validate:
	$(PYTHON) tools/validate_release.py --write-evidence

verify: test smoke validate
