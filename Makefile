# Dev checks: compile collectors, validate JSON Schema + fixture, smoke-test live inventory output.
PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

.PHONY: check compile validate-schema validate-collect nix-develop nix-install-all flake-lock flake-check

check: compile validate-schema validate-collect
	@echo "make check: OK"

compile:
	$(PYTHON) -m py_compile agent/mac-nixos-bootstrap/survey.py
	$(PYTHON) -m py_compile agent/mac-nixos-bootstrap/collect-mac-state.py
	$(PYTHON) -m py_compile agent/mac-nixos-bootstrap/validate_inventory.py

validate-schema:
	$(PIP) install -q -r requirements-dev.txt
	$(PYTHON) agent/mac-nixos-bootstrap/validate_inventory.py

# Runs collect-mac-state to a temp dir and validates emitted JSON (cross-platform; fast without brew).
validate-collect: compile
	$(PIP) install -q -r requirements-dev.txt
	@set -e; TMP=$$(mktemp -d); \
	INV=$$($(PYTHON) agent/mac-nixos-bootstrap/collect-mac-state.py -o "$$TMP" --no-md --print-json-path); \
	if [ -z "$$INV" ] || [ ! -f "$$INV" ]; then \
		echo "validate-collect: expected JSON file missing (collect-mac-state did not print --print-json-path)" >&2; \
		exit 1; \
	fi; \
	$(PYTHON) agent/mac-nixos-bootstrap/validate_inventory.py --json "$$INV"

# Nix (umbrella): dev shell + install-all app (requires flake.lock — run `nix flake lock` once).
nix-develop:
	nix develop

nix-install-all:
	nix run .#

flake-lock:
	nix flake lock

flake-check:
	nix flake check
